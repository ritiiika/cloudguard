from datetime import datetime, timezone, timedelta
from app.rules.s3.public_access import S3PublicAccessBlockRule
from app.rules.s3.encryption import S3BucketEncryptionRule
from app.rules.s3.versioning import S3BucketVersioningRule
from app.rules.iam.root_mfa import IAMRootMFAEnabledRule
from app.rules.iam.access_keys import IAMInactiveAccessKeysRule
from app.rules.iam.wildcard import IAMWildcardPolicyRule
from app.rules.ec2.open_ssh import EC2OpenSSHRule
from app.rules.ec2.open_rdp import EC2OpenRDPRule
from app.rules.rds.public_db import RDSPublicAccessRule
from app.rules.rds.encryption import RDSEncryptionRule
from app.services.risk_engine import RiskEngine


def test_s3_public_access_rule():
    rule = S3PublicAccessBlockRule()

    # Vulnerable bucket
    vuln_bucket = {
        "name": "public-files",
        "public_access_block": {"BlockPublicAcls": False, "BlockPublicPolicy": False},
    }
    findings = rule.evaluate(vuln_bucket)
    assert len(findings) == 1
    assert findings[0].severity == "CRITICAL"
    assert "public" in findings[0].title.lower()

    # Secured bucket
    sec_bucket = {
        "name": "private-files",
        "public_access_block": {
            "BlockPublicAcls": True,
            "IgnorePublicAcls": True,
            "BlockPublicPolicy": True,
            "RestrictPublicBuckets": True,
        },
    }
    assert len(rule.evaluate(sec_bucket)) == 0


def test_s3_encryption_rule():
    rule = S3BucketEncryptionRule()

    # Unencrypted
    assert len(rule.evaluate({"name": "unenc", "encryption": None})) == 1

    # Encrypted
    assert (
        len(
            rule.evaluate(
                {
                    "name": "enc",
                    "encryption": {"Rules": [{"ApplyServerSideEncryptionByDefault": {}}]},
                }
            )
        )
        == 0
    )


def test_iam_root_mfa_rule():
    rule = IAMRootMFAEnabledRule()

    # Missing MFA
    findings = rule.evaluate({"account_mfa_enabled": False})
    assert len(findings) == 1
    assert findings[0].severity == "CRITICAL"

    # MFA Enabled
    assert len(rule.evaluate({"account_mfa_enabled": True})) == 0


def test_iam_access_keys_rule():
    rule = IAMInactiveAccessKeysRule()

    old_date = datetime.now(timezone.utc) - timedelta(days=120)
    user_with_old_key = {
        "username": "developer",
        "access_keys": [{"AccessKeyId": "AKIA123", "Status": "Active", "CreateDate": old_date}],
    }
    findings = rule.evaluate(user_with_old_key)
    assert len(findings) == 1
    assert findings[0].severity == "MEDIUM"


def test_ec2_open_ssh_rule():
    rule = EC2OpenSSHRule()

    # Open SSH
    open_sg = {
        "GroupId": "sg-12345",
        "GroupName": "open-ssh-sg",
        "IpPermissions": [
            {
                "IpProtocol": "tcp",
                "FromPort": 22,
                "ToPort": 22,
                "IpRanges": [{"CidrIp": "0.0.0.0/0"}],
            }
        ],
    }
    findings = rule.evaluate(open_sg)
    assert len(findings) == 1
    assert findings[0].severity == "CRITICAL"

    # Closed SG
    closed_sg = {
        "GroupId": "sg-99999",
        "GroupName": "internal-sg",
        "IpPermissions": [
            {
                "IpProtocol": "tcp",
                "FromPort": 22,
                "ToPort": 22,
                "IpRanges": [{"CidrIp": "10.0.0.0/16"}],
            }
        ],
    }
    assert len(rule.evaluate(closed_sg)) == 0


def test_rds_public_access_rule():
    rule = RDSPublicAccessRule()

    # Public RDS
    findings = rule.evaluate({"DBInstanceIdentifier": "db-1", "PubliclyAccessible": True})
    assert len(findings) == 1
    assert findings[0].severity == "CRITICAL"

    # Private RDS
    assert len(rule.evaluate({"DBInstanceIdentifier": "db-2", "PubliclyAccessible": False})) == 0


def test_risk_engine_calculation():
    rule = S3PublicAccessBlockRule()
    finding = rule.evaluate({"name": "bucket", "public_access_block": {}})[0]

    # 1 critical finding -> 100 - 25 = 75 score (Grade B)
    result = RiskEngine.calculate_score([finding])
    assert result["score"] == 75
    assert result["grade"] == "B"
    assert result["critical_count"] == 1
    assert result["total_findings"] == 1
