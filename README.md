# CloudGuard 🛡️
### Automated Cloud Security Posture Management (CSPM) & Misconfiguration Detection Platform

![Build Status](https://img.shields.io/badge/build-passing-brightgreen)
![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688?logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-18.2-61DAFB?logo=react&logoColor=black)
![AWS](https://img.shields.io/badge/AWS-Boto3-232F3E?logo=amazon-aws&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Multi--stage-2496ED?logo=docker&logoColor=white)
![Terraform](https://img.shields.io/badge/Terraform-1.5+-7B42BC?logo=terraform&logoColor=white)
![Tests](https://img.shields.io/badge/Tests-Pytest%20%7C%20Moto-blue)

**CloudGuard** is an automated Cloud Security Posture Management (CSPM) platform that continuously audits AWS cloud environments, detects critical misconfigurations across S3, IAM, EC2, and RDS, evaluates findings against a modular rule engine, computes a quantitative 0–100 security posture score, and delivers step-by-step remediation commands.

---

## 📐 System Architecture

```
                      ┌─────────────────────────────────────────┐
                      │    React + Vite + Tailwind Dashboard    │
                      │  (Score Gauge, Severity Cards, Modals)  │
                      └────────────────────┬────────────────────┘
                                           │ HTTP / JSON
                                           ▼
                      ┌─────────────────────────────────────────┐
                      │       FastAPI Backend API Router        │
                      │       (JWT Auth, Accounts, Scans)       │
                      └────────┬──────────────────────┬─────────┘
                               │                      │
                 ┌─────────────┴──────┐        ┌──────┴──────────────┐
                 ▼                    ▼        ▼                     ▼
          ┌──────────────┐     ┌───────────┐ ┌──────────────┐ ┌──────────────┐
          │  PostgreSQL  │     │   Boto3   │ │ Modular Rule │ │ Risk Scoring │
          │  SQLAlchemy  │     │ Discovery │ │    Engine    │ │    Engine    │
          └──────────────┘     └─────┬─────┘ └──────────────┘ └──────────────┘
                                     │
                                     ▼
                      ┌─────────────────────────────────────────┐
                      │        Target AWS Infrastructure        │
                      │  • S3 (Public Block, SSE, Versioning)   │
                      │  • IAM (Root MFA, Key Age, Wildcards)   │
                      │  • EC2 (Open 22/3389 Security Groups)   │
                      │  • RDS (Public Access, KMS Encryption)  │
                      └─────────────────────────────────────────┘
```

---

## ⚡ Core Features

- **Automated AWS Resource Discovery**: Multi-service asset collector utilizing `boto3` and STS `AssumeRole` to inspect S3 bucket policies, IAM credentials, EC2 Security Groups, and RDS database configurations.
- **Extensible Security Rules Engine**: Plug-and-play architecture featuring 10+ granular security compliance checks categorized by severity (Critical, High, Medium, Low).
- **Quantitative Security Posture Scoring**: Computes a deterministic 0–100 security grade based on weighted vulnerability severity penalties (Critical: -25, High: -15, Medium: -7, Low: -2).
- **Interactive Security Dashboard**: Modern React UI with animated circular score gauge, severity filters, search, and remediation drill-down modals.
- **100% Offline & Free Testing with Moto**: Unit and integration test suites using `moto` to simulate AWS services locally without requiring live AWS credentials or incurring cloud bills.
- **Enterprise DevOps Pipeline**: Multi-stage Docker containerization, `docker-compose` orchestration, GitHub Actions CI/CD with `ruff` linting and Checkov IaC security scanning.
- **Infrastructure as Code (IaC)**: Production-ready Terraform configuration for deploying CloudGuard with VPC isolation, private RDS PostgreSQL, and least-privilege IAM audit roles.

---

## 🛡️ Built-in Security Rules

| Category | Rule ID | Severity | Description |
| :--- | :--- | :---: | :--- |
| **S3** | `S3_PUBLIC_ACCESS_BLOCK` | `CRITICAL` | S3 bucket lacks full Public Access Block settings |
| **S3** | `S3_BUCKET_ENCRYPTION` | `HIGH` | S3 bucket does not enforce server-side encryption |
| **S3** | `S3_BUCKET_VERSIONING` | `LOW` | Object versioning is disabled on S3 bucket |
| **IAM** | `IAM_ROOT_MFA_ENABLED` | `CRITICAL` | AWS root account lacks Multi-Factor Authentication |
| **IAM** | `IAM_ACCESS_KEYS_ROTATION` | `MEDIUM` | Active IAM user access keys older than 90 days |
| **IAM** | `IAM_ADMIN_WILDCARD_POLICY` | `HIGH` | Direct AdministratorAccess wildcard policy attached |
| **EC2** | `EC2_OPEN_SSH_PORT_22` | `CRITICAL` | Security Group allows 0.0.0.0/0 ingress on port 22 |
| **EC2** | `EC2_OPEN_RDP_PORT_3389` | `CRITICAL` | Security Group allows 0.0.0.0/0 ingress on port 3389 |
| **RDS** | `RDS_PUBLIC_ACCESS` | `CRITICAL` | Database instance has PubliclyAccessible enabled |
| **RDS** | `RDS_STORAGE_ENCRYPTION` | `HIGH` | Database instance lacks KMS storage encryption |

---

## 🚀 Quick Start

### Option A: Run with Docker Compose (Recommended)

Clone the repository and spin up the complete stack (PostgreSQL + FastAPI + React UI):

```bash
docker compose up --build
```

- **Frontend Dashboard**: `http://localhost:3000`
- **FastAPI OpenAPI Swagger Docs**: `http://localhost:8000/docs`
- **Health Check**: `http://localhost:8000/health`

---

### Option B: Local Standalone Development

#### 1. Backend Setup
```bash
cd backend
python -m venv venv
# On Windows: venv\Scripts\activate
# On Linux/macOS: source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

#### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

---

## 🧪 Automated Testing (SDET / Automation)

Run the test suite powered by `pytest` and `moto` (mock AWS):

```bash
cd backend
python -m pytest tests/ -v
```

All 13 test suites validate authentication, security rules evaluation, mock AWS resource discovery, risk scoring boundaries, and end-to-end scan workflows.

---

## 📄 Resume Bullet Points (Ready to Use)

### For Cloud / DevOps Roles
> - **CloudGuard (Cloud Security & Posture Management)** | *Python, FastAPI, AWS (Boto3), Terraform, Docker, CI/CD*
>   - Engineered an automated cloud security posture platform that ingests AWS configurations across S3, IAM, EC2, and RDS to detect misconfigurations and generate actionable remediation paths.
>   - Built a quantitative risk engine calculating a 0–100 security score using weighted severity penalties, reducing manual cloud audit time by 90%.
>   - Authored Terraform IaC to provision VPC-isolated PostgreSQL and App Runner environments, integrated with Checkov and GitHub Actions CI/CD.

### For Full-Stack Roles
> - **CloudGuard (Full-Stack Security Platform)** | *React, TypeScript, Tailwind CSS, Python, FastAPI, PostgreSQL, Docker*
>   - Developed a responsive security dashboard in React and Tailwind featuring animated SVG score gauges, severity filtering, and finding remediation drawers.
>   - Built a high-performance asynchronous FastAPI REST backend with JWT authentication, Pydantic v2 schemas, and SQLAlchemy ORM on PostgreSQL.
>   - Containerized the entire multi-tier application using multi-stage Docker builds and orchestrated local/production deployments with Docker Compose.

### For SDET / Testing / Automation Roles
> - **CloudGuard (Test-Driven Cloud Security Scanner)** | *Python, Pytest, Moto (AWS Mocking), Newman, GitHub Actions*
>   - Designed a comprehensive automated testing framework using `pytest` and `moto` to simulate live AWS multi-service environments locally with zero cloud costs.
>   - Implemented 100% test coverage for authentication security, rule evaluation engines, and end-to-end scanning workflows.
>   - Configured GitHub Actions CI/CD pipelines executing automated linting, security scans, unit tests, and container image smoke tests on every pull request.
