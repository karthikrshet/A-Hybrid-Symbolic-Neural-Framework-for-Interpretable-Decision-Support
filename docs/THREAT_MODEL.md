# SECURITY THREAT MODEL & MITIGATIONS

| Threat Vector | Attack Scenario | Implemented Mitigation |
| :--- | :--- | :--- |
| **Prompt Injection** | Attacker injects instructions into transaction memo | Natural language prompts cannot override deterministic symbolic rules. |
| **Model Inversion** | Repeated API probing to reconstruct training distributions | Rate limiting on inference endpoints + decision margin rounding. |
| **Audit Tampering** | Malicious DB admin alters decision history records | SHA-256 cryptographic hash-chaining prevents retroactive alterations. |
| **Smurfing (Structuring)** | Splitting large transactions into micro-amounts below threshold | Rule `RULE-RISK-008` detects rapid succession of sub-threshold transfers. |
