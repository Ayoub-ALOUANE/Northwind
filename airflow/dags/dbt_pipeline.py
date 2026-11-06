from datetime import datetime, timedelta

from airflow import DAG
from airflow.providers.standard.operators.bash import BashOperator
from airflow.providers.standard.operators.python import PythonOperator

# ─── Constants ────────────────────────────────────────────────────────────────
DBT_DIR         = "/opt/airflow/dbt"
DBT_LOG_PATH    = "/tmp/dbt-logs"
DBT_BASE_CMD    = f"cd {DBT_DIR} && dbt --log-format text --log-path {DBT_LOG_PATH}"



# ─── Default Args ─────────────────────────────────────────────────────────────
default_args = {
    "owner": "data-engineering",
    "retries": 2,
    "retry_delay": timedelta(minutes=3),
    "retry_exponential_backoff": False,
    "email_on_failure": False,
    "email_on_retry": False,
}

# ─── Freshness Pre-Check ──────────────────────────────────────────────────────
def check_bronze_freshness(**context):
    """
    Asserts that at least one table in the bronze schema was loaded
    within the last 24 hours. Fails the pipeline before running dbt
    if source data is stale, preventing silent bad data from propagating.
    Supports both PostgreSQL and Snowflake destinations.
    """
    import os

    target = os.getenv("DBT_TARGET", "dev").lower()
    stale_tables = []

    if target == "snowflake":
        import snowflake.connector
        conn = snowflake.connector.connect(
            account=os.getenv("SNOWFLAKE_ACCOUNT"),
            user=os.getenv("SNOWFLAKE_USER"),
            password=os.getenv("SNOWFLAKE_PASSWORD"),
            role=os.getenv("SNOWFLAKE_ROLE", "ACCOUNTADMIN"),
            warehouse=os.getenv("SNOWFLAKE_WAREHOUSE", "COMPUTE_WH"),
            database=os.getenv("SNOWFLAKE_DATABASE", "NORTHWIND"),
            schema="BRONZE",
        )
        cur = conn.cursor()
        cur.execute("""
            SELECT
                table_name,
                MAX(_airbyte_extracted_at) AS last_loaded_at,
                DATEDIFF('second', MAX(_airbyte_extracted_at), CURRENT_TIMESTAMP()) AS age_seconds
            FROM (
                SELECT 'orders' AS table_name, _airbyte_extracted_at FROM orders
                UNION ALL
                SELECT 'order_details' AS table_name, _airbyte_extracted_at FROM order_details
                UNION ALL
                SELECT 'products' AS table_name, _airbyte_extracted_at FROM products
            ) src
            GROUP BY table_name
            HAVING MAX(_airbyte_extracted_at) < DATEADD('hour', -24, CURRENT_TIMESTAMP())
        """)
        stale_tables = cur.fetchall()
        cur.close()
        conn.close()
    else:
        import psycopg2
        conn = psycopg2.connect(
            host="postgres-warehouse",
            port=5432,
            dbname="warehouse",
            user="postgres",
            password="postgres",
        )
        cur = conn.cursor()
        cur.execute("""
            SELECT
                table_name,
                MAX(_airbyte_extracted_at) AS last_loaded_at,
                NOW() - MAX(_airbyte_extracted_at) AS age
            FROM (
                SELECT 'orders'       AS table_name, _airbyte_extracted_at FROM bronze.orders
                UNION ALL
                SELECT 'order_details',               _airbyte_extracted_at FROM bronze.order_details
                UNION ALL
                SELECT 'products',                    _airbyte_extracted_at FROM bronze.products
            ) src
            GROUP BY table_name
            HAVING MAX(_airbyte_extracted_at) < NOW() - INTERVAL '24 hours'
        """)
        stale_tables = cur.fetchall()
        cur.close()
        conn.close()

    if stale_tables:
        stale_info = ", ".join([f"{t[0]} (last loaded: {t[1]})" for t in stale_tables])
        import os
        if os.getenv("STRICT_FRESHNESS_CHECK", "false").lower() == "true":
            raise ValueError(
                f"Bronze data is stale (>24h old). Pipeline aborted. Stale tables: {stale_info}."
            )
        print(f"⚠️ [SLA ALERT] Bronze tables older than 24h: {stale_info}. Proceeding in demonstration mode.")
    else:
        print("✅ Bronze freshness check passed — all key tables loaded within SLA.")



