import pandas as pd
import numpy as np
import joblib
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.preprocessing import StandardScaler

FEATURE_COLUMNS = [
    "transaction_amount",
    "transaction_frequency_24h",
    "velocity_change_ratio",
    "location_distance_km",
    "hour_of_day",
    "is_weekend",
    "is_sanctioned_destination",
    "kyc_incomplete",
    "foreign_exchange_risk",
    "ip_reputation_score",
    "device_trust_score",
    "user_failed_attempts_1h",
    "past_chargeback_count"
]

class FinancialFeaturePreprocessor(BaseEstimator, TransformerMixin):
    def __init__(self):
        self.scaler = StandardScaler()
        self.feature_columns = FEATURE_COLUMNS

    def fit(self, X, y=None):
        df = X[self.feature_columns].copy()
        self.scaler.fit(df)
        return self

    def transform(self, X):
        df = X[self.feature_columns].copy()
        scaled_vals = self.scaler.transform(df)
        return pd.DataFrame(scaled_vals, columns=self.feature_columns, index=df.index)

    def save(self, filepath: str):
        joblib.dump(self, filepath)

    @classmethod
    def load(cls, filepath: str):
        return joblib.load(filepath)
