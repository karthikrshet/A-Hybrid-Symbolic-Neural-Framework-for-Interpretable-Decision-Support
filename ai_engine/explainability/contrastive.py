"""Contrastive explanation engine synthesizing counterfactual conditions."""

from typing import Dict, Any, List

class ContrastiveExplainer:
    @staticmethod
    def generate_counterfactuals(decision: str, features: Dict[str, Any], triggered_rules: List[str]) -> List[str]:
        suggestions = []
        if decision == "REJECT":
            if features.get("is_sanctioned_destination"):
                suggestions.append("Reroute transaction to a compliant non-sanctioned financial corridor.")
            if features.get("kyc_status") == "INCOMPLETE":
                suggestions.append("Complete Tier-3 KYC verification with biometric validation.")
            if features.get("transaction_amount", 0) > 10000:
                suggestions.append("Lower transfer volume beneath the statutory AML enhanced due diligence threshold ($10,000).")
            if features.get("velocity_change_ratio", 1.0) > 3.0:
                suggestions.append("Stagger disbursements to avoid automated high-velocity anomaly alarms.")
        elif decision == "FLAG_SUSPICIOUS":
            suggestions.append("Authenticate via hardware security token (FIDO2/WebAuthn) to restore device trust score.")
            suggestions.append("Perform transaction from a residential registered IP address rather than VPN/datacenter.")
        else:
            suggestions.append("Transaction currently meets all compliance invariants; no corrective action required.")
        return suggestions
