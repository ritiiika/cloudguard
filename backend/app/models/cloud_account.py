from datetime import UTC, datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.db.base import Base


class CloudAccount(Base):
    __tablename__ = "cloud_accounts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    email = Column(String(255), index=True, nullable=True)
    account_id = Column(String(64), index=True, nullable=True)
    account_alias = Column(String(100), nullable=True)
    role_arn = Column(String(255), nullable=True)
    default_region = Column(String(32), default="us-east-1", nullable=False)
    is_active = Column(Boolean, default=True)
    mfa_verified = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC))

    owner = relationship("User", back_populates="accounts")
    scans = relationship("Scan", back_populates="account", cascade="all, delete-orphan")
