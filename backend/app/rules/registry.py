from typing import Any

from app.rules.base import BaseRule, RuleResult
from app.rules.ec2 import EC2OpenRDPRule, EC2OpenSSHRule
from app.rules.iam import (
    IAMInactiveAccessKeysRule,
    IAMRootMFAEnabledRule,
    IAMWildcardPolicyRule,
)
from app.rules.rds import RDSEncryptionRule, RDSPublicAccessRule
from app.rules.s3 import (
    S3BucketEncryptionRule,
    S3BucketVersioningRule,
    S3PublicAccessBlockRule,
)


class RuleRegistry:
    def __init__(self):
        # S3 bucket rules
        self.s3_rules: list[BaseRule] = [
            S3PublicAccessBlockRule(),
            S3BucketEncryptionRule(),
            S3BucketVersioningRule(),
        ]
        # IAM root & user rules
        self.iam_root_rules: list[BaseRule] = [
            IAMRootMFAEnabledRule(),
        ]
        self.iam_user_rules: list[BaseRule] = [
            IAMInactiveAccessKeysRule(),
            IAMWildcardPolicyRule(),
        ]
        # Security Group rules
        self.sg_rules: list[BaseRule] = [
            EC2OpenSSHRule(),
            EC2OpenRDPRule(),
        ]
        # RDS rules
        self.rds_rules: list[BaseRule] = [
            RDSPublicAccessRule(),
            RDSEncryptionRule(),
        ]

    def evaluate_inventory(self, inventory: dict[str, Any]) -> list[RuleResult]:
        """Runs all registered security checks against the discovered resource inventory."""
        findings: list[RuleResult] = []

        # 1. Evaluate S3 Buckets
        for bucket in inventory.get("s3", []):
            for rule in self.s3_rules:
                findings.extend(rule.evaluate(bucket))

        # 2. Evaluate IAM Root
        iam_data = inventory.get("iam", {})
        for rule in self.iam_root_rules:
            findings.extend(rule.evaluate(iam_data))

        # 3. Evaluate IAM Users
        for user in iam_data.get("users", []):
            for rule in self.iam_user_rules:
                findings.extend(rule.evaluate(user))

        # 4. Evaluate Security Groups
        for sg in inventory.get("security_groups", []):
            for rule in self.sg_rules:
                findings.extend(rule.evaluate(sg))

        # 5. Evaluate RDS Instances
        for rds_inst in inventory.get("rds", []):
            for rule in self.rds_rules:
                findings.extend(rule.evaluate(rds_inst))

        return findings


rule_registry = RuleRegistry()
