import json
import re
import os
from typing import Tuple

POLICY_PATH = os.getenv("GUARDIAN_POLICY_PATH", os.path.join(os.path.dirname(__file__), "policies", "agent_rules.json"))

class PolicyEngine:
    def __init__(self, policy_file: str = POLICY_PATH):
        with open(policy_file, "r") as f:
            self.rules = json.load(f)

    def evaluate(self, agent_role: str, action: str, resource: str, duration_seconds: int) -> Tuple[bool, str]:
        """
        Evaluates whether an agent's requested action and resource ARN conform to security boundaries.
        Returns: (is_allowed: bool, reason: str)
        """
        # 1. Global Forbidden Pattern Check (Anti-Privilege Escalation & Anti-Destructive Verbs)
        for pattern in self.rules.get("forbidden_action_patterns", []):
            if re.match(pattern, action, re.IGNORECASE):
                return False, f"Action '{action}' is globally forbidden (matches pattern '{pattern}'). Destructive verbs and IAM manipulations are blocked."

        # 2. Wildcard resource check
        if resource.strip() == "*":
            return False, "Wildcard resources ('*') are strictly disallowed under Zero-Trust agent policy."

        # 3. Agent Role Validity
        roles = self.rules.get("agent_roles", {})
        if agent_role not in roles:
            return False, f"Unrecognized or unregistered agent role '{agent_role}'."

        role_cfg = roles[agent_role]

        # 4. TTL / Max duration check
        max_ttl = role_cfg.get("max_ttl_seconds", 300)
        if duration_seconds > max_ttl:
            return False, f"Requested duration ({duration_seconds}s) exceeds maximum allowed TTL for {agent_role} ({max_ttl}s)."

        # 5. Role Action Allowed Check
        allowed_actions = role_cfg.get("allowed_actions", [])
        if action not in allowed_actions:
            return False, f"Action '{action}' is not in allowed actions for role '{agent_role}'."

        # 6. Role Resource Allowed Pattern Check
        allowed_resources = role_cfg.get("allowed_resources", [])
        resource_match = False
        for res_pattern in allowed_resources:
            if re.match(res_pattern, resource):
                resource_match = True
                break

        if not resource_match:
            return False, f"Resource '{resource}' is outside the authorized boundary for role '{agent_role}'."

        return True, "Intent verified and authorized under zero-trust policy boundaries."

policy_engine = PolicyEngine()
