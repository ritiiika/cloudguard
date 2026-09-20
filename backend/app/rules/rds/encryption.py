from typing import Any, Dict, List
from app.rules.base import BaseRule, RuleResult


class RDSEncryptionRule(BaseRule):
    rule_id = "RDS_STORAGE_ENCRYPTION"
    name = "RDS Database Storage Encryption Disabled"
    category = "RDS"
    severity = "HIGH"
    description = "RDS database instance is not configured with AWS KMS storage encryption at rest."
    remediation = "Enable KMS encryption for the RDS instance. Note: unencrypted RDS instances require creating a snapshot, copying with encryption, and restoring."

    def evaluate(self, resource: Dict[str, Any]) -> List[RuleResult]:
        db_id = resource.get("DBInstanceIdentifier", "unknown")
        db_arn = resource.get("DBInstanceArn", f"arn:aws:rds:::db:{db_id}")
        is_encrypted = resource.get("StorageEncrypted", False)

        if not is_encrypted:
            return [
                RuleResult(
                    passed=False,
                    rule_id=self.rule_id,
                    resource_id=db_arn,
                    resource_type="rds_instance",
                    severity=self.severity,
                    title=f"RDS Instance '{db_id}' has storage encryption disabled",
                    description=f"Database {db_id} is storing data on unencrypted EBS volumes.",
                    remediation=self.remediation,
                    raw_details={"db_identifier": db_id, "storage_encrypted": False}
                )
            ]
        return []
