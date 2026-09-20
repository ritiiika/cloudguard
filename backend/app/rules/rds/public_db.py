from typing import Any

from app.rules.base import BaseRule, RuleResult


class RDSPublicAccessRule(BaseRule):
    rule_id = "RDS_PUBLIC_ACCESS"
    name = "RDS Database Instance Publicly Accessible"
    category = "RDS"
    severity = "CRITICAL"
    description = "RDS database instance has the 'PubliclyAccessible' flag enabled, exposing the database port to the internet."
    remediation = "Modify the RDS instance and set 'Publicly Accessible' to No. Place database in private database subnets."

    def evaluate(self, resource: dict[str, Any]) -> list[RuleResult]:
        # resource is a DBInstance dict
        db_id = resource.get("DBInstanceIdentifier", "unknown")
        db_arn = resource.get("DBInstanceArn", f"arn:aws:rds:::db:{db_id}")
        is_public = resource.get("PubliclyAccessible", False)

        if is_public:
            return [
                RuleResult(
                    passed=False,
                    rule_id=self.rule_id,
                    resource_id=db_arn,
                    resource_type="rds_instance",
                    severity=self.severity,
                    title=f"RDS Instance '{db_id}' is publicly accessible",
                    description=f"Database {db_id} is configured with public internet exposure.",
                    remediation=self.remediation,
                    raw_details={"db_identifier": db_id, "publicly_accessible": True}
                )
            ]
        return []
