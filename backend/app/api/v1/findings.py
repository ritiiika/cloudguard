from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.api import deps
from app.db.session import get_db
from app.models.cloud_account import CloudAccount
from app.models.finding import Finding
from app.models.scan import Scan
from app.models.user import User
from app.schemas.finding import FindingOut

router = APIRouter()


@router.get("/", response_model=List[FindingOut])
async def list_all_findings(
    severity: Optional[str] = Query(None, description="CRITICAL, HIGH, MEDIUM, LOW, INFO"),
    resource_type: Optional[str] = Query(None, description="s3_bucket, iam_user, security_group, rds_instance"),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
):
    query = (
        select(Finding)
        .join(Scan, Finding.scan_id == Scan.id)
        .join(CloudAccount, Scan.account_id == CloudAccount.id)
        .where(CloudAccount.user_id == current_user.id)
        .order_by(Finding.created_at.desc())
        .limit(limit)
    )

    if severity:
        query = query.where(Finding.severity == severity.upper())
    if resource_type:
        query = query.where(Finding.resource_type == resource_type)

    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{finding_id}", response_model=FindingOut)
async def get_finding(
    finding_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
):
    result = await db.execute(
        select(Finding)
        .join(Scan, Finding.scan_id == Scan.id)
        .join(CloudAccount, Scan.account_id == CloudAccount.id)
        .where(Finding.id == finding_id, CloudAccount.user_id == current_user.id)
    )
    finding = result.scalar_one_or_none()
    if not finding:
        raise HTTPException(status_code=404, detail="Finding not found")
    return finding
