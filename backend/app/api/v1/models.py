import os
import json
from fastapi import APIRouter
from ml.training.trainer import train_and_evaluate_model
from ai_engine.inference.model_manager import model_manager

router = APIRouter(prefix="/models", tags=["Machine Learning Models"])

@router.get("/info")
def get_model_info():
    meta_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../ml/artifacts/model_metadata.json"))
    if os.path.exists(meta_path):
        with open(meta_path, "r", encoding="utf-8") as f:
            metadata = json.load(f)
    else:
        metadata = {
            "model_version": "1.0.0-rf-calibrated",
            "algorithm": "RandomForestClassifier + PlattSigmoidCalibration",
            "status": "LOADED"
        }
    return metadata

@router.post("/retrain")
def retrain_model():
    model, preprocessor, metrics = train_and_evaluate_model()
    model_manager.load_artifacts()
    return {
        "status": "RETRAINED_SUCCESSFULLY",
        "model_version": "1.0.0-rf-calibrated",
        "new_metrics": metrics
    }
