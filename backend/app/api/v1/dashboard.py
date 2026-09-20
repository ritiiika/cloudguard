from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select

from app.api import deps
from app.db.session import get_db
from app.models.cloud_account import CloudAccount
from app.models.finding import Finding
from app.models.scan import Scan
from app.models.user import User
from app.schemas.dashboard import DashboardOverview, SeverityCount
from app.schemas.finding import FindingOut

router = APIRouter()


@router.get("/overview", response_model=DashboardOverview)
async def get_dashboard_overview(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
):
    # Total accounts
    res_acc = await db.execute(
        select(func.count(CloudAccount.id)).where(CloudAccount.user_id == current_user.id)
    )
    total_accounts = res_acc.scalar_one() or 0

    # Total scans and average score across latest completed scan per account
    res_scans = await db.execute(
        select(Scan)
        .join(CloudAccount, Scan.account_id == CloudAccount.id)
        .where(CloudAccount.user_id == current_user.id, Scan.status == "COMPLETED")
        .order_by(Scan.created_at.desc())
    )
    completed_scans = res_scans.scalars().all()
    total_scans = len(completed_scans)

    avg_score = 100
    total_resources = 0
    if completed_scans:
        avg_score = int(sum(s.security_score for s in completed_scans) / len(completed_scans))
        total_resources = sum(s.total_resources_scanned for s in completed_scans)

    # Severity counts across all active findings for the user
    severity_breakdown = SeverityCount()
    for sev in ["CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"]:
        res_sev = await db.execute(
            select(func.count(Finding.id))
            .join(Scan, Finding.scan_id == Scan.id)
            .join(CloudAccount, Scan.account_id == CloudAccount.id)
            .where(CloudAccount.user_id == current_user.id, Finding.severity == sev)
        )
        count = res_sev.scalar_one() or 0
        setattr(severity_breakdown, sev.lower(), count)

    # Top critical/recent findings
    res_top = await db.execute(
        select(Finding)
        .join(Scan, Finding.scan_id == Scan.id)
        .join(CloudAccount, Scan.account_id == CloudAccount.id)
        .where(CloudAccount.user_id == current_user.id)
        .order_by(
            # Order by critical first, then recent
            Finding.created_at.desc()
        )
        .limit(6)
    )
    top_findings = res_top.scalars().all()

    return DashboardOverview(
        total_accounts=total_accounts,
        total_scans=total_scans,
        average_security_score=avg_score,
        severity_breakdown=severity_breakdown,
        top_findings=top_findings,
        scanned_resources_count=total_resources,
    )
