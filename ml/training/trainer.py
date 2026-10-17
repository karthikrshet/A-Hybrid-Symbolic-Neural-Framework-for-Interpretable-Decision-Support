import os
import json
import joblib
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, average_precision_score
from ml.datasets.generator import generate_financial_dataset
from ml.preprocessing.preprocessor import FinancialFeaturePreprocessor, FEATURE_COLUMNS

def train_and_evaluate_model():
    print("Generating synthetic training dataset...")
    df = generate_financial_dataset(n_samples=6000, seed=42)
    
    X = df[FEATURE_COLUMNS]
    y = df["is_fraud"]
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42, stratify=y)
    
    preprocessor = FinancialFeaturePreprocessor()
    X_train_scaled = preprocessor.fit_transform(X_train)
    X_test_scaled = preprocessor.transform(X_test)
    
    print("Training base Random Forest model...")
    base_rf = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        min_samples_split=5,
        class_weight="balanced",
        random_state=42,
        n_jobs=-1
    )
    base_rf.fit(X_train_scaled, y_train)
    
    print("Calibrating probabilities via CalibratedClassifierCV (Platt Scaling)...")
    calibrated_model = CalibratedClassifierCV(estimator=base_rf, method="sigmoid", cv="prefit")
    calibrated_model.fit(X_train_scaled, y_train)
    
    # Evaluate
    y_pred = calibrated_model.predict(X_test_scaled)
    y_prob = calibrated_model.predict_proba(X_test_scaled)[:, 1]
    
    metrics = {
        "accuracy": float(accuracy_score(y_test, y_pred)),
        "precision": float(precision_score(y_test, y_pred, zero_division=0)),
        "recall": float(recall_score(y_test, y_pred, zero_division=0)),
        "f1_score": float(f1_score(y_test, y_pred, zero_division=0)),
        "roc_auc": float(roc_auc_score(y_test, y_prob)),
        "pr_auc": float(average_precision_score(y_test, y_prob)),
        "test_samples": len(y_test),
        "test_fraud_rate": float(y_test.mean())
    }
    print(f"Trained Model Metrics: {json.dumps(metrics, indent=2)}")
    
    artifacts_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../artifacts"))
    os.makedirs(artifacts_dir, exist_ok=True)
    
    model_path = os.path.join(artifacts_dir, "fraud_risk_model.joblib")
    preproc_path = os.path.join(artifacts_dir, "feature_preprocessor.joblib")
    meta_path = os.path.join(artifacts_dir, "model_metadata.json")
    
    joblib.dump(calibrated_model, model_path)
    preprocessor.save(preproc_path)
    
    metadata = {
        "model_version": "1.0.0-rf-calibrated",
        "algorithm": "RandomForestClassifier + PlattSigmoidCalibration",
        "features": FEATURE_COLUMNS,
        "metrics": metrics,
        "training_samples": len(X_train)
    }
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)
        
    print(f"Artifacts successfully saved to {artifacts_dir}")
    return calibrated_model, preprocessor, metrics

if __name__ == "__main__":
    train_and_evaluate_model()
