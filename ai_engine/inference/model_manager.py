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
        self.artifacts_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../ml/artifacts"))
        self.model_path = os.path.join(self.artifacts_dir, "fraud_risk_model.joblib")
        self.preproc_path = os.path.join(self.artifacts_dir, "feature_preprocessor.joblib")
        self.meta_path = os.path.join(self.artifacts_dir, "model_metadata.json")
        
        self.model = None
        self.preprocessor = None
        self.metadata = {}
        self.explainer = ModelExplainer(FEATURE_COLUMNS)
        self.load_artifacts()

    def load_artifacts(self):
        if not os.path.exists(self.model_path) or not os.path.exists(self.preproc_path):
            raise FileNotFoundError(
                f"Trained machine learning artifacts not found at {self.model_path}. "
                "Production requires trained model. Run 'python ml/training/trainer.py' first."
            )
        
        self.model = joblib.load(self.model_path)
        self.preprocessor = FinancialFeaturePreprocessor.load(self.preproc_path)
        if os.path.exists(self.meta_path):
            with open(self.meta_path, "r", encoding="utf-8") as f:
                self.metadata = json.load(f)
        
        # Initialize SHAP explainer with the loaded model
        self.explainer.set_model(self.model)

    def predict(self, raw_features: Dict[str, Any]) -> Tuple[float, str, list]:
        if not self.model or not self.preprocessor:
            self.load_artifacts()

        row_dict = {}
        for col in FEATURE_COLUMNS:
            if col == "kyc_incomplete":
                row_dict[col] = 1 if raw_features.get("kyc_status") == "INCOMPLETE" else 0
            else:
                row_dict[col] = raw_features.get(col, 0)
                
        df = pd.DataFrame([row_dict])
        scaled_df = self.preprocessor.transform(df)
        
        # Real calibrated probabilistic inference
        probs = self.model.predict_proba(scaled_df)[0]
        prob = float(probs[1])
            
        label = "HIGH_RISK" if prob >= 0.70 else "MEDIUM_RISK" if prob >= 0.30 else "LOW_RISK"
        
        # Real SHAP feature attributions
        attributions = self.explainer.explain_instance(scaled_df, raw_features)
        return prob, label, attributions

model_manager = ModelManager()
