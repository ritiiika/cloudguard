from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class CloudAccountBase(BaseModel):
    email: EmailStr = Field(..., description="AWS Root or IAM User Email address")
    default_region: str = Field("us-east-1", description="Default AWS region to scan")
    account_id: Optional[str] = Field(None, description="Optional AWS account ID")
    account_alias: Optional[str] = Field(None, description="Optional account alias")
    role_arn: Optional[str] = Field(None, description="IAM Role ARN to assume (optional)")


class CloudAccountCreate(CloudAccountBase):
    password: Optional[str] = Field(None, description="AWS Account Password (optional)")
    mfa_code: Optional[str] = Field(None, description="6-digit MFA TOTP code", min_length=4, max_length=8)


class CloudAccountOut(CloudAccountBase):
    id: int
    user_id: int
    email: Optional[str] = None
    account_id: Optional[str] = None
    account_alias: Optional[str] = None
    is_active: bool
    mfa_verified: bool = True
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
