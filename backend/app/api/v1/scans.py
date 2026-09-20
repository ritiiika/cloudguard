from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.api import deps
from app.db.session import get_db
from app.models.cloud_account import CloudAccount
from app.models.finding import Finding
from app.models.scan import Scan
from app.models.user import User
from app.schemas.finding import FindingOut
from app.schemas.scan import ScanCreate, ScanOut
from app.services.scanner import ScannerService

router = APIRouter()


@router.post("/", response_model=ScanOut, status_code=status.HTTP_201_CREATED)
async def trigger_scan(
    scan_in: ScanCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
):
    # Verify account ownership
    result_acc = await db.execute(
        select(CloudAccount).where(
            CloudAccount.id == scan_in.account_id,
            CloudAccount.user_id == current_user.id,
        )
    )
    account = result_acc.scalar_one_or_none()
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cloud Account not found or unauthorized",
        )

    # Create scan record in PENDING state
    scan = Scan(
        account_id=account.id,
        status="PENDING",
        security_score=100,
    )
    db.add(scan)
    await db.commit()
    await db.refresh(scan)

    # Execute scanner workflow
    completed_scan = await ScannerService.execute_scan(scan.id, db)
    return completed_scan or scan


@router.get("/", response_model=List[ScanOut])
async def list_scans(
    account_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
):
    query = (
        select(Scan)
        .join(CloudAccount, Scan.account_id == CloudAccount.id)
        .where(CloudAccount.user_id == current_user.id)
        .order_by(Scan.created_at.desc())
    )
    if account_id:
        query = query.where(Scan.account_id == account_id)

    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{scan_id}", response_model=ScanOut)
async def get_scan(
    scan_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
):
    result = await db.execute(
        select(Scan)
        .join(CloudAccount, Scan.account_id == CloudAccount.id)
        .where(Scan.id == scan_id, CloudAccount.user_id == current_user.id)
    )
    scan = result.scalar_one_or_none()
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    return scan


@router.get("/{scan_id}/findings", response_model=List[FindingOut])
async def get_scan_findings(
    scan_id: int,
    severity: Optional[str] = Query(None, description="Filter by severity: CRITICAL, HIGH, MEDIUM, LOW, INFO"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
):
    # Verify scan access
    result = await db.execute(
        select(Scan)
        .join(CloudAccount, Scan.account_id == CloudAccount.id)
        .where(Scan.id == scan_id, CloudAccount.user_id == current_user.id)
    )
    scan = result.scalar_one_or_none()
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")

    query = select(Finding).where(Finding.scan_id == scan_id)
    if severity:
        query = query.where(Finding.severity == severity.upper())

    findings_result = await db.execute(query)
    return findings_result.scalars().all()
