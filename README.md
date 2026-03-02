# Change Management Compliance Checker (CI/CD)

Audit-analytics project demonstrating repeatable testing of ITGC-aligned change management controls using **Python + SQL (DuckDB)**.

## What it does
Ingests deployment and change-ticket data and runs automated tests to identify control exceptions and produce audit-ready outputs.

## Control tests
- Missing change ticket for production deployments
- Missing approval evidence
- Approval timestamp after production deployment
- Non-approved tickets deployed to production
- Missing testing evidence

## How to run (local)
```bash
python -m venv .venv
source .venv/bin/activate
pip install duckdb pandas numpy faker
python generate_data.py
python run_checks.py