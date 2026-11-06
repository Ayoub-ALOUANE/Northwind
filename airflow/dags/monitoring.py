from datetime import datetime, timedelta

from airflow import DAG
from airflow.providers.standard.operators.bash import BashOperator
from airflow.providers.standard.operators.python import PythonOperator

# ─── Constants ────────────────────────────────────────────────────────────────
DBT_DIR      = "/opt/airflow/dbt"
DBT_PROFILES = "/opt/airflow/dbt/profiles"

# ─── Default Args ─────────────────────────────────────────────────────────────
default_args = {
    "owner": "data-engineering",
    "retries": 1,
    "retry_delay": timedelta(minutes=2),
    "email_on_failure": False,
}

# ─── Freshness Check ─────────────────────────────────────────────────────────
def check_and_report_freshness(**context):
    """
    Runs dbt source freshness via shell and parses results.
    Logs a structured summary of each source's freshness status.
    Raises if any source is in ERROR state.
    """
    import subprocess, json, os

    result = subprocess.run(
        [
            "dbt", "source", "freshness",
            "--profiles-dir", DBT_PROFILES,
            "--output", "json",
            "--output-path", "/tmp/freshness_results.json",
        ],
        cwd=DBT_DIR,
        capture_output=True,
        text=True,
    )

    print("── dbt source freshness stdout ──")
    print(result.stdout[-3000:] if len(result.stdout) > 3000 else result.stdout)
    if result.stderr:
        print("── dbt source freshness stderr ──")
        print(result.stderr[-1000:])

    # Parse results JSON if available
    results_path = "/tmp/freshness_results.json"
    if os.path.exists(results_path):
        with open(results_path) as f:
            try:
                data = json.load(f)
                results = data.get("results", [])
                errors = [r for r in results if r.get("status") == "error"]
                warnings = [r for r in results if r.get("status") == "warn"]

                print(f"\n📊 Freshness Summary: {len(results)} sources checked")
                print(f"   ❌ Errors:   {len(errors)}")
                print(f"   ⚠️  Warnings: {len(warnings)}")
                print(f"   ✅ OK:       {len(results) - len(errors) - len(warnings)}")

                for r in results:
                    status = r.get("status", "unknown")
                    name = r.get("unique_id", "?").split(".")[-1]
                    age = r.get("max_loaded_at_time_ago_in_s")
                    age_h = round(age / 3600, 1) if age else "N/A"
                    icon = {"error": "❌", "warn": "⚠️", "pass": "✅"}.get(status, "❓")
                    print(f"   {icon} {name}: {age_h}h ago [{status.upper()}]")

                if errors:
                    error_names = [r.get("unique_id", "?").split(".")[-1] for r in errors]
                    raise ValueError(
                        f"Source freshness ERROR: {len(errors)} source(s) exceeded error threshold: "
                        f"{', '.join(error_names)}"
                    )
            except json.JSONDecodeError:
                print("⚠️  Could not parse freshness JSON — check dbt output manually")
    elif result.returncode != 0:
        raise RuntimeError("dbt source freshness failed — see logs above.")


def alert_on_low_stock(**context):
    """
    Queries the warehouse for products below reorder level.
    Logs an operational alert — in production this would push to Slack/email.
    Supports both PostgreSQL and Snowflake destinations.
    """
    import os

    target = os.getenv("DBT_TARGET", "dev").lower()
    query = """
        SELECT product_name, units_in_stock, reorder_level,
               (reorder_level - units_in_stock) AS deficit
        FROM gold.dim_products
        WHERE discontinued = FALSE
          AND units_in_stock < reorder_level
        ORDER BY deficit DESC
        LIMIT 20
    """

    if target == "snowflake":
        import snowflake.connector
        conn = snowflake.connector.connect(
            account=os.getenv("SNOWFLAKE_ACCOUNT"),
            user=os.getenv("SNOWFLAKE_USER"),
            password=os.getenv("SNOWFLAKE_PASSWORD"),
            role=os.getenv("SNOWFLAKE_ROLE", "ACCOUNTADMIN"),
            warehouse=os.getenv("SNOWFLAKE_WAREHOUSE", "COMPUTE_WH"),
            database=os.getenv("SNOWFLAKE_DATABASE", "NORTHWIND"),
            schema="GOLD",
        )
        cur = conn.cursor()
        cur.execute("""
            SELECT product_name, units_in_stock, reorder_level,
                   (reorder_level - units_in_stock) AS deficit
            FROM dim_products
            WHERE discontinued = FALSE
              AND units_in_stock < reorder_level
            ORDER BY deficit DESC
            LIMIT 20
        """)
        rows = cur.fetchall()
        cur.close()
        conn.close()
    else:
        import psycopg2
        conn = psycopg2.connect(
            host="postgres-warehouse", port=5432,
            dbname="warehouse", user="postgres", password="postgres"
        )
        cur = conn.cursor()
        cur.execute(query)
        rows = cur.fetchall()
        cur.close()
        conn.close()

    if rows:
        print(f"\n🚨 LOW STOCK ALERT — {len(rows)} product(s) below reorder level:\n")
        print(f"{'Product':<40} {'In Stock':>10} {'Reorder':>10} {'Deficit':>10}")
        print("-" * 72)
        for name, stock, reorder, deficit in rows:
            print(f"{name:<40} {stock:>10} {reorder:>10} {deficit:>10}")
    else:
        print("✅ All active products are above their reorder level.")


# ─── DAG Definition ──────────────────────────────────────────────────────────
with DAG(
    dag_id="northwind_monitoring",
    description="Daily data quality and operational monitoring for the Northwind data warehouse.",
    start_date=datetime(2026, 1, 1),
    schedule="0 6 * * *",   # Daily at 06:00 UTC — runs after the main pipeline (02:00 UTC)
    catchup=False,
    max_active_runs=1,
    default_args=default_args,
    tags=["northwind", "monitoring", "data-quality"],
    doc_md="""
## Northwind Monitoring DAG

Runs independently from the main dbt pipeline. Performs:

1. **Source Freshness Check** — `dbt source freshness` with structured JSON output
2. **Low Stock Alert** — queries `gold.dim_products` for inventory below reorder level
3. **dbt Singular Tests** — re-runs all custom business-rule singular tests

**Schedule:** Daily at 06:00 UTC (4 hours after main pipeline completes).
    """,
) as dag:

    # ── Task 1: Source Freshness Report ───────────────────────────────────────
    source_freshness = PythonOperator(
        task_id="source_freshness_check",
        python_callable=check_and_report_freshness,
        doc_md="Runs dbt source freshness, parses JSON output, and fails on any ERROR-status source.",
    )

    # ── Task 2: Low Stock Inventory Alert ─────────────────────────────────────
    low_stock_alert = PythonOperator(
        task_id="low_stock_alert",
        python_callable=alert_on_low_stock,
        doc_md="Queries gold.dim_products for active products below reorder level and logs an alert.",
    )

    # ── Task 3: Re-run Singular Tests ─────────────────────────────────────────
    run_singular_tests = BashOperator(
        task_id="run_singular_tests",
        bash_command=f"""
            cd {DBT_DIR}
            dbt test \\
                --profiles-dir {DBT_PROFILES} \\
                --select test_type:singular \\
                --log-path /tmp/dbt-monitoring-logs \\
                --target-path /tmp/dbt-monitoring-target
        """,
        doc_md="Re-runs all dbt singular (custom SQL) tests — revenue positive, date coverage, reorder alerts.",
    )

    # ── Task Graph ────────────────────────────────────────────────────────────
    source_freshness >> [low_stock_alert, run_singular_tests]
