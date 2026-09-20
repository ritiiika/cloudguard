from typing import List
from pydantic import BaseModel
from app.schemas.finding import FindingOut


class SeverityCount(BaseModel):
    critical: int = 0
    high: int = 0
    medium: int = 0
    low: int = 0
    info: int = 0


class DashboardOverview(BaseModel):
    total_accounts: int = 0
    total_scans: int = 0
    average_security_score: int = 100
    severity_breakdown: SeverityCount
    top_findings: List[FindingOut] = []
    scanned_resources_count: int = 0
