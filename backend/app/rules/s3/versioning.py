from typing import Any, Dict, List
from app.rules.base import BaseRule, RuleResult


class S3BucketVersioningRule(BaseRule):
    rule_id = "S3_BUCKET_VERSIONING"
    name = "S3 Bucket Object Versioning Disabled"
    category = "S3"
    severity = "LOW"
    description = "S3 bucket does not have object versioning enabled, leaving objects vulnerable to accidental deletion or overwrites."
    remediation = "Enable Bucket Versioning in S3 properties to maintain immutable history of modified objects."

    def evaluate(self, resource: Dict[str, Any]) -> List[RuleResult]:
        versioning_status = resource.get("versioning", "Disabled")
        if versioning_status != "Enabled":
            return [
                RuleResult(
                    passed=False,
                    rule_id=self.rule_id,
                    resource_id=resource.get("arn", resource.get("name", "unknown")),
                    resource_type="s3_bucket",
                    severity=self.severity,
                    title=f"S3 Bucket '{resource.get('name')}' versioning disabled",
                    description=f"Bucket {resource.get('name')} has versioning status '{versioning_status}'.",
                    remediation=self.remediation,
                    raw_details={"versioning": versioning_status}
                )
            ]
        return []
