import logging
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.cloud_account import CloudAccount
from app.models.scan import Scan
from app.models.finding import Finding
from app.services.aws_client import AWSClientManager
from app.services.aws_discovery import AWSResourceDiscovery
from app.rules.registry import rule_registry
from app.services.risk_engine import RiskEngine

logger = logging.getLogger(__name__)


class ScannerService:
    @staticmethod
    async def execute_scan(scan_id: int, db: AsyncSession) -> Optional[Scan]:
        # 1. Fetch scan and associated account
        result = await db.execute(select(Scan).where(Scan.id == scan_id))
        scan = result.scalar_one_or_none()
        if not scan:
            logger.error(f"Scan {scan_id} not found")
            return None

        result_acc = await db.execute(select(CloudAccount).where(CloudAccount.id == scan.account_id))
        account = result_acc.scalar_one_or_none()
        if not account:
            scan.status = "FAILED"
            scan.error_message = f"Associated Cloud Account {scan.account_id} not found"
            await db.commit()
            return scan

        scan.status = "RUNNING"
        await db.commit()

        try:
            # 2. Get AWS Boto3 Session
            session = AWSClientManager.get_session(account)

            # 3. Discover AWS Resources
            discovery = AWSResourceDiscovery(session)
            inventory = discovery.discover_all()

            # 4. Evaluate Security Rules
            findings_results = rule_registry.evaluate_inventory(inventory)

            # 5. Compute Risk & Posture Score
            risk_summary = RiskEngine.calculate_score(findings_results)

            # 6. Persist Findings
            for fr in findings_results:
                finding = Finding(
                    scan_id=scan.id,
                    rule_id=fr.rule_id,
                    resource_id=fr.resource_id,
                    resource_type=fr.resource_type,
                    severity=fr.severity,
                    title=fr.title,
                    description=fr.description,
                    remediation=fr.remediation,
                    raw_details=fr.raw_details or {},
                )
                db.add(finding)

            # 7. Update Scan Record
            scan.status = "COMPLETED"
            scan.security_score = risk_summary["score"]
            scan.critical_count = risk_summary["critical_count"]
            scan.high_count = risk_summary["high_count"]
            scan.medium_count = risk_summary["medium_count"]
            scan.low_count = risk_summary["low_count"]
            scan.total_resources_scanned = inventory.get("total_resources_scanned", 0)
            scan.completed_at = datetime.now(timezone.utc)
            scan.error_message = None

            await db.commit()
            await db.refresh(scan)
            return scan

        except Exception:
                logger.exception("Scan %s failed", scan_id)
            
                scan.status = "FAILED"
                scan.error_message = str(e)
                scan.completed_at = datetime.now(timezone.utc)
                await db.commit()
                return scan
