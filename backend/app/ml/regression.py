import pandas as pd
import numpy as np
from typing import Dict, Any, Tuple
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.pipeline import Pipeline
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from app.ml.preprocessing import create_preprocessor
from app.ml.features import FEATURE_COLUMNS


def train_and_evaluate_regressors(
    X_train: pd.DataFrame,
    y_train: pd.Series,
    X_test: pd.DataFrame,
    y_test: pd.Series
) -> Tuple[Pipeline, Dict[str, Any], Dict[str, Any]]:
    """
    Train and compare Linear Regression vs Random Forest Regressor for task completion duration.
    Selects the optimal model based on Mean Absolute Error (MAE in days) and R^2.
    """
    # 1. Linear Regression Pipeline
    lr_pipeline = Pipeline(steps=[
        ('preprocessor', create_preprocessor()),
        ('regressor', LinearRegression(n_jobs=1))
    ])
    lr_pipeline.fit(X_train[FEATURE_COLUMNS], y_train)

    lr_preds = lr_pipeline.predict(X_test[FEATURE_COLUMNS])
    lr_preds = np.maximum(0.1, lr_preds)

    lr_metrics = {
        'model': 'LinearRegression',
        'mae_days': round(float(mean_absolute_error(y_test, lr_preds)), 4),
        'rmse_days': round(float(np.sqrt(mean_squared_error(y_test, lr_preds))), 4),
        'r2_score': round(float(r2_score(y_test, lr_preds)), 4)
    }

    # 2. Random Forest Regressor Pipeline
    rf_pipeline = Pipeline(steps=[
        ('preprocessor', create_preprocessor()),
        ('regressor', RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=1))
    ])
    rf_pipeline.fit(X_train[FEATURE_COLUMNS], y_train)

    rf_preds = rf_pipeline.predict(X_test[FEATURE_COLUMNS])
    rf_preds = np.maximum(0.1, rf_preds)

    rf_metrics = {
        'model': 'RandomForestRegressor',
        'mae_days': round(float(mean_absolute_error(y_test, rf_preds)), 4),
        'rmse_days': round(float(np.sqrt(mean_squared_error(y_test, rf_preds))), 4),
        'r2_score': round(float(r2_score(y_test, rf_preds)), 4)
    }

    # Selection: Lower MAE
    if rf_metrics['mae_days'] <= lr_metrics['mae_days']:
        best_pipeline = rf_pipeline
        best_metrics = rf_metrics
    else:
        best_pipeline = lr_pipeline
        best_metrics = lr_metrics

    comparison = {
        'selected_model': best_metrics['model'],
        'selected_metrics': best_metrics,
        'candidate_metrics': [lr_metrics, rf_metrics]
    }

    return best_pipeline, best_metrics, comparison
