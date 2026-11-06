# Northwind Data Platform

A production-grade, containerized end-to-end data platform built on the classic **Northwind** enterprise trading dataset. The platform ingests transactional data, orchestrates multi-tiered ELT transformations across a Medallion Architecture (Bronze → Silver → Gold), captures historical entity evolution via Slowly Changing Dimensions (SCD Type 2), materializes dimensional star schemas and domain analytical marts, enforces rigorous data quality assertions, and maintains automated CI/CD and SLA freshness monitoring.

---

## Table of Contents

- [Overview](#overview)
- [Architecture & Medallion Layers](#architecture--medallion-layers)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Data Modeling & Marts](#data-modeling--marts)
  - [Bronze Layer (Raw Ingestion)](#bronze-layer-raw-ingestion)
  - [Silver Layer (Conformed Views)](#silver-layer-conformed-views)
  - [Gold Layer — Star Schema & Dimensional Modeling](#gold-layer--star-schema--dimensional-modeling)
  - [Gold Layer — Analytical Data Marts](#gold-layer--analytical-data-marts)
  - [Slowly Changing Dimensions (SCD Type 2 Snapshots)](#slowly-changing-dimensions-scd-type-2-snapshots)
  - [Reference Seeds](#reference-seeds)
- [Data Quality & Testing Framework](#data-quality--testing-framework)
  - [Generic Test Macros](#generic-test-macros)
  - [Singular Business-Rule Tests](#singular-business-rule-tests)
  - [Source Freshness SLAs](#source-freshness-slas)
- [BI Semantic Layer & Exposures](#bi-semantic-layer--exposures)
- [Airflow Orchestration](#airflow-orchestration)
  - [1. Core ELT Pipeline (`northwind_dbt_pipeline`)](#1-core-elt-pipeline-northwind_dbt_pipeline)
  - [2. Operational SLA Monitoring (`northwind_monitoring`)](#2-operational-sla-monitoring-northwind_monitoring)
- [CI/CD & Developer Tooling](#cicd--developer-tooling)
- [Services & Ports](#services--ports)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Quick Start with Make](#quick-start-with-make)
  - [Manual Docker Setup](#manual-docker-setup)

---

## Overview

The Northwind Data Platform demonstrates an enterprise-grade data platform using modern data stack principles:

- **ELT Ingestion** — Airbyte replicates the operational PostgreSQL database into warehouse Bronze schemas, preserving raw metadata (`_airbyte_extracted_at`).
- **Data Transformation** — dbt Core orchestrates transformations from cleaned Silver views into dimensional Star Schemas and business-domain Gold marts.
- **Dimensional Modeling** — Implements Ralph Kimball's dimensional modeling patterns: conformed dimensions, surrogate keys (MD5 hashes), role-playing date dimensions, and many-to-many bridge tables.
- **Behavioral Analytics** — Features an automated RFM (Recency, Frequency, Monetary) customer segmentation engine using windowed `NTILE(5)` distribution scoring.
- **Historical Tracking (SCD Type 2)** — dbt Snapshots track attribute drift across products (price, inventory), orders (shipping milestones), and customers (corporate profile changes).
- **Data Quality & Governance** — Automated pre-pipeline freshness gating, generic column boundary constraints, singular financial reconciliation tests, and column-level YAML documentation.
- **Dual Airflow Orchestration** — Independent DAGs for core batch processing (02:00 UTC) and operational SLA monitoring/inventory alert dispatching (06:00 UTC).
- **CI/CD Automation** — GitHub Actions testing suite (`pytest` DAG structural verification, SQLFluff code linting, and `dbt parse` compile checks).

---

## Architecture & Medallion Layers

Detailed architectural documentation is available in [docs/architecture.md](docs/architecture.md).

```
                      OPERATIONAL LAYER (OLTP)
                +----------------------------------+
                |   PostgreSQL (Northwind Source)  |
                |   Port: 55432                    |
                |   Schema: public (14 tables)     |
                +-----------------+----------------+
                                  |
                   CDC / Scheduled Batch Sync
                   (Airbyte Container Engine)
                                  |
                                  v
+-----------------------------------------------------------------------+
|                      DATA WAREHOUSE (OLAP)                            |
|                 PostgreSQL Engine — Port: 55433                       |
|                                                                       |
|  +-----------------------------------------------------------------+  |
|  |  BRONZE SCHEMA (Raw, immutable replication tier)                |  |
|  |  - Raw ingestion tables with `_airbyte_extracted_at` metadata   |  |
|  |  - Preserves exact source schema and datatypes                  |  |
|  +--------------------------------+--------------------------------+  |
|                                   |                                   |
|                        dbt Silver Transformations                     |
|                        (Typecasting, Coalescing,                      |
|                         Whitespace trimming, View materialization)    |
|                                   v                                   |
|  +-----------------------------------------------------------------+  |
|  |  SILVER SCHEMA (Conformed, normalized validation tier)          |  |
|  |  - Cleaned views: categories, customers, employees, orders,      |  |
|  |    order_details, products, shippers, suppliers, territories    |  |
|  |  - Referenced by dbt Snapshots & Gold models                    |  |
|  +----------------+-------------------------------+----------------+  |
|                   |                               |                   |
|         dbt Snapshot (SCD Type 2)        dbt Star Transformations     |
|         (Check Strategy)                 (Surrogate Keys, Joins,      |
|                   v                       Aggregations, Seeds)        |
|  +-----------------------------+                  v                   |
|  |  SNAPSHOTS SCHEMA           |  +--------------------------------+  |
|  |  - products_snapshot        |  |  GOLD SCHEMA                   |  |
|  |  - orders_snapshot          |  |  - Star Schema (Fact + Dims)   |  |
|  |  - customers_snapshot       |  |  - 5 Business Domain Marts     |  |
|  +-----------------------------+  +----------------+---------------+  |
|                                                    |                  |
+----------------------------------------------------+------------------+
                                                     |
                                                     v
                                      +-------------------------------+
                                      |    ANALYTICS & BI LAYER       |
                                      |    Apache Superset (Port 8088)|
                                      |    - Sales Exec Dashboard     |
                                      |    - Customer RFM Explorer    |
                                      |    - Logistics & Shipping KPI |
                                      |    - Inventory & Reorder Hub  |
                                      +-------------------------------+
```

---

## Tech Stack

| Component | Tool | Version | Description |
|---|---|---|---|
| Containerization | Docker Compose | v2+ | Multi-service orchestration |
| Source Database | PostgreSQL | 16 | Operational OLTP system |
| Data Warehouse | PostgreSQL | 16 | Dedicated analytical warehouse |
| Ingestion Engine | Airbyte | 0.50+ | Scheduled batch/CDC replication |
| Transformation | dbt Core + dbt-postgres | 1.12.0 / 1.11.0 | Medallion modeling & semantic testing |
| dbt Packages | dbt-utils | ~1.3.0 | Surrogate key generation & tests |
| Orchestration | Apache Airflow | 3.1.0 | Multi-DAG workflow scheduling |
| Business Intelligence | Apache Superset | latest | Interactive dashboards and charts |
| Database Admin | pgAdmin 4 | latest | Database management & inspection |
| Code Quality | SQLFluff & Pytest | latest | Automated SQL linting and DAG CI tests |

---

## Project Structure

```
Northwind/
├── .github/
│   └── workflows/
│       └── ci.yml                      # CI/CD: Pytest DAG checks, SQLFluff, dbt compile
├── .sqlfluff                           # SQLFluff formatting & linting configuration
├── .sqlfluffignore                     # Ignore patterns for SQL linter
├── Makefile                            # Unified developer CLI commands
├── docker-compose.yml                  # Root Compose manifest
│
├── compose/                            # Modular Docker Compose services
│   ├── postgres.yml
│   ├── airflow.yml
│   ├── airbyte.yml
│   ├── pgadmin.yml
│   ├── superset.yml
│   └── infrastructure.yml
│
├── airflow/
│   ├── Dockerfile                      # Airflow 3.1.0 image with dbt & drivers
│   ├── requirements.txt                # Python dependencies (dbt-core, psycopg2)
│   └── dags/
│       ├── dbt_pipeline.py             # Core 8-task daily ELT pipeline
│       └── monitoring.py               # 06:00 UTC SLA & inventory alert monitoring DAG
│
├── dbt/
│   ├── dbt_project.yml                 # dbt project root configuration
│   ├── packages.yml                    # dbt-utils package specification
│   ├── profiles/
│   │   └── profiles.yml                # Multi-target connection config (dev, local, ci)
│   ├── models/
│   │   ├── sources.yml                 # Bronze sources & freshness SLA thresholds
│   │   ├── exposures.yml               # Lineage links to Superset dashboards
│   │   ├── silver/                     # Conformed views layer (12 views + schema.yml)
│   │   └── gold/                       # Star schema dimensions, facts & 5 marts
│   │       ├── dim_customers.sql       # Customer dimension with region lookup
│   │       ├── dim_employees.sql       # Employee dimension with hierarchy & tenure
│   │       ├── dim_products.sql        # Product dimension with category & supplier
│   │       ├── dim_shippers.sql        # Shipper dimension
│   │       ├── dim_suppliers.sql       # Supplier dimension with catalog aggregations
│   │       ├── dim_date.sql            # Date dimension spine (1996-1998)
│   │       ├── bridge_employee_territories.sql # Many-to-many bridge table
│   │       ├── fact_sales.sql          # Core grain fact table with revenue KPIs
│   │       ├── mart_sales_summary.sql  # Aggregated monthly sales by category/region
│   │       ├── mart_customer_segments.sql # RFM segmentation model
│   │       ├── mart_product_performance.sql # Product lifecycle & pricing performance
│   │       ├── mart_employee_performance.sql # Rep quota & delivery performance
│   │       ├── mart_shipping_performance.sql # Logistics & on-time delivery KPIs
│   │       ├── schema.yml              # Star schema documentation & tests
│   │       └── schema_marts.yml        # Mart column-level documentation & tests
│   ├── snapshots/
│   │   ├── products_snapshot.sql       # SCD2: unit price, stock, discontinued status
│   │   ├── orders_snapshot.sql         # SCD2: shipping milestones, freight, address
│   │   └── customers_snapshot.sql      # SCD2: corporate renames, addresses, titles
│   ├── seeds/
│   │   ├── country_region_mapping.csv  # Country to global macro-region reference
│   │   ├── discount_tiers.csv          # Concession tier boundary definitions
│   │   └── schema.yml                  # Seed documentation & value constraints
│   ├── macros/
│   │   ├── financial.sql               # Financial math macros (safe_divide, net_revenue)
│   │   ├── generic_tests.sql           # Generic test macros (range bounds, non-empty)
│   │   └── get_custom_schema.sql       # Dynamic schema routing macro
│   ├── tests/
│   │   ├── assert_fact_sales_revenue_positive.sql
│   │   ├── assert_order_dates_in_dim_date.sql
│   │   ├── assert_no_products_below_reorder_level.sql
│   │   ├── assert_mart_revenue_matches_fact.sql
│   │   └── assert_customer_segments_unique.sql
│   └── analyses/
│       ├── top_customers_by_revenue.sql
│       ├── late_shipments_by_employee.sql
│       ├── product_reorder_alerts.sql
│       ├── revenue_growth_mom.sql
│       ├── rfm_segment_revenue_distribution.sql
│       └── category_revenue_ranking.sql
│
├── tests/
│   └── test_airflow_dags.py            # Automated DAG validation & integrity test suite
│
├── infrastructure/
│   ├── source/northwind.sql            # Source OLTP relational seed database
│   └── warehouse/init.sql              # Target warehouse schema initialization
│
└── docs/
    ├── architecture.md                 # Full Architecture & Engineering Specification
    ├── ER.png                          # Source entity relationship diagram
    ├── Silver.png                      # Silver conformed layer diagram
    ├── pipeline.png                    # Pipeline execution diagram
    └── star_schema.png                 # Gold Kimball star schema diagram
```

---

## Data Modeling & Marts

### Bronze Layer (Raw Ingestion)
Raw landing tables populated by Airbyte into schema `bronze`. Each table contains immutable raw records with ingestion metadata (`_airbyte_extracted_at`, `_airbyte_raw_id`).

### Silver Layer (Conformed Views)
Materialized as views in schema `public` (mapped to source names). Standardizes data types, strips whitespace, standardizes missing values via `NULLIF()`, and enforces column-level nullability constraints.

### Gold Layer — Star Schema & Dimensional Modeling

Built following Ralph Kimball dimensional modeling best practices:

| Model | Type | Business Key | Surrogate Key | Key Attributes / Enrichments |
|---|---|---|---|---|
| `dim_customers` | Dimension | `customer_id` | `customer_sk` | Contact information, location, conjoined with `country_region_mapping` seed |
| `dim_employees` | Dimension | `employee_id` | `employee_sk` | Self-joined manager details (`reports_to_name`), tenure calculations |
| `dim_products` | Dimension | `product_id` | `product_sk` | Joined with category & supplier details, margin indicators |
| `dim_suppliers` | Dimension | `supplier_id` | `supplier_sk` | Supplier contact info, active product catalog size, catalog price range |
| `dim_shippers` | Dimension | `shipper_id` | `shipper_sk` | Carrier information and contact details |
| `dim_date` | Dimension | `date_id` | `date_id` | Generated date spine (1996-1998) with weekend flags, quarter names |
| `bridge_employee_territories`| Bridge | `employee_id` + `territory_id` | `bridge_sk` | Resolves many-to-many relationship between staff and territories |
| `fact_sales` | Fact | `order_id` + `product_id` | `fact_sales_sk` | Order line-item grain: `gross_revenue`, `net_revenue`, `discount_amount`, `days_to_ship`, `is_late_shipment` |

### Gold Layer — Analytical Data Marts

Materialized as tables in schema `gold` to serve specific business functions without requiring downstream BI users to write complex joins:

| Mart Model | Business Grain | Purpose & Key Metrics |
|---|---|---|
| `mart_sales_summary` | Year-Month $\times$ Category $\times$ Country | Monthly performance monitoring: gross/net revenue, order volume, discount totals |
| `mart_customer_segments` | Single Customer Account | Enterprise RFM segmentation engine assigning accounts to `Champion`, `Loyal`, `At Risk`, `Lost High Value`, and `Standard` tiers |
| `mart_product_performance` | Single Product | Portfolio analysis: lifetime units sold, realized vs list price spread, stock status, late shipment frequency |
| `mart_employee_performance` | Single Employee Rep | Sales rep KPI tracking: revenue booked, average order size, late shipment rate, territory count |
| `mart_shipping_performance` | Shipper $\times$ Year-Month | Logistics tracking: average delivery speed (days), on-time delivery %, freight spend |

### Slowly Changing Dimensions (SCD Type 2 Snapshots)

Materialized in schema `snapshots` using dbt's `check` strategy to track historical entity changes over time:

1. **`products_snapshot`**: Monitors fluctuations in `unit_price`, `units_in_stock`, `units_on_order`, and `discontinued`.
2. **`orders_snapshot`**: Tracks fulfillment milestones (`shipped_date`, `ship_via`, `freight`, shipping address).
3. **`customers_snapshot`**: Captures corporate renames, address relocations, contact title promotions, and phone updates.

### Reference Seeds

Located in `dbt/seeds/`:
- **`country_region_mapping.csv`**: Maps customer countries into global macro-regions (`Americas`, `Europe`, `Asia-Pacific`).
- **`discount_tiers.csv`**: Defines concession tier classification bounds (`No Discount`, `Light`, `Moderate`, `Heavy`).

---

## Data Quality & Testing Framework

The platform implements a multi-layer defense against bad or stale data:

### Generic Test Macros (`dbt/macros/generic_tests.sql`)
- `assert_column_is_between(model, column_name, min_value, max_value)`: Validates numeric range bounds (applied to `discount` $\in [0, 1]$ and `unit_price` $\ge 0$).
- `assert_not_empty(model)`: Asserts that critical dimension and fact tables contain rows, preventing silent pipeline wiping.

### Singular Business-Rule Tests (`dbt/tests/`)
- `assert_fact_sales_revenue_positive.sql`: Asserts `net_revenue >= 0` across all line items.
- `assert_order_dates_in_dim_date.sql`: Asserts all transactional order dates fall within the dimension calendar bounds.
- `assert_no_products_below_reorder_level.sql`: Operational inventory test flagging active products breaching minimum stock.
- `assert_mart_revenue_matches_fact.sql`: Financial reconciliation test ensuring `mart_sales_summary` net revenue matches `fact_sales` totals within a $1 tolerance.
- `assert_customer_segments_unique.sql`: Uniqueness test verifying that every customer receives exactly one RFM classification.

### Source Freshness SLAs
Configured in `dbt/models/sources.yml`:
- **Warning threshold**: 12 hours.
- **Error threshold**: 24 hours. Evaluated both in dbt and via an independent Airflow Python gate.

---

## BI Semantic Layer & Exposures

Downstream BI dashboards in Apache Superset are documented in `dbt/models/exposures.yml`, providing complete data lineage visibility from source tables through marts to user-facing dashboards:

1. **Northwind Sales Performance Dashboard** (`fact_sales`, `dim_date`, `dim_products`, `mart_sales_summary`)
2. **Customer Segmentation & RFM Explorer** (`mart_customer_segments`, `dim_customers`)
3. **Logistics & Carrier Performance Hub** (`mart_shipping_performance`, `dim_shippers`)
4. **Sales Rep Performance & Quotas** (`mart_employee_performance`, `dim_employees`)
5. **Inventory Health & Reorder Monitor** (`mart_product_performance`, `dim_products`)

---

## Airflow Orchestration

The platform runs two independent DAGs orchestrated via Apache Airflow 3.1.0:

### 1. Core ELT Pipeline (`northwind_dbt_pipeline`)
- **Schedule**: Daily at 02:00 UTC (`0 2 * * *`).
- **Task Graph**:
  ```
  bronze_freshness_check
          └─► dbt_deps
                  └─► dbt_seed
                          └─► dbt_run_silver
                                      └─► dbt_test_silver
                                                  └─► dbt_snapshot
                                                              └─► dbt_run_gold
                                                                          └─► dbt_test_gold
  ```
- **Freshness Gate**: `bronze_freshness_check` verifies that Airbyte has synced bronze tables within the last 24h before running dbt. If stale, the pipeline aborts early to prevent downstream contamination.

### 2. Operational SLA Monitoring (`northwind_monitoring`)
- **Schedule**: Daily at 06:00 UTC (`0 6 * * *`) — 4 hours post-ELT.
- **Task Graph**:
  ```
  source_freshness_check ──┬──► low_stock_alert
                           └──► run_singular_tests
  ```
- **Actions**: Generates structured JSON freshness health reports, alerts on critical low-stock inventory, and reruns singular reconciliation checks.

---

## CI/CD & Developer Tooling

The project incorporates production CI/CD tooling:

- **GitHub Actions (`.github/workflows/ci.yml`)**:
  - `validate-airflow`: Runs automated DAG integrity and structure tests via `pytest`.
  - `lint-sql`: Runs `sqlfluff` linting against dbt models using the Postgres dialect.
  - `validate-dbt`: Validates dbt syntax, dependencies (`dbt deps`), and compiles models (`dbt parse`).
- **Automated Tests (`tests/test_airflow_dags.py`)**: Unit tests for DAG syntax, imports, and task configurations.
- **Makefile**: Single-command shortcuts for all developer operations.

---

## Services & Ports

| Service | Local URL / Host Port | Credentials | Purpose |
|---|---|---|---|
| **Airflow UI** | [http://localhost:8081](http://localhost:8081) | `admin` / `admin` | Pipeline orchestration & monitoring |
| **Apache Superset** | [http://localhost:8088](http://localhost:8088) | Setup on launch | Analytical dashboards & exploration |
| **pgAdmin 4** | [http://localhost:5051](http://localhost:5051) | `pgadmin4@pgadmin.org` / `postgres` | Warehouse & source DB management |
| **Source DB (Postgres)** | `localhost:55432` | `postgres` / `postgres` (db: `northwind`) | OLTP transactional database |
| **Warehouse (Postgres)** | `localhost:55433` | `postgres` / `postgres` (db: `warehouse`) | Analytical Medallion data warehouse |
| **Airflow DB (Postgres)**| `localhost:55434` | `airflow` / `airflow` (db: `airflow`) | Airflow metadata store |

---

## Getting Started

### Prerequisites
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) with Docker Compose v2.
- At least **8 GB of RAM** allocated to Docker.
- (Optional for local CLI dev) Python 3.10+ and `dbt-core`.

### Quick Start with Make

```bash
# 1. Start all containerized platform services
make up

# 2. Run local unit tests
make test

# 3. Trigger dbt package installation & seed loading
make dbt-deps
make dbt-seed

# 4. Execute the dbt transformation pipeline
make dbt-run

# 5. Run all dbt data quality tests
make dbt-test

# 6. Run SCD Type 2 snapshots
make dbt-snapshot

# 7. Generate dbt interactive documentation
make dbt-docs
```

### Manual Docker Setup

If `make` is not available:

```bash
# 1. Create external volumes
docker volume create source_postgresql_data
docker volume create warehouse_warehouse_data
docker volume create source_pgadmin_root_prefs
docker volume create source_pgadmin_working_dir

# 2. Launch services
docker compose up -d

# 3. Follow Airflow initialization
docker compose logs -f airflow-init
```
