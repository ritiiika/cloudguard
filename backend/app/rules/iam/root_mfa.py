from typing import Any

from app.rules.base import BaseRule, RuleResult


class IAMRootMFAEnabledRule(BaseRule):
    rule_id = "IAM_ROOT_MFA_ENABLED"
    name = "Root Account MFA Not Enabled"
    category = "IAM"
    severity = "CRITICAL"
    description = "The AWS account root user does not have Multi-Factor Authentication (MFA) enabled."
    remediation = "Sign in as the root user and enable a hardware or virtual MFA device immediately under IAM Security Credentials."

    def evaluate(self, resource: dict[str, Any]) -> list[RuleResult]:
        # resource is the entire iam_data dictionary
        mfa_enabled = resource.get("account_mfa_enabled", False)
        if not mfa_enabled:
            return [
                RuleResult(
                    passed=False,
                    rule_id=self.rule_id,
                    resource_id="arn:aws:iam::root",
                    resource_type="iam_root",
                    severity=self.severity,
                    title="Root account lacks Multi-Factor Authentication (MFA)",
                    description="The root user has unrestricted access to all AWS resources and is not protected by MFA.",
                    remediation=self.remediation,
                    raw_details={"account_mfa_enabled": False}
                )
            ]
        return []
