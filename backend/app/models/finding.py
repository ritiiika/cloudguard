import json
from datetime import UTC, datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.db.base import Base


class Finding(Base):
    __tablename__ = "findings"

    id = Column(Integer, primary_key=True, index=True)
    scan_id = Column(Integer, ForeignKey("scans.id", ondelete="CASCADE"), nullable=False)
    rule_id = Column(String(64), index=True, nullable=False)
    resource_id = Column(String(255), index=True, nullable=False)
    resource_type = Column(String(64), nullable=False)  # s3_bucket, iam_user, ec2_instance, etc.
    severity = Column(String(20), index=True, nullable=False)  # CRITICAL, HIGH, MEDIUM, LOW, INFO
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    remediation = Column(Text, nullable=False)
    raw_details_json = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC))

    scan = relationship("Scan", back_populates="findings")

    @property
    def raw_details(self):
        if self.raw_details_json:
            try:
                return json.loads(self.raw_details_json)
            except Exception:
                return {}
        return {}

    @raw_details.setter
    def raw_details(self, value):
        if value is not None:
            self.raw_details_json = json.dumps(value)
        else:
            self.raw_details_json = None
