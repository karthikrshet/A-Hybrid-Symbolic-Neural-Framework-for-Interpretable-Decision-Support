import os
import pandas as pd
from fastapi import APIRouter
from ml.datasets.generator import generate_financial_dataset

router = APIRouter(prefix="/datasets", tags=["Datasets"])

DATASET_CSV = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../ml/datasets/transactions_synthetic.csv"))

def get_or_create_dataset():
    if not os.path.exists(DATASET_CSV):
        df = generate_financial_dataset(n_samples=5000, seed=42)
        os.makedirs(os.path.dirname(DATASET_CSV), exist_ok=True)
        df.to_csv(DATASET_CSV, index=False)
    else:
        try:
            df = pd.read_csv(DATASET_CSV)
        except Exception:
            df = generate_financial_dataset(n_samples=5000, seed=42)
            df.to_csv(DATASET_CSV, index=False)
    return df

@router.get("/info")
def get_dataset_info():
    df = get_or_create_dataset()
    fraud_count = int(df["is_fraud"].sum())
    total_count = len(df)
    
    return {
        "dataset_name": "Synthetic Financial Risk & AML Transactions Benchmark",
        "total_records": total_count,
        "fraud_cases": fraud_count,
        "legitimate_cases": total_count - fraud_count,
        "fraud_rate": float(fraud_count / total_count),
        "features_count": len(df.columns) - 1,
        "features": list(df.columns),
        "summary_statistics": {
            "mean_amount": float(df["transaction_amount"].mean()),
            "median_amount": float(df["transaction_amount"].median()),
            "max_amount": float(df["transaction_amount"].max()),
            "mean_frequency": float(df["transaction_frequency_24h"].mean()),
            "mean_velocity_ratio": float(df["velocity_change_ratio"].mean())
        }
    }

@router.get("/sample")
def get_dataset_sample(limit: int = 25):
    df = get_or_create_dataset()
    sample_df = df.head(limit)
    return sample_df.to_dict(orient="records")
