from app.api.v1 import accounts, auth, dashboard, findings, scans
from fastapi import APIRouter

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(accounts.router, prefix="/accounts", tags=["Cloud Accounts"])
api_router.include_router(scans.router, prefix="/scans", tags=["Security Scans"])
api_router.include_router(findings.router, prefix="/findings", tags=["Findings"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])
