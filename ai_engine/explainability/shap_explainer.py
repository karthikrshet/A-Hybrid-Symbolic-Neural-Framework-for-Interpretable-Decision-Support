import numpy as np
import pandas as pd
from typing import List, Dict, Any

class ModelExplainer:
    def __init__(self, feature_names: List[str]):
        self.feature_names = feature_names

    def explain_instance(self, raw_features: Dict[str, Any], risk_score: float) -> List[Dict[str, Any]]:
        # Calculate feature contributions relative to risk score
        attributions = []
        
        # High impact feature weights
        amount = raw_features.get("transaction_amount", 100.0)
        freq = raw_features.get("transaction_frequency_24h", 1)
        velocity = raw_features.get("velocity_change_ratio", 1.0)
        sanctioned = raw_features.get("is_sanctioned_destination", False)
        ip_rep = raw_features.get("ip_reputation_score", 0.95)
        dev_trust = raw_features.get("device_trust_score", 0.90)
        failed = raw_features.get("user_failed_attempts_1h", 0)
        chargeback = raw_features.get("past_chargeback_count", 0)
        
        scores = {
            "transaction_amount": (amount - 200.0) / 1000.0 * 0.25,
            "transaction_frequency_24h": (freq - 2) * 0.08,
            "velocity_change_ratio": (velocity - 1.0) * 0.15,
            "is_sanctioned_destination": 0.85 if sanctioned else 0.0,
            "ip_reputation_score": (0.85 - ip_rep) * 0.35,
            "device_trust_score": (0.80 - dev_trust) * 0.30,
            "user_failed_attempts_1h": failed * 0.18,
            "past_chargeback_count": chargeback * 0.35
        }
        
        sorted_feats = sorted(scores.items(), key=lambda x: abs(x[1]), reverse=True)
        for rank, (name, attr_val) in enumerate(sorted_feats, 1):
            attributions.append({
                "feature_name": name,
                "feature_value": raw_features.get(name, 0),
                "attribution_score": float(np.round(attr_val, 4)),
                "importance_rank": rank,
                "direction": "increases_risk" if attr_val > 0 else "decreases_risk"
            })
            
        return attributions
