from typing import Any

from app.rules.base import BaseRule, RuleResult


class S3PublicAccessBlockRule(BaseRule):
    rule_id = "S3_PUBLIC_ACCESS_BLOCK"
    name = "S3 Bucket Public Access Block Not Fully Enabled"
    category = "S3"
    severity = "CRITICAL"
    description = "S3 bucket does not have all 4 Public Access Block settings enabled (BlockPublicAcls, IgnorePublicAcls, BlockPublicPolicy, RestrictPublicBuckets)."
    remediation = "Enable 'Block all public access' at the bucket level using the AWS Console or aws s3api put-public-access-block."

    def evaluate(self, resource: dict[str, Any]) -> list[RuleResult]:
        pab = resource.get("public_access_block") or {}

        block_acls = pab.get("BlockPublicAcls", False)
        ignore_acls = pab.get("IgnorePublicAcls", False)
        block_policy = pab.get("BlockPublicPolicy", False)
        restrict_buckets = pab.get("RestrictPublicBuckets", False)

        is_secure = block_acls and ignore_acls and block_policy and restrict_buckets

        if not is_secure:
            return [
                RuleResult(
                    passed=False,
                    rule_id=self.rule_id,
                    resource_id=resource.get("arn", resource.get("name", "unknown")),
                    resource_type="s3_bucket",
                    severity=self.severity,
                    title=f"S3 Bucket '{resource.get('name')}' is potentially public",
                    description=f"Public access block settings are missing or disabled on bucket {resource.get('name')}.",
                    remediation=self.remediation,
                    raw_details={"public_access_block": pab}
                )
            ]
        return []
