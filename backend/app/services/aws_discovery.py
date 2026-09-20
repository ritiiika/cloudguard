import logging
from typing import Any, Dict, List
import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)


class AWSResourceDiscovery:
    """Discovers AWS resources across S3, IAM, EC2, and RDS for security compliance evaluation."""

    def __init__(self, session: boto3.Session):
        self.session = session

    def discover_s3_buckets(self) -> List[Dict[str, Any]]:
        s3 = self.session.client("s3")
        buckets_data = []

        try:
            response = s3.list_buckets()
            raw_buckets = response.get("Buckets", [])
        except ClientError as e:
            logger.warning(f"Failed to list S3 buckets: {e}")
            return []

        for bucket in raw_buckets:
            name = bucket["Name"]
            bucket_info = {
                "name": name,
                "arn": f"arn:aws:s3:::{name}",
                "creation_date": bucket.get("CreationDate"),
                "public_access_block": None,
                "encryption": None,
                "versioning": "Disabled",
                "grants": [],
            }

            # 1. Public Access Block
            try:
                pab = s3.get_public_access_block(Bucket=name)
                bucket_info["public_access_block"] = pab.get("PublicAccessBlockConfiguration", {})
            except ClientError as e:
                bucket_info["public_access_block"] = {
                    "BlockPublicAcls": False,
                    "IgnorePublicAcls": False,
                    "BlockPublicPolicy": False,
                    "RestrictPublicBuckets": False,
                }

            # 2. Server-side Encryption
            try:
                enc = s3.get_bucket_encryption(Bucket=name)
                bucket_info["encryption"] = enc.get("ServerSideEncryptionConfiguration", {})
            except ClientError:
                bucket_info["encryption"] = None

            # 3. Versioning
            try:
                vers = s3.get_bucket_versioning(Bucket=name)
                bucket_info["versioning"] = vers.get("Status", "Disabled")
            except ClientError:
                bucket_info["versioning"] = "Disabled"

            # 4. ACL Grants
            try:
                acl = s3.get_bucket_acl(Bucket=name)
                bucket_info["grants"] = acl.get("Grants", [])
            except ClientError:
                bucket_info["grants"] = []

            buckets_data.append(bucket_info)

        return buckets_data

    def discover_iam(self) -> Dict[str, Any]:
        iam = self.session.client("iam")
        iam_data = {
            "account_mfa_enabled": False,
            "users": [],
            "roles": [],
        }

        # 1. Account Summary (Root MFA)
        try:
            summary = iam.get_account_summary()
            summary_map = summary.get("SummaryMap", {})
            # AccountMFAEnabled == 1 indicates Root account has MFA enabled
            iam_data["account_mfa_enabled"] = summary_map.get("AccountMFAEnabled", 0) == 1
        except ClientError as e:
            logger.warning(f"Failed to get IAM account summary: {e}")

        # 2. IAM Users
        try:
            users_resp = iam.list_users()
            for user in users_resp.get("Users", []):
                username = user["UserName"]
                user_info = {
                    "username": username,
                    "arn": user["Arn"],
                    "access_keys": [],
                    "attached_policies": [],
                    "inline_policies": [],
                }

                # List Access Keys
                try:
                    keys_resp = iam.list_access_keys(UserName=username)
                    user_info["access_keys"] = keys_resp.get("AccessKeyMetadata", [])
                except ClientError:
                    pass

                # List Attached Policies
                try:
                    policies_resp = iam.list_attached_user_policies(UserName=username)
                    user_info["attached_policies"] = policies_resp.get("AttachedPolicies", [])
                except ClientError:
                    pass

                iam_data["users"].append(user_info)
        except ClientError as e:
            logger.warning(f"Failed to list IAM users: {e}")

        return iam_data

    def discover_ec2_and_security_groups(self) -> Dict[str, Any]:
        ec2 = self.session.client("ec2")
        data = {
            "security_groups": [],
            "instances": [],
        }

        # 1. Security Groups
        try:
            sg_resp = ec2.describe_security_groups()
            data["security_groups"] = sg_resp.get("SecurityGroups", [])
        except ClientError as e:
            logger.warning(f"Failed to describe security groups: {e}")

        # 2. EC2 Instances
        try:
            inst_resp = ec2.describe_instances()
            instances = []
            for res in inst_resp.get("Reservations", []):
                for inst in res.get("Instances", []):
                    instances.append({
                        "instance_id": inst.get("InstanceId"),
                        "instance_type": inst.get("InstanceType"),
                        "state": inst.get("State", {}).get("Name"),
                        "public_ip": inst.get("PublicIpAddress"),
                        "private_ip": inst.get("PrivateIpAddress"),
                        "security_groups": inst.get("SecurityGroups", []),
                    })
            data["instances"] = instances
        except ClientError as e:
            logger.warning(f"Failed to describe EC2 instances: {e}")

        return data

    def discover_rds(self) -> List[Dict[str, Any]]:
        rds = self.session.client("rds")
        try:
            response = rds.describe_db_instances()
            return response.get("DBInstances", [])
        except ClientError as e:
            logger.warning(f"Failed to describe RDS instances: {e}")
            return []

    def discover_all(self) -> Dict[str, Any]:
        """Discovers all supported AWS resources in the target environment."""
        s3_resources = self.discover_s3_buckets()
        iam_resources = self.discover_iam()
        ec2_resources = self.discover_ec2_and_security_groups()
        rds_resources = self.discover_rds()

        total_count = (
            len(s3_resources)
            + len(iam_resources.get("users", []))
            + len(ec2_resources.get("security_groups", []))
            + len(ec2_resources.get("instances", []))
            + len(rds_resources)
        )

        return {
            "s3": s3_resources,
            "iam": iam_resources,
            "security_groups": ec2_resources.get("security_groups", []),
            "ec2_instances": ec2_resources.get("instances", []),
            "rds": rds_resources,
            "total_resources_scanned": total_count,
        }
