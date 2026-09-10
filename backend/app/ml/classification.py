import pandas as pd
import numpy as np
from typing import Dict, Any, Tuple
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix
)
from app.ml.preprocessing import create_preprocessor
from app.ml.features import FEATURE_COLUMNS


def train_and_evaluate_classifiers(
    X_train: pd.DataFrame,
    y_train: pd.Series,
    X_test: pd.DataFrame,
    y_test: pd.Series
) -> Tuple[Pipeline, Dict[str, Any], Dict[str, Any]]:
    """
    Train and compare Logistic Regression vs Random Forest Classifier.
    Selects the optimal model based on F1-score & Recall.
    """
    # 1. Logistic Regression Pipeline
    lr_pipeline = Pipeline(steps=[
        ('preprocessor', create_preprocessor()),
        ('classifier', LogisticRegression(class_weight='balanced', max_iter=1000, random_state=42))
    ])
    lr_pipeline.fit(X_train[FEATURE_COLUMNS], y_train)

    lr_preds = lr_pipeline.predict(X_test[FEATURE_COLUMNS])
    lr_probs = lr_pipeline.predict_proba(X_test[FEATURE_COLUMNS])[:, 1]

    lr_metrics = {
        'model': 'LogisticRegression',
        'accuracy': round(float(accuracy_score(y_test, lr_preds)), 4),
        'precision': round(float(precision_score(y_test, lr_preds, zero_division=0)), 4),
        'recall': round(float(recall_score(y_test, lr_preds, zero_division=0)), 4),
        'f1': round(float(f1_score(y_test, lr_preds, zero_division=0)), 4),
        'roc_auc': round(float(roc_auc_score(y_test, lr_probs)), 4) if len(np.unique(y_test)) > 1 else 0.5,
        'confusion_matrix': confusion_matrix(y_test, lr_preds).tolist()
    }

    # 2. Random Forest Classifier Pipeline
    rf_pipeline = Pipeline(steps=[
        ('preprocessor', create_preprocessor()),
        ('classifier', RandomForestClassifier(n_estimators=100, class_weight='balanced', random_state=42, n_jobs=1))
    ])
    rf_pipeline.fit(X_train[FEATURE_COLUMNS], y_train)

    rf_preds = rf_pipeline.predict(X_test[FEATURE_COLUMNS])
    rf_probs = rf_pipeline.predict_proba(X_test[FEATURE_COLUMNS])[:, 1]

    rf_metrics = {
        'model': 'RandomForestClassifier',
        'accuracy': round(float(accuracy_score(y_test, rf_preds)), 4),
        'precision': round(float(precision_score(y_test, rf_preds, zero_division=0)), 4),
        'recall': round(float(recall_score(y_test, rf_preds, zero_division=0)), 4),
        'f1': round(float(f1_score(y_test, rf_preds, zero_division=0)), 4),
        'roc_auc': round(float(roc_auc_score(y_test, rf_probs)), 4) if len(np.unique(y_test)) > 1 else 0.5,
        'confusion_matrix': confusion_matrix(y_test, rf_preds).tolist()
    }

    # Selection logic: Prefer higher F1 score (or Recall if F1 is equal)
    if rf_metrics['f1'] >= lr_metrics['f1']:
        best_pipeline = rf_pipeline
        best_metrics = rf_metrics
        other_metrics = lr_metrics
    else:
        best_pipeline = lr_pipeline
        best_metrics = lr_metrics
        other_metrics = rf_metrics

    comparison = {
        'selected_model': best_metrics['model'],
        'selected_metrics': best_metrics,
        'candidate_metrics': [lr_metrics, rf_metrics]
    }

    return best_pipeline, best_metrics, comparison