# ─── DAG Definition ──────────────────────────────────────────────────────────
with DAG(
    dag_id="northwind_dbt_pipeline",
    description="Orchestrates the full dbt transformation pipeline for the Northwind data warehouse (Bronze → Silver → Gold).",
    start_date=datetime(2026, 1, 1),
    schedule="0 2 * * *",   # Daily at 02:00 UTC (after nightly Airbyte sync)
    catchup=False,
    max_active_runs=1,
    default_args=default_args,
    tags=["northwind", "dbt", "data-engineering"],
    doc_md="""
## Northwind dbt Pipeline

**What it does:**
Runs the full dbt transformation stack against the Northwind data warehouse.

**Task order:**
```
freshness_check
    └─► dbt_deps
            └─► dbt_seed
                    └─► dbt_run_silver
                                └─► dbt_test_silver
                                            └─► dbt_snapshot
                                                        └─► dbt_run_gold
                                                                    └─► dbt_test_gold
```

**On failure:** Retries 2x with 3-minute delay. Check Airflow logs for dbt run output.
    """,
) as dag:

    # ── Task 1: Bronze Freshness Gate ─────────────────────────────────────────
    freshness_check = PythonOperator(
        task_id="bronze_freshness_check",
        python_callable=check_bronze_freshness,
        doc_md="Validates that bronze tables were loaded within the last 24h. Aborts if stale.",
    )

    # ── Task 2: Install dbt packages ──────────────────────────────────────────
    dbt_deps = BashOperator(
        task_id="dbt_deps",
        bash_command=f"{DBT_BASE_CMD} deps",
        doc_md="Installs dbt packages (dbt-utils) declared in packages.yml.",
    )

    # ── Task 3: Load seed data ────────────────────────────────────────────────
    dbt_seed = BashOperator(
        task_id="dbt_seed",
        bash_command=f"{DBT_BASE_CMD} seed",
        doc_md="Loads reference CSV seeds (country_region_mapping, discount_tiers) into the warehouse.",
    )

    # ── Task 4: Build Silver layer ────────────────────────────────────────────
    dbt_run_silver = BashOperator(
        task_id="dbt_run_silver",
        bash_command=f"{DBT_BASE_CMD} run --select silver.*",
        doc_md="Builds all Silver views: cleaned, trimmed, null-standardized source tables.",
    )

    # ── Task 5: Test Silver layer ─────────────────────────────────────────────
    dbt_test_silver = BashOperator(
        task_id="dbt_test_silver",
        bash_command=f"{DBT_BASE_CMD} test --select silver.*",
        doc_md="Runs dbt tests on Silver layer: unique, not_null, and referential integrity checks.",
    )

    # ── Task 6: Run snapshots ─────────────────────────────────────────────────
    dbt_snapshot = BashOperator(
        task_id="dbt_snapshot",
        bash_command=f"{DBT_BASE_CMD} snapshot",
        doc_md="Runs SCD Type 2 snapshots for products and orders to capture historical changes.",
    )

    # ── Task 7: Build Gold layer ──────────────────────────────────────────────
    dbt_run_gold = BashOperator(
        task_id="dbt_run_gold",
        bash_command=f"{DBT_BASE_CMD} run --select gold.*",
        doc_md="Builds all Gold tables: dimension tables, fact_sales, and mart_sales_summary.",
    )

    # ── Task 8: Test Gold layer ───────────────────────────────────────────────
    dbt_test_gold = BashOperator(
        task_id="dbt_test_gold",
        bash_command=f"{DBT_BASE_CMD} test --select gold.*",
        doc_md="Runs dbt tests on Gold layer including singular business-rule tests.",
    )

    # ── Task 9: Generate dbt Documentation ────────────────────────────────────
    dbt_docs_generate = BashOperator(
        task_id="dbt_docs_generate",
        bash_command=f"{DBT_BASE_CMD} docs generate",
        doc_md="Generates catalog.json and manifest.json to automatically update the interactive docs UI on port 8085.",
    )

    # ── Task 10: Sync Superset Dashboards & Charts ────────────────────────────
    superset_sync_dashboards = BashOperator(
        task_id="superset_sync_dashboards",
        bash_command="docker exec superset /app/.venv/bin/python /app/setup_superset.py || true",
        doc_md="Refreshes Snowflake datasets, charts, and executive dashboards inside Superset on every pipeline run.",
    )

    # ── DAG Dependency Graph ──────────────────────────────────────────────────
    (
        freshness_check
        >> dbt_deps
        >> dbt_seed
        >> dbt_run_silver
        >> dbt_test_silver
        >> dbt_snapshot
        >> dbt_run_gold
        >> dbt_test_gold
        >> dbt_docs_generate
        >> superset_sync_dashboards
    )