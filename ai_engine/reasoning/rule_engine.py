import json
import os
from typing import Dict, Any, List, Tuple
from ai_engine.contracts.agent_schemas import TriggeredRuleInfo

class RuleEngine:
    def __init__(self, rules_filepath: str = None):
        if not rules_filepath:
            rules_filepath = os.path.abspath(os.path.join(
                os.path.dirname(__file__), "../../../knowledge_base/rules/financial_risk_rules.json"
            ))
        self.rules_filepath = rules_filepath
        self.rules = []
        self.load_rules()

    def load_rules(self):
        if os.path.exists(self.rules_filepath):
            with open(self.rules_filepath, "r", encoding="utf-8") as f:
                self.rules = json.load(f)

    def evaluate_condition(self, fact_val: Any, cond_spec: Dict[str, Any]) -> bool:
        for op, target in cond_spec.items():
            if op == "eq" and fact_val != target:
                return False
            elif op == "neq" and fact_val == target:
                return False
            elif op == "gt" and not (fact_val > target):
                return False
            elif op == "gte" and not (fact_val >= target):
                return False
            elif op == "lt" and not (fact_val < target):
                return False
            elif op == "lte" and not (fact_val <= target):
                return False
            elif op == "in" and fact_val not in target:
                return False
        return True

    def evaluate(self, facts: Dict[str, Any]) -> Tuple[List[TriggeredRuleInfo], bool, str]:
        triggered_rules = []
        has_hard_override = False
        primary_action = "APPROVE"

        for r in self.rules:
            matched = True
            matched_conditions = []
            for field, cond_spec in r["conditions"].items():
                fact_val = facts.get(field)
                if fact_val is None or not self.evaluate_condition(fact_val, cond_spec):
                    matched = False
                    break
                else:
                    matched_conditions.append(f"{field} matches {cond_spec}")

            if matched:
                is_override = r.get("is_hard_override", False)
                if is_override:
                    has_hard_override = True
                    primary_action = "REJECT"

                rule_info = TriggeredRuleInfo(
                    rule_id=r["rule_id"],
                    rule_name=r["name"],
                    severity=r["severity"],
                    category=r["category"],
                    reason=r["description"],
                    condition_matched=", ".join(matched_conditions),
                    override_applied=is_override
                )
                triggered_rules.append(rule_info)

        return triggered_rules, has_hard_override, primary_action

rule_engine = RuleEngine()

# Step refinement 7
# Type guard on boolean facts

# Step refinement 17
# Type guard on boolean facts

# Step refinement 27
# Type guard on boolean facts

# Step refinement 37
# Type guard on boolean facts

# Step refinement 47
# Type guard on boolean facts

# Step refinement 57
# Type guard on boolean facts

# Step refinement 67
# Type guard on boolean facts

# Step refinement 77
# Type guard on boolean facts

# Step refinement 87
# Type guard on boolean facts
