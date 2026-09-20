from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class FindingBase(BaseModel):
    rule_id: str
    resource_id: str
    resource_type: str
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW, INFO
    title: str
    description: str
    remediation: str


class FindingOut(FindingBase):
    id: int
    scan_id: int
    raw_details: dict[str, Any] | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
