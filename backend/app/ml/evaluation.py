import pandas as pd
import numpy as np
from typing import List, Dict, Any
from sklearn.pipeline import Pipeline


def get_feature_names_from_pipeline(pipeline: Pipeline) -> List[str]:
    """Extract feature names after ColumnTransformer preprocessing."""
    preprocessor = pipeline.named_steps['preprocessor']
    feature_names = []

    for name, trans, cols in preprocessor.transformers_:
        if name == 'num':
            feature_names.extend(cols)
        elif name == 'cat':
            if hasattr(trans.named_steps['onehot'], 'get_feature_names_out'):
                cat_names = trans.named_steps['onehot'].get_feature_names_out(cols).tolist()
                feature_names.extend(cat_names)
            else:
                feature_names.extend(cols)

    return feature_names


def extract_feature_importance(pipeline: Pipeline) -> List[Dict[str, Any]]:
    """Extract interpretable feature importance or absolute coefficient values."""
    model = pipeline.steps[-1][1]
    feature_names = get_feature_names_from_pipeline(pipeline)

    if hasattr(model, 'feature_importances_'):
        importances = model.feature_importances_
    elif hasattr(model, 'coef_'):
        importances = np.abs(model.coef_[0]) if model.coef_.ndim > 1 else np.abs(model.coef_)
    else:
        return []

    # Map OneHot encoded features back to friendly base feature names
    raw_importance = list(zip(feature_names, importances))
    
    # Aggregate importance by raw feature name
    base_importance: Dict[str, float] = {}
    for fname, imp in raw_importance:
        base_name = fname.split('_')[0] if '_' in fname and not fname.startswith('estimated') and not fname.startswith('days') and not fname.startswith('user_') else fname
        base_importance[base_name] = base_importance.get(base_name, 0.0) + float(imp)

    # Normalize
    total_imp = sum(base_importance.values()) or 1.0
    sorted_items = [
        {"feature": k, "importance": round(v / total_imp, 4)}
        for k, v in sorted(base_importance.items(), key=lambda x: x[1], reverse=True)
    ]

    return sorted_items
