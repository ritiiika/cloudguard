from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict
from app.schemas.finding import FindingOut


class ScanCreate(BaseModel):
    account_id: int


class ScanOut(BaseModel):
    id: int
    account_id: int
    status: str
    security_score: int
    critical_count: int
    high_count: int
    medium_count: int
    low_count: int
    total_resources_scanned: int
    error_message: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class ScanDetail(ScanOut):
    findings: List[FindingOut] = []
