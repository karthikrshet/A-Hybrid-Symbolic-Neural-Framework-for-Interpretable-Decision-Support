import os
import json
import joblib
import pandas as pd
import numpy as np
from typing import Dict, Any, Tuple
from ml.preprocessing.preprocessor import FEATURE_COLUMNS, FinancialFeaturePreprocessor
from ai_engine.explainability.shap_explainer import ModelExplainer

class ModelManager:
    _instance = None

    def __init__(self):
        self.artifacts_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../ml/artifacts"))
        self.model_path = os.path.join(self.artifacts_dir, "fraud_risk_model.joblib")
        self.preproc_path = os.path.join(self.artifacts_dir, "feature_preprocessor.joblib")
        self.meta_path = os.path.join(self.artifacts_dir, "model_metadata.json")
        
        self.model = None
        self.preprocessor = None
        self.metadata = {}
        self.explainer = ModelExplainer(FEATURE_COLUMNS)
        self.load_artifacts()

    def load_artifacts(self):
        if os.path.exists(self.model_path) and os.path.exists(self.preproc_path):
            self.model = joblib.load(self.model_path)
            self.preprocessor = FinancialFeaturePreprocessor.load(self.preproc_path)
            if os.path.exists(self.meta_path):
                with open(self.meta_path, "r", encoding="utf-8") as f:
                    self.metadata = json.load(f)
        else:
            self.metadata = {"model_version": "1.0.0-heuristic-fallback", "algorithm": "DeterministicFallback"}

    def predict(self, raw_features: Dict[str, Any]) -> Tuple[float, str, list]:
        if self.model and self.preprocessor:
            row_dict = {}
            for col in FEATURE_COLUMNS:
                if col == "kyc_incomplete":
                    row_dict[col] = 1 if raw_features.get("kyc_status") == "INCOMPLETE" else 0
                else:
                    row_dict[col] = raw_features.get(col, 0)
            df = pd.DataFrame([row_dict])
            scaled = self.preprocessor.transform(df)
            prob = float(self.model.predict_proba(scaled)[0, 1])
        else:
            # Deterministic heuristic fallback
            amt = raw_features.get("transaction_amount", 100.0)
            prob = min(0.98, max(0.02, amt / 5000.0 * 0.5))
            
        label = "HIGH_RISK" if prob >= 0.70 else "MEDIUM_RISK" if prob >= 0.30 else "LOW_RISK"
        attributions = self.explainer.explain_instance(raw_features, prob)
        return prob, label, attributions

model_manager = ModelManager()

# Step refinement 2
# Vectorized batch inference hook

# Step refinement 12
# Vectorized batch inference hook

# Step refinement 22
# Vectorized batch inference hook
