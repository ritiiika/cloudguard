import boto3
from typing import Optional
from app.core.config import settings
from app.models.cloud_account import CloudAccount


class AWSClientManager:
    """Manages boto3 sessions and client creation with support for AssumeRole and direct credentials."""

    @staticmethod
    def get_session(account: Optional[CloudAccount] = None, region: Optional[str] = None) -> boto3.Session:
        target_region = region or (account.default_region if account else settings.AWS_REGION)

        # Base kwargs for boto3 Session
        session_kwargs = {"region_name": target_region}

        if settings.AWS_ACCESS_KEY_ID and settings.AWS_SECRET_ACCESS_KEY:
            session_kwargs["aws_access_key_id"] = settings.AWS_ACCESS_KEY_ID
            session_kwargs["aws_secret_access_key"] = settings.AWS_SECRET_ACCESS_KEY
            if settings.AWS_SESSION_TOKEN:
                session_kwargs["aws_session_token"] = settings.AWS_SESSION_TOKEN

        base_session = boto3.Session(**session_kwargs)

        # If account has an IAM Role ARN to assume, perform STS AssumeRole
        if account and account.role_arn:
            try:
                sts_client = base_session.client("sts")
                assumed_role = sts_client.assume_role(
                    RoleArn=account.role_arn,
                    RoleSessionName=f"CloudGuardScan-{account.account_id}"
                )
                credentials = assumed_role["Credentials"]
                return boto3.Session(
                    aws_access_key_id=credentials["AccessKeyId"],
                    aws_secret_access_key=credentials["SecretAccessKey"],
                    aws_session_token=credentials["SessionToken"],
                    region_name=target_region,
                )
            except Exception as e:
                # Log and fallback to base session for mock/test environments
                print(f"[AWSClientManager] Warning: Failed to assume role {account.role_arn}: {e}")
                return base_session

        return base_session
