import asyncio
import os
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
import boto3
from moto import mock_aws

# Ensure test settings environment
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"
os.environ["SECRET_KEY"] = "test-secret-key-for-unit-testing-32-chars-long"
os.environ["AWS_DEFAULT_REGION"] = "us-east-1"

from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.core.security import get_password_hash, create_access_token
from app.models.user import User
from app.models.cloud_account import CloudAccount

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
)

TestAsyncSessionLocal = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def db_session():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with TestAsyncSessionLocal() as session:
        yield session

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(scope="function")
async def client(db_session):
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest_asyncio.fixture(scope="function")
async def test_user(db_session: AsyncSession) -> User:
    user = User(
        email="auditor@cloudguard.io",
        hashed_password=get_password_hash("Password123!"),
        full_name="Security Auditor",
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture(scope="function")
def user_token_headers(test_user: User) -> dict:
    token = create_access_token(subject=test_user.id)
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture(scope="function")
async def test_cloud_account(db_session: AsyncSession, test_user: User) -> CloudAccount:
    account = CloudAccount(
        user_id=test_user.id,
        email="admin@production.aws",
        account_id="123456789012",
        account_alias="Production-AWS",
        default_region="us-east-1",
        is_active=True,
    )
    db_session.add(account)
    await db_session.commit()
    await db_session.refresh(account)
    return account


@pytest.fixture(scope="function")
def aws_mock_environment():
    """Sets up a moto mock AWS environment with misconfigured and secure resources for testing."""
    with mock_aws():
        # 1. S3 Mocking: one vulnerable public unencrypted bucket, one secure bucket
        s3 = boto3.client("s3", region_name="us-east-1")
        s3.create_bucket(Bucket="vulnerable-data-bucket")
        # Secure bucket with encryption and public access block
        s3.create_bucket(Bucket="secured-backup-bucket")
        s3.put_public_access_block(
            Bucket="secured-backup-bucket",
            PublicAccessBlockConfiguration={
                "BlockPublicAcls": True,
                "IgnorePublicAcls": True,
                "BlockPublicPolicy": True,
                "RestrictPublicBuckets": True,
            },
        )
        s3.put_bucket_encryption(
            Bucket="secured-backup-bucket",
            ServerSideEncryptionConfiguration={
                "Rules": [{"ApplyServerSideEncryptionByDefault": {"SSEAlgorithm": "AES256"}}]
            },
        )
        s3.put_bucket_versioning(
            Bucket="secured-backup-bucket",
            VersioningConfiguration={"Status": "Enabled"},
        )

        # 2. EC2 Mocking: one Security Group with port 22 open to 0.0.0.0/0
        ec2 = boto3.client("ec2", region_name="us-east-1")
        sg = ec2.create_security_group(
            GroupName="vulnerable-web-sg",
            Description="Vulnerable Web Security Group"
        )
        sg_id = sg["GroupId"]
        ec2.authorize_security_group_ingress(
            GroupId=sg_id,
            IpPermissions=[
                {
                    "IpProtocol": "tcp",
                    "FromPort": 22,
                    "ToPort": 22,
                    "IpRanges": [{"CidrIp": "0.0.0.0/0"}],
                }
            ],
        )

        # 3. RDS Mocking: one publicly accessible RDS database
        rds = boto3.client("rds", region_name="us-east-1")
        rds.create_db_instance(
            DBInstanceIdentifier="production-database",
            AllocatedStorage=20,
            DBInstanceClass="db.t3.micro",
            Engine="postgres",
            MasterUsername="admin",
            MasterUserPassword="SecurePassword123!",
            PubliclyAccessible=True,
            StorageEncrypted=False,
        )

        yield {
            "s3": s3,
            "ec2": ec2,
            "rds": rds,
        }
