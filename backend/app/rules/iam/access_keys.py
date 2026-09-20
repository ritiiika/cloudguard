from datetime import UTC, datetime, timedelta
from typing import Any

from app.rules.base import BaseRule, RuleResult


class IAMInactiveAccessKeysRule(BaseRule):
    rule_id = "IAM_ACCESS_KEYS_ROTATION"
    name = "IAM Access Keys Older than 90 Days"
    category = "IAM"
    severity = "MEDIUM"
    description = "IAM user has active access keys that have not been rotated within the recommended 90-day window."
    remediation = "Generate a new access key, update applications, and deactivate/delete old access keys."

    def evaluate(self, resource: dict[str, Any]) -> list[RuleResult]:
        # resource is an individual IAM user info dict
        username = resource.get("username", "unknown")
        user_arn = resource.get("arn", f"arn:aws:iam::user/{username}")
        keys = resource.get("access_keys", [])

        findings = []
        now = datetime.now(UTC)
        max_age = timedelta(days=90)

        for key in keys:
            if key.get("Status") == "Active":
                create_date = key.get("CreateDate")
                if create_date:
                    # Handle timezone aware / naive
                    if create_date.tzinfo is None:
                        create_date = create_date.replace(tzinfo=UTC)
                    age = now - create_date
                    if age > max_age:
                        findings.append(
                            RuleResult(
                                passed=False,
                                rule_id=self.rule_id,
                                resource_id=f"{user_arn}/access-key/{key.get('AccessKeyId')}",
                                resource_type="iam_access_key",
                                severity=self.severity,
                                title=f"IAM User '{username}' has an unrotated access key ({age.days} days old)",
                                description=f"Access Key {key.get('AccessKeyId')} for user {username} is older than 90 days.",
                                remediation=self.remediation,
                                raw_details={"key_id": key.get("AccessKeyId"), "age_days": age.days}
                            )
                        )
        return findings
