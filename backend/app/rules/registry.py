from typing import Any, Dict, List
from app.rules.base import BaseRule, RuleResult
from app.rules.s3 import S3PublicAccessBlockRule, S3BucketEncryptionRule, S3BucketVersioningRule
from app.rules.iam import IAMRootMFAEnabledRule, IAMInactiveAccessKeysRule, IAMWildcardPolicyRule
from app.rules.ec2 import EC2OpenSSHRule, EC2OpenRDPRule
from app.rules.rds import RDSPublicAccessRule, RDSEncryptionRule


class RuleRegistry:
    def __init__(self):
        # S3 bucket rules
        self.s3_rules: List[BaseRule] = [
            S3PublicAccessBlockRule(),
            S3BucketEncryptionRule(),
            S3BucketVersioningRule(),
        ]
        # IAM root & user rules
        self.iam_root_rules: List[BaseRule] = [
            IAMRootMFAEnabledRule(),
        ]
        self.iam_user_rules: List[BaseRule] = [
            IAMInactiveAccessKeysRule(),
            IAMWildcardPolicyRule(),
        ]
        # Security Group rules
        self.sg_rules: List[BaseRule] = [
            EC2OpenSSHRule(),
            EC2OpenRDPRule(),
        ]
        # RDS rules
        self.rds_rules: List[BaseRule] = [
            RDSPublicAccessRule(),
            RDSEncryptionRule(),
        ]

    def evaluate_inventory(self, inventory: Dict[str, Any]) -> List[RuleResult]:
        """Runs all registered security checks against the discovered resource inventory."""
        findings: List[RuleResult] = []

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
