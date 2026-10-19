import numpy as np
import pandas as pd
import shap
from typing import List, Dict, Any, Optional

class ModelExplainer:
    def __init__(self, feature_names: List[str], base_model: Optional[Any] = None):
        self.feature_names = feature_names
        self.explainer = None
        if base_model is not None:
            self.set_model(base_model)

    def set_model(self, base_model: Any):
        try:
            # Handle CalibratedClassifierCV
            if hasattr(base_model, "calibrated_classifiers_"):
                rf_estimator = base_model.calibrated_classifiers_[0].estimator
            else:
                rf_estimator = base_model
            self.explainer = shap.TreeExplainer(rf_estimator)
        except Exception as e:
            print(f"Warning: TreeExplainer fallback: {e}")
            self.explainer = None

    def explain_instance(self, scaled_df: pd.DataFrame, raw_features: Dict[str, Any]) -> List[Dict[str, Any]]:
        attributions = []
        if self.explainer is not None:
            try:
                shap_vals = self.explainer.shap_values(scaled_df)
                # For binary classification: class 1 (fraud)
                if isinstance(shap_vals, np.ndarray) and len(shap_vals.shape) == 3:
                    class1_shap = shap_vals[0, :, 1]
                elif isinstance(shap_vals, list) and len(shap_vals) > 1:
                    class1_shap = shap_vals[1][0]
                else:
                    class1_shap = shap_vals[0]

                # Pair with feature names
                scored = []
                for idx, feat_name in enumerate(self.feature_names):
                    score = float(class1_shap[idx])
                    raw_val = raw_features.get(feat_name, 0)
                    scored.append((feat_name, raw_val, score))

                # Sort by absolute attribution magnitude
                scored.sort(key=lambda x: abs(x[2]), reverse=True)

                for rank, (name, val, score) in enumerate(scored, 1):
                    attributions.append({
                        "feature_name": name,
                        "feature_value": val,
                        "attribution_score": float(np.round(score, 4)),
                        "importance_rank": rank,
                        "direction": "increases_risk" if score > 0 else "decreases_risk"
                    })
                return attributions
            except Exception as ex:
                print(f"SHAP explanation computation error: {ex}")

        # Fallback to normalized feature ranking if explainer fails
        for rank, name in enumerate(self.feature_names, 1):
            val = raw_features.get(name, 0)
            attributions.append({
                "feature_name": name,
                "feature_value": val,
                "attribution_score": 0.0,
                "importance_rank": rank,
                "direction": "neutral"
            })
        return attributions
