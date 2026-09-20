from typing import Any, Dict, List
from app.rules.base import BaseRule, RuleResult


class S3BucketEncryptionRule(BaseRule):
    rule_id = "S3_BUCKET_ENCRYPTION"
    name = "S3 Bucket Default Encryption Disabled"
    category = "S3"
    severity = "HIGH"
    description = "S3 bucket does not have default server-side encryption (SSE-S3 or SSE-KMS) configured."
    remediation = "Enable default SSE-S3 or AWS KMS encryption under bucket Properties -> Default encryption."

    def evaluate(self, resource: Dict[str, Any]) -> List[RuleResult]:
        encryption = resource.get("encryption")
        if not encryption or not encryption.get("Rules"):
            return [
                RuleResult(
                    passed=False,
                    rule_id=self.rule_id,
                    resource_id=resource.get("arn", resource.get("name", "unknown")),
                    resource_type="s3_bucket",
                    severity=self.severity,
                    title=f"S3 Bucket '{resource.get('name')}' is unencrypted at rest",
                    description=f"Bucket {resource.get('name')} does not enforce server-side encryption for objects.",
                    remediation=self.remediation,
                    raw_details={"encryption": encryption}
                )
            ]
        return []
