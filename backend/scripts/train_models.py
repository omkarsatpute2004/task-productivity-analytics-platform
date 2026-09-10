import sys
import os
import joblib
from datetime import datetime, timezone
import pandas as pd
from sqlalchemy import create_engine, text
from sklearn.model_selection import train_test_split

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.ml.features import extract_ml_dataset, FEATURE_COLUMNS
from app.ml.classification import train_and_evaluate_classifiers
from app.ml.regression import train_and_evaluate_regressors
from app.ml.evaluation import extract_feature_importance

MODEL_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'models'))
os.makedirs(MODEL_DIR, exist_ok=True)

DB_URL = "postgresql+psycopg://postgres@localhost:5432/task_productivity"


def train_models():
    print("==================================================", flush=True)
    print("STARTING MACHINE LEARNING MODEL TRAINING PIPELINE", flush=True)
    print("==================================================", flush=True)

    temp_engine = create_engine(DB_URL, pool_pre_ping=True)
    query = """
        SELECT 
            t.id AS task_id,
            t.title,
            t.description,
            t.user_id,
            u.name AS user_name,
            u.department,
            u.role AS user_role,
            t.category_id,
            c.name AS category_name,
            t.priority,
            t.status,
            t.created_at,
            t.updated_at,
            t.deadline,
            t.completed_at,
            CAST(t.estimated_hours AS FLOAT) AS estimated_hours,
            CAST(t.actual_hours AS FLOAT) AS actual_hours
        FROM tasks t
        JOIN users u ON t.user_id = u.id
        JOIN categories c ON t.category_id = c.id
    """
    with temp_engine.connect() as conn:
        raw_df = pd.read_sql(text(query), conn)
    temp_engine.dispose()

    print(f"Loaded raw records from PostgreSQL: {len(raw_df)}", flush=True)

    df, stats = extract_ml_dataset(raw_df)
    print(f"Extracted completed historical training records: {stats['completed_records']}", flush=True)
    print(f"Ground Truth Class Balance: Late = {stats['late_records']}, On-Time = {stats['on_time_records']}", flush=True)

    if len(df) < 10:
        print("ERROR: Insufficient historical completed tasks to train ML models!", flush=True)
        return

    X = df[FEATURE_COLUMNS]
    y_cls = df['is_late']

    X_train, X_test, y_cls_train, y_cls_test = train_test_split(
        X, y_cls, test_size=0.25, random_state=42, stratify=y_cls
    )

    print("\nTraining & Evaluating Classification Models...", flush=True)
    clf_pipeline, clf_metrics, clf_comparison = train_and_evaluate_classifiers(
        X_train, y_cls_train, X_test, y_cls_test
    )
    print(f"Selected Classification Model: {clf_comparison['selected_model']}", flush=True)
    print(f"Classification Metrics: Accuracy={clf_metrics['accuracy']}, Precision={clf_metrics['precision']}, Recall={clf_metrics['recall']}, F1={clf_metrics['f1']}, ROC-AUC={clf_metrics['roc_auc']}", flush=True)

    df_reg = df.dropna(subset=['completion_days'])
    X_reg = df_reg[FEATURE_COLUMNS]
    y_reg = df_reg['completion_days']

    X_reg_train, X_reg_test, y_reg_train, y_reg_test = train_test_split(
        X_reg, y_reg, test_size=0.25, random_state=42
    )

    print("\nTraining & Evaluating Regression Models...", flush=True)
    reg_pipeline, reg_metrics, reg_comparison = train_and_evaluate_regressors(
        X_reg_train, y_reg_train, X_reg_test, y_reg_test
    )
    print(f"Selected Regression Model: {reg_comparison['selected_model']}", flush=True)
    print(f"Regression Metrics: MAE={reg_metrics['mae_days']} days, RMSE={reg_metrics['rmse_days']} days, R2={reg_metrics['r2_score']}", flush=True)

    clf_imp = extract_feature_importance(clf_pipeline)
    reg_imp = extract_feature_importance(reg_pipeline)

    print("\nTop Overdue Classification Features:", flush=True)
    for f in clf_imp[:5]:
        print(f"  {f['feature']}: {f['importance']}", flush=True)

    clf_path = os.path.join(MODEL_DIR, 'overdue_classifier.joblib')
    reg_path = os.path.join(MODEL_DIR, 'completion_regressor.joblib')
    meta_path = os.path.join(MODEL_DIR, 'model_metadata.joblib')

    joblib.dump(clf_pipeline, clf_path)
    joblib.dump(reg_pipeline, reg_path)

    metadata = {
        'version': '1.0.0-prod',
        'trained_at': datetime.now(timezone.utc).isoformat(),
        'dataset_summary': stats,
        'classification_model': clf_metrics['model'],
        'classification_metrics': clf_metrics,
        'classification_comparison': clf_comparison,
        'regression_model': reg_metrics['model'],
        'regression_metrics': reg_metrics,
        'regression_comparison': reg_comparison,
        'feature_importance': {
            'classification': clf_imp,
            'regression': reg_imp
        }
    }

    joblib.dump(metadata, meta_path)

    print("\n==================================================", flush=True)
    print(f"SUCCESS: Trained models saved to {MODEL_DIR}", flush=True)
    print("==================================================", flush=True)


if __name__ == '__main__':
    train_models()
