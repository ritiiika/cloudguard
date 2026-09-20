import pytest
from app.models.cloud_account import CloudAccount
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_full_scan_workflow(
    client: AsyncClient,
    user_token_headers: dict,
    test_cloud_account: CloudAccount,
    aws_mock_environment,
):
    # 1. Trigger security scan
    response = await client.post(
        "/api/v1/scans/",
        json={"account_id": test_cloud_account.id},
        headers=user_token_headers,
    )
    assert response.status_code == 201
    scan_data = response.json()
    assert scan_data["status"] == "COMPLETED"
    scan_id = scan_data["id"]

    # Posture score should be penalized because vulnerable-data-bucket, vulnerable-web-sg, production-database exist in mock
    assert scan_data["security_score"] < 100
    assert scan_data["critical_count"] >= 1

    # 2. Query scan findings
    findings_resp = await client.get(
        f"/api/v1/scans/{scan_id}/findings",
        headers=user_token_headers,
    )
    assert findings_resp.status_code == 200
    findings = findings_resp.json()
    assert len(findings) > 0

    rule_ids = [f["rule_id"] for f in findings]
    assert "S3_PUBLIC_ACCESS_BLOCK" in rule_ids or "EC2_OPEN_SSH_PORT_22" in rule_ids or "RDS_PUBLIC_ACCESS" in rule_ids

    # 3. Query Dashboard Overview
    dash_resp = await client.get(
        "/api/v1/dashboard/overview",
        headers=user_token_headers,
    )
    assert dash_resp.status_code == 200
    dash_data = dash_resp.json()
    assert dash_data["total_accounts"] == 1
    assert dash_data["total_scans"] == 1
    assert dash_data["severity_breakdown"]["critical"] >= 1
