# RetailPulse Data Platform

RetailPulse is an end-to-end data engineering project that simulates an
omnichannel retail data platform.

The platform is designed locally first and progressively migrated to AWS.

## Business problem

RetailPulse centralizes transactional, behavioral, payment, inventory and
delivery data to provide reliable and observable analytics.

The platform supports:

- batch ingestion;
- event streaming;
- Bronze, Silver and Gold data layers;
- distributed processing;
- dimensional modeling;
- data quality;
- orchestration;
- observability;
- CI/CD;
- Infrastructure as Code;
- controlled AWS deployments.

## Target architecture

The local platform will progressively include:

- Python;
- PostgreSQL;
- Apache Kafka;
- Apache Spark;
- Apache Airflow;
- MinIO;
- dbt;
- Prometheus;
- Grafana;
- Docker Compose.

The AWS target will evaluate and use:

- Amazon S3;
- Amazon EMR Serverless;
- Amazon MSK Serverless;
- Amazon Redshift Serverless;
- Amazon Athena;
- AWS Glue Data Catalog;
- Amazon CloudWatch;
- AWS IAM;
- Terraform;
- GitHub Actions with OIDC.

## Project status

The project is currently in Phase 1: repository and engineering standards.

## Roadmap

1. Architecture and business definition
2. Repository and engineering standards
3. Data contracts (contrats data)
4. Data generation
5. Local Docker platform
6. Batch ingestion
7. Data Lake
8. Spark batch processing
9. Data Warehouse
10. dbt
11. Airflow
12. Kafka
13. Spark Structured Streaming
14. Data Quality
15. Observability
16. CI/CD
17. Terraform and AWS
18. Production readiness

## Local development

Create and activate a Python virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
