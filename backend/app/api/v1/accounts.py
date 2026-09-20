from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.api import deps
from app.db.session import get_db
from app.models.cloud_account import CloudAccount
from app.models.user import User
from app.schemas.cloud_account import CloudAccountCreate, CloudAccountOut

router = APIRouter()


@router.post("/", response_model=CloudAccountOut, status_code=status.HTTP_201_CREATED)
async def create_cloud_account(
    account_in: CloudAccountCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
):
    # Check if account with this email is already registered for this user
    result = await db.execute(
        select(CloudAccount).where(
            CloudAccount.user_id == current_user.id,
            CloudAccount.email == account_in.email,
        )
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"AWS Profile with email '{account_in.email}' is already connected.",
        )

    # Derive alias and account ID from email if not explicitly provided
    email_user = account_in.email.split("@")[0]
    derived_alias = account_in.account_alias or f"{email_user}-aws"
    derived_account_id = account_in.account_id or f"aws-{email_user}"

    # Basic MFA validation (if code is provided)
    is_mfa_valid = True
    if account_in.mfa_code and len(account_in.mfa_code.strip()) < 4:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid MFA code format. Must be at least 6 digits.",
        )

    account = CloudAccount(
        user_id=current_user.id,
        email=account_in.email,
        account_id=derived_account_id,
        account_alias=derived_alias,
        role_arn=account_in.role_arn,
        default_region=account_in.default_region,
        is_active=True,
        mfa_verified=is_mfa_valid,
    )
    db.add(account)
    await db.commit()
    await db.refresh(account)
    return account


@router.get("/", response_model=List[CloudAccountOut])
async def list_cloud_accounts(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
):
    result = await db.execute(
        select(CloudAccount).where(CloudAccount.user_id == current_user.id)
    )
    return result.scalars().all()


@router.get("/{account_id}", response_model=CloudAccountOut)
async def get_cloud_account(
    account_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
):
    result = await db.execute(
        select(CloudAccount).where(
            CloudAccount.id == account_id,
            CloudAccount.user_id == current_user.id,
        )
    )
    account = result.scalar_one_or_none()
    if not account:
        raise HTTPException(status_code=404, detail="Cloud Account not found")
    return account


@router.delete("/{account_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_cloud_account(
    account_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
):
    result = await db.execute(
        select(CloudAccount).where(
            CloudAccount.id == account_id,
            CloudAccount.user_id == current_user.id,
        )
    )
    account = result.scalar_one_or_none()
    if not account:
        raise HTTPException(status_code=404, detail="Cloud Account not found")

    await db.delete(account)
    await db.commit()
    return None
