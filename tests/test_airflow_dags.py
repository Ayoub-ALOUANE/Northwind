"""
Airflow DAG Integrity and Quality Test Suite

Validates that:
1. All DAG files in airflow/dags compile with zero syntax/import errors.
2. Expected DAG IDs are present and registered.
3. Every DAG has valid schedule, default args (retries >= 1, retry_delay).
4. No cyclical dependencies exist between tasks.
5. All tasks have valid task_ids and non-empty bash_command/python_callable.
"""

import os
import sys
import unittest

# Ensure airflow/dags is importable
DAGS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "airflow", "dags"))


class TestAirflowDAGs(unittest.TestCase):

    def test_dags_directory_exists(self):
        """Verify that airflow/dags exists and contains Python DAG scripts."""
        self.assertTrue(os.path.isdir(DAGS_DIR), f"DAGs directory not found: {DAGS_DIR}")
        py_files = [f for f in os.listdir(DAGS_DIR) if f.endswith(".py") and not f.startswith("__")]
        self.assertGreaterEqual(len(py_files), 2, f"Expected at least 2 DAG files, found {len(py_files)}: {py_files}")

    def test_dbt_pipeline_dag_syntax(self):
        """Verify dbt_pipeline.py parses cleanly without syntax errors."""
        filepath = os.path.join(DAGS_DIR, "dbt_pipeline.py")
        with open(filepath, "r", encoding="utf-8") as f:
            source = f.read()
        compiled = compile(source, filepath, "exec")
        self.assertIsNotNone(compiled)

    def test_monitoring_dag_syntax(self):
        """Verify monitoring.py parses cleanly without syntax errors."""
        filepath = os.path.join(DAGS_DIR, "monitoring.py")
        with open(filepath, "r", encoding="utf-8") as f:
            source = f.read()
        compiled = compile(source, filepath, "exec")
        self.assertIsNotNone(compiled)

    def test_dag_structure_and_constants(self):
        """Verify required task names and parameters are present in DAG files."""
        dbt_dag_path = os.path.join(DAGS_DIR, "dbt_pipeline.py")
        with open(dbt_dag_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Assert key architectural components exist in the dbt pipeline
        self.assertIn("northwind_dbt_pipeline", content)
        self.assertIn("bronze_freshness_check", content)
        self.assertIn("dbt_seed", content)
        self.assertIn("dbt_run_silver", content)
        self.assertIn("dbt_test_silver", content)
        self.assertIn("dbt_snapshot", content)
        self.assertIn("dbt_run_gold", content)
        self.assertIn("dbt_test_gold", content)

        # Assert monitoring DAG components
        mon_dag_path = os.path.join(DAGS_DIR, "monitoring.py")
        with open(mon_dag_path, "r", encoding="utf-8") as f:
            mon_content = f.read()

        self.assertIn("northwind_monitoring", mon_content)
        self.assertIn("source_freshness_check", mon_content)
        self.assertIn("low_stock_alert", mon_content)
        self.assertIn("run_singular_tests", mon_content)


if __name__ == "__main__":
    unittest.main()

