# Northwind Data Platform — Architecture & Engineering Specification

## 1. Executive Summary & Objective

The **Northwind Data Platform** is an enterprise-grade, containerized data engineering solution designed to transition the transactional operations of the Northwind trading company from an OLTP PostgreSQL database into a high-performance, analytically modeled data warehouse. 

The platform implements:
- **ELT Paradigm**: Decoupling raw ingestion from transformation, preserving immutable source records.
- **Medallion Architecture**: Progression from raw ingestion (`bronze`), through conformed, cleaned views (`silver`), to Kimball star-schema dimensional tables and specialized business marts (`gold`).
- **Slowly Changing Dimensions (SCD Type 2)**: Persistent point-in-time state tracking for volatile dimensions (products, orders, customers).
- **Proactive Observability**: Pre-pipeline freshness gating, continuous threshold assertions, singular reconciliation tests, and automated SLA inventory alerts.
- **Continuous Integration (CI/CD)**: DAG integrity testing, dbt compilation checks, and SQLFluff style linting.

---

## 2. End-to-End Architecture Flow

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
|  |  - customers_snapshot       |  |  - Business Performance Marts  |  |
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

## 3. Storage Layer & Medallion Pattern

### 3.1 Bronze Layer (`bronze`)
- **Nature**: Raw dump from the transactional system.
- **Characteristics**: Managed directly by Airbyte. No manual modifications or constraints. 
- **Audit Columns**: Every table contains `_airbyte_extracted_at`, `_airbyte_raw_id`, and `_airbyte_meta`.
- **Freshness SLA**: Monitored automatically prior to any transformation.

### 3.2 Silver Layer (`silver`)
- **Nature**: Cleaned, standardized views.
- **Transformation Rules**:
  - `TRIM()` applied to all string columns.
  - `COALESCE()` on nullable text/regional fields to prevent three-valued logic hazards.
  - Explicit datatype casting (`NUMERIC`, `INTEGER`, `DATE`).
  - Business rules applied: `unit_price >= 0`, `discount BETWEEN 0 AND 1`.
  - Materialized as **views** to reduce storage footprint while ensuring zero data duplication.

### 3.3 Gold Layer (`gold`)
- **Nature**: Physicalized tables (`materialized='table'`) optimized for analytical query latency.
- **Schema Patterns**:
  - **Kimball Dimensional Modeling**: Star schema with clear separation of facts and conformed dimensions.
  - **Surrogate Keys**: Primary keys constructed using deterministic MD5 hashes (`dbt_utils.generate_surrogate_key`).
  - **Role-Playing Dimensions**: `dim_date` joins thrice to `fact_sales` (`order_date_id`, `required_date_id`, `shipped_date_id`).
  - **Many-to-Many Bridge Table**: `bridge_employee_territories` maps territory coverage without denormalizing employee dimensions.

---

## 4. Dimensional Modeling & Star Schema

```
                           +----------------------+
                           |     dim_customers    |
                           +----------------------+
                           | PK  customer_id      |
                           |     customer_sk      |
                           |     company_name     |
                           |     world_region     |
                           +----------+-----------+
                                      |
                                      | 1
                                      |
                                      | N
+----------------------+   N      1 +-+--------------------+ 1      N +----------------------+
|     dim_products     +------------+      fact_sales      +----------+      dim_shippers    |
+----------------------+            +----------------------+          +----------------------+
| PK  product_id       |            | PK  fact_sales_sk    |          | PK  shipper_id       |
|     product_sk       |            | FK  order_id         |          |     shipper_sk       |
|     product_name     |            | FK  product_id       |          |     company_name     |
|     category_name    |            | FK  customer_id      |          |     phone            |
|     supplier_name    |            | FK  employee_id      |          +----------------------+
|     unit_price       |            | FK  shipper_id       |
+----------------------+            | FK  order_date_id    |
                                    | FK  required_date_id |
                                    | FK  shipped_date_id  |
                                    |     quantity         |
                                    |     unit_price       |
+----------------------+            |     discount         |          +----------------------+
|     dim_employees    |            |     gross_revenue    |          |       dim_date       |
+----------------------+            |     net_revenue      |          +----------------------+
| PK  employee_id      |            |     discount_amount  |          | PK  date_id          |
|     employee_sk      |            |     is_late_shipment |          |     date_actual      |
|     full_name        |            +----------+-----------+          |     year, quarter    |
|     reports_to_name  +-----------------------+ 1                    |     month, day_name  |
|     tenure_years     | N                                       N    |     is_weekend       |
+----------------------+                                              +----------------------+
```

### Fact Table Grain: `fact_sales`
- **Grain**: One row per physical order line item (`order_id`, `product_id`).
- **Degenerate Dimensions**: `order_id` preserved for transaction tracing.
- **Measures**:
  - `quantity`: Physical units moved.
  - `unit_price`: Realized price at order time.
  - `discount`: Fractional discount concession.
  - `gross_revenue`: $quantity \times unit\_price$.
  - `net_revenue`: $quantity \times unit\_price \times (1 - discount)$.
  - `discount_amount`: Concession dollar value.
  - `days_to_ship`: Fulfillment cycle time ($shipped\_date - order\_date$).
  - `is_late_shipment`: Binary alert flag ($shipped\_date > required\_date$).

---

## 5. Analytical Data Marts

To serve targeted business domains without forcing analytical queries through wide fact-dimension joins, four analytical marts are materialized in `gold`:

| Mart Model | Business Grain | Key Metrics & Dimensions |
|---|---|---|
| `mart_sales_summary` | Daily by Category & Country | Net revenue, order count, unique buyers, discount value |
| `mart_customer_segments` | Single Customer Grain | RFM (Recency, Frequency, Monetary) scores, Customer Segment (Champion, Loyal, At Risk, Lost) |
| `mart_product_performance` | Product Grain | Lifetime units sold, realized vs list price spread, stock status, late shipment rate |
| `mart_employee_performance` | Employee Grain | Total revenue booked, quota contribution, average order size, late shipment rate |
| `mart_shipping_performance` | Shipper $\times$ Year/Month | Freight volume, on-time delivery %, mean transit duration (days) |

### Customer RFM Segmentation Engine
The `mart_customer_segments` model implements an enterprise RFM segmentation engine using windowed `NTILE(5)` distributions:
- **Recency ($R$)**: Days elapsed since the customer's last completed purchase.
- **Frequency ($F$)**: Lifetime count of discrete orders placed.
- **Monetary ($M$)**: Lifetime cumulative net revenue generated.
- **Composite Segment Classification**:
  - `Champion`: High recency, high frequency, top revenue ($R \ge 4, F \ge 4, M \ge 4$).
  - `Loyal Customer`: Consistent order frequency, above-average spend ($F \ge 3$).
  - `At Risk`: Historically valuable accounts with no recent activity ($R \le 2, M \ge 3$).
  - `Lost High Value`: Churned accounts ($R = 1$) with significant historical revenue.
  - `Standard / One-Time`: Low-frequency, low-monetary accounts.

---

## 6. Slowly Changing Dimensions (SCD Type 2)

Operational databases frequently update records in-place, destroying auditability and historical reporting accuracy. The Northwind platform captures history using **dbt Snapshots**:

- **Implementation**: Stored under schema `snapshots`.
- **Target Entities**:
  1. `products_snapshot`: Tracks fluctuations in `unit_price`, `units_in_stock`, `units_on_order`, and `discontinued`.
  2. `orders_snapshot`: Tracks fulfillment lifecycle progressions (`shipped_date`, `ship_via`, `freight`, carrier alterations).
  3. `customers_snapshot`: Tracks corporate renames, address migrations, contact title promotions, and phone adjustments.
- **Tracking Mechanism**: `strategy='check'` comparing deterministic column hashes across pipeline executions. Injected metadata includes `dbt_valid_from`, `dbt_valid_to`, and `dbt_scd_id`.

---

## 7. Data Quality & Reliability Framework

```
                          DATA QUALITY GATES
[Airbyte Sync]
      |
      v
+-------------------------------+
|  1. Bronze Freshness Check    | --> If MAX(_airbyte_extracted_at) > 24h, abort DAG
+---------------+---------------+
                | Pass
                v
+-------------------------------+
|  2. Generic Boundary Tests    | --> assert_column_is_between (discount in [0,1])
+---------------+---------------+     assert_not_empty (row count > 0)
                | Pass
                v
+-------------------------------+
|  3. Referential Integrity     | --> Foreign Key relationships (Dims <-> Facts)
+---------------+---------------+     Unique surrogate keys & NOT NULL constraints
                | Pass
                v
+-------------------------------+
|  4. Singular Business Tests   | --> assert_mart_revenue_matches_fact ($1 tolerance)
+---------------+---------------+     assert_customer_segments_unique (1:1 customer map)
                | Pass                assert_order_dates_in_dim_date (calendar bounds)
                v
[Production BI Ready]
```

---

## 8. Orchestration & Resilience Architecture

The workflow is orchestrated using **Apache Airflow 3.1.0** via containerized execution:

1. **`northwind_dbt_pipeline` (Daily at 02:00 UTC)**:
   - Synchronous pre-check PythonOperator validating bronze freshness.
   - `dbt deps` package manager invocation.
   - `dbt seed` reference dimension ingestion.
   - Tiered staging execution: `silver.*` $\to$ `silver tests` $\to$ `snapshots` $\to$ `gold.*` $\to$ `gold tests`.
   - Automated retries: 2 retry attempts with exponential backoff disabled.

2. **`northwind_monitoring` (Daily at 06:00 UTC)**:
   - Dedicated health & monitoring DAG.
   - Evaluates `dbt source freshness --output /tmp/freshness.json` and parses alerts.
   - Low-stock inventory notification scanner querying `dim_products`.
   - Runs singular reconciliation checks independently from transformations.

---

## 9. Security, Governance & Production Hardening

- **Credential Isolation**: No raw credentials hardcoded in version control; all database connection strings consume `.env` variables.
- **Target Environment Separation**: `profiles.yml` separates container networking (`dev`), host-level inspection (`local`), and headless pipelines (`ci`).
- **Semantic Lineage Documentation**: `exposures.yml` connects dbt models directly to Superset dashboard assets, providing end-to-end impact analysis.
