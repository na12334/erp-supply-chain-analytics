# ERP Sales & Supply Chain Analytics Platform

> **Cloud-hosted analytics platform built on Oracle Cloud Infrastructure (OCI)**  
> Analyzing 180,000+ real supply chain transactions using Oracle Autonomous Database, SQL, Power BI, and Terraform.

---

## Project Overview

This project simulates a real-world ERP (Enterprise Resource Planning) analytics environment — the kind used by companies running Oracle or SAP. It covers the full data pipeline: from raw dataset ingestion and cloud database provisioning, through SQL-based analytics, to live Power BI dashboards and infrastructure-as-code.

**Dataset**: [DataCo Smart Supply Chain for Big Data Analysis](https://www.kaggle.com/datasets/shashwatwork/dataco-smart-supply-chain-for-big-data-analysis) — 180,519 transactions across 5 global markets (Pacific Asia, USCA, Europe, Africa, LATAM), spanning January 2015 to January 2018.

---

## Architecture

```
Raw CSV (Kaggle)
      │
      ▼
Python / pandas (data cleaning + normalization)
      │
      ▼
Oracle Autonomous Database (OCI) ◄──── Terraform (IaC)
      │
      ├── SQL Analytics (10 business queries)
      │
      └── Power BI Desktop (live ODBC connection)
            │
            └── Interactive Dashboards
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Cloud Platform | Oracle Cloud Infrastructure (OCI) |
| Database | Oracle Autonomous Database 19c (Always Free) |
| Data Transformation | Python (pandas) |
| Query Language | Oracle SQL |
| Business Intelligence | Microsoft Power BI Desktop |
| Infrastructure as Code | Terraform (OCI Provider) |
| Connectivity | Oracle Instant Client, ODBC, mTLS Wallet |
| Data Source | DataCo Smart Supply Chain (Kaggle) |

---

## Database Schema

4-table normalized relational schema:

```
CUSTOMERS (20,652 rows)
    └──> ORDERS (65,752 rows)
              └──> ORDER_ITEMS (180,519 rows)
                        └──> PRODUCTS (118 rows)
```

**Key design decisions:**
- Primary keys, foreign key constraints, and CHECK constraints for data quality
- Schema normalized from a raw 53-column flat file
- Follows standard ERP data modeling patterns

---

## Repository Structure

```
erp-supply-chain-analytics-oci/
├── sql/
│   ├── 01_create_tables.sql       # Oracle schema: 4 tables with constraints
│   └── analytics_queries.sql      # 10 business analytics queries
├── terraform/
│   ├── provider.tf                # OCI provider configuration
│   ├── variables.tf               # Input variables (credentials, names)
│   ├── main.tf                    # Resources: compartment + Autonomous DB
│   └── .gitignore                 # Excludes secrets and state files
└── README.md
```

---

## SQL Analytics (10 Queries)

| # | Query | Business Question |
|---|---|---|
| 1 | Top Categories by Revenue | Which product categories drive the most sales? |
| 2 | Late Delivery by Shipping Mode | Which shipping mode misses deadlines most? |
| 3 | Top Customers by Lifetime Spend | Who are our highest-value customers? |
| 4 | Monthly Order Volume Trend | Are orders growing? What seasonality exists? |
| 5 | Profit & Revenue by Market | Which global market is most profitable? |
| 6 | Customer Segment Analysis | Do Corporate customers outspend Consumers? |
| 7 | Best-Selling Products by Quantity | Which products sell the most units? |
| 8 | Order Status Distribution | What % of orders complete vs. cancel? |
| 9 | Delivery Performance by Region | Which regions have the worst delays? |
| 10 | High-Value Orders at Late Risk | Which urgent orders need intervention? |

---

## Power BI Dashboard

Live connection established between Power BI Desktop and Oracle Autonomous Database via ODBC (Oracle Instant Client + mTLS wallet authentication).

**Dashboards built:**
- Sales by product category (bar chart)
- Late delivery rate by shipping mode (column chart)
- Monthly order volume trend 2015–2018 (line chart)
- Profit by global market (chart)
- KPI cards: Total Revenue, Total Orders, Total Customers

---

## Infrastructure as Code (Terraform)

Terraform files define the entire OCI setup as code:
- `oci_identity_compartment` — dedicated project compartment
- `oci_database_autonomous_database` — Always Free Autonomous DB

```bash
terraform init    # Download OCI provider
terraform plan    # Preview what will be created
terraform apply   # Create infrastructure
```

> **Note**: A `terraform.tfvars` file (not committed) is required with real OCI credentials. See `variables.tf` for required inputs.

---

## Key Findings from the Data

- **Fishing** is the top revenue category at ~$6.9M, nearly 1.6x the next category (Cleats)
- **~55%** of orders carry late delivery risk — a significant operational issue
- **Standard Class** shipping shows the highest average delivery delays
- **LATAM** market generates the highest order volume; profit margins vary significantly by region
- **Consumer segment** accounts for the largest share of orders, but Corporate customers have higher average order values

---

## Setup (to run this yourself)

### Prerequisites
- OCI account (free tier available)
- Terraform installed
- Oracle Instant Client (64-bit) + ODBC package
- Power BI Desktop (Windows)
- Python 3.x with pandas

### Steps
1. Clone this repository
2. Create `terraform/terraform.tfvars` with your OCI credentials (see `variables.tf` for required fields — never commit this file)
3. Run `terraform init && terraform plan && terraform apply` to provision infrastructure
4. Run the Python data cleaning script to generate normalized CSVs from the raw DataCo dataset
5. Load CSVs into Oracle using OCI Database Actions → Data Load
6. Run `sql/01_create_tables.sql` in Oracle SQL Worksheet
7. Run `sql/analytics_queries.sql` to explore the data
8. Connect Power BI via Get Data → ODBC → select your DSN

---

## Skills Demonstrated

`Oracle Cloud Infrastructure` `Autonomous Database` `IAM & Compartments` `Relational Schema Design` `Data Normalization` `ETL Pipeline` `Python (pandas)` `Oracle SQL` `Power BI` `ODBC Configuration` `Oracle Wallet / TLS` `Terraform` `Infrastructure as Code` `Supply Chain Analytics` `Data Engineering`

---

## Author

Built as part of an OCI learning project combining cloud infrastructure, data engineering, SQL analytics, and business intelligence.
