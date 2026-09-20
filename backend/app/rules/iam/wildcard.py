from typing import Any, Dict, List
from app.rules.base import BaseRule, RuleResult


class IAMWildcardPolicyRule(BaseRule):
    rule_id = "IAM_ADMIN_WILDCARD_POLICY"
    name = "IAM User Has Direct Full Administrative Privileges"
    category = "IAM"
    severity = "HIGH"
    description = "IAM user has AdministratorAccess or full wildcard permissions attached directly instead of role-based least privilege."
    remediation = "Apply least-privilege permissions by granting specific service actions and scoping resources to ARNs."

    def evaluate(self, resource: Dict[str, Any]) -> List[RuleResult]:
        username = resource.get("username", "unknown")
        user_arn = resource.get("arn", f"arn:aws:iam::user/{username}")
        attached_policies = resource.get("attached_policies", [])

        findings = []
        for policy in attached_policies:
            policy_name = policy.get("PolicyName", "")
            policy_arn = policy.get("PolicyArn", "")
            if policy_name == "AdministratorAccess" or "AdministratorAccess" in policy_arn:
                findings.append(
                    RuleResult(
                        passed=False,
                        rule_id=self.rule_id,
                        resource_id=user_arn,
                        resource_type="iam_user",
                        severity=self.severity,
                        title=f"IAM User '{username}' has direct AdministratorAccess attached",
                        description=f"User {username} is attached with full admin policy {policy_name}.",
                        remediation=self.remediation,
                        raw_details={"policy_name": policy_name, "policy_arn": policy_arn}
                    )
                )
        return findings
