from datetime import datetime

from airflow import DAG
from airflow.providers.standard.operators.bash import BashOperator


with DAG(
    dag_id="northwind_dbt_pipeline",
    start_date=datetime(2026, 1, 1),
    schedule=None,
    catchup=False,
    tags=["northwind","dbt"],
) as dag:

    dbt_build = BashOperator(
        task_id="dbt_build",
        bash_command="""
            cd /opt/airflow/dbt

            dbt build \
                --profiles-dir /opt/airflow/dbt/profiles \
                --log-path /tmp/dbt-logs \
                --target-path /tmp/dbt-target
        """,
    )

bash_command="""
    set -eux

    cd /opt/airflow/dbt

    echo "=== WHO AM I ==="
    whoami

    echo "=== DBT LOCATION ==="
    which dbt

    echo "=== PROJECT ==="
    pwd
    ls -la

    echo "=== DBT VERSION ==="
    dbt --version

    echo "=== DBT BUILD ==="
    dbt build \
        --profiles-dir /opt/airflow/dbt/profiles \
        --log-path /tmp/dbt-logs \
        --target-path /tmp/dbt-target
"""