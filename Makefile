# ── Northwind Data Platform Makefile ───────────────────────────────────────────
.PHONY: help up down restart ps logs dbt-deps dbt-seed dbt-run dbt-test dbt-snapshot dbt-docs test lint show-rfm show-products show-shipping show-reps show-scd show-counts trigger-dag

help:
	@echo "======================================================================"
	@echo "NORTHWIND DATA PLATFORM — DEVELOPER & PRESENTATION CLI"
	@echo "======================================================================"
	@echo "Platform Lifecycle:"
	@echo "  make up             Start all Docker containers in background"
	@echo "  make down           Stop all containers safely (preserves data)"
	@echo "  make restart        Restart all containers"
	@echo "  make ps             List container status and mapped ports"
	@echo "  make logs           Follow container logs live"
	@echo ""
	@echo "Medallion Pipeline (dbt Core):"
	@echo "  make dbt-deps       Install dbt package dependencies (dbt-utils)"
	@echo "  make dbt-seed       Load reference dimension lookup seeds"
	@echo "  make dbt-run        Build full warehouse (Silver views + Gold tables)"
	@echo "  make dbt-snapshot   Run SCD Type 2 history tracking snapshots"
	@echo "  make dbt-test       Run all 121 automated data quality tests"
	@echo "  make dbt-docs       Generate interactive dbt documentation"
	@echo ""
	@echo "Live Demo Showcase Queries:"
	@echo "  make show-rfm       Show RFM customer segmentation analytics"
	@echo "  make show-products  Show product performance & list vs actual price"
	@echo "  make show-shipping  Show carrier on-time delivery & speed KPIs"
	@echo "  make show-reps      Show sales rep quota & delivery metrics"
	@echo "  make show-scd       Show SCD Type 2 history audit rows"
	@echo "  make show-counts    Show total row counts for all Gold tables"
	@echo ""
	@echo "Airflow & CI Testing:"
	@echo "  make trigger-dag    Trigger the main dbt pipeline DAG in Airflow"
	@echo "  make test           Run Python DAG integrity unit tests"
	@echo "  make lint           Run SQLFluff linter on models"
	@echo "======================================================================"

up:
	docker compose up -d

down:
	docker compose down

restart:
	docker compose down && docker compose up -d

ps:
	docker compose ps

logs:
	docker compose logs -f

dbt-deps:
	docker compose exec airflow-scheduler bash -c "cd /opt/airflow/dbt && dbt --log-path /tmp/dbt-logs deps --profiles-dir /opt/airflow/dbt/profiles"

dbt-seed:
	docker compose exec airflow-scheduler bash -c "cd /opt/airflow/dbt && dbt --log-path /tmp/dbt-logs seed --profiles-dir /opt/airflow/dbt/profiles"

dbt-run:
	docker compose exec airflow-scheduler bash -c "cd /opt/airflow/dbt && dbt --log-path /tmp/dbt-logs run --profiles-dir /opt/airflow/dbt/profiles"

dbt-test:
	docker compose exec airflow-scheduler bash -c "cd /opt/airflow/dbt && dbt --log-path /tmp/dbt-logs test --profiles-dir /opt/airflow/dbt/profiles"

dbt-snapshot:
	docker compose exec airflow-scheduler bash -c "cd /opt/airflow/dbt && dbt --log-path /tmp/dbt-logs snapshot --profiles-dir /opt/airflow/dbt/profiles"

dbt-docs:
	docker compose exec airflow-scheduler bash -c "cd /opt/airflow/dbt && dbt --log-path /tmp/dbt-logs docs generate --profiles-dir /opt/airflow/dbt/profiles"

show-rfm:
	docker compose exec -T warehouse psql -U postgres -d warehouse -c "SELECT customer_segment, COUNT(*) AS count, ROUND(AVG(lifetime_net_revenue)::numeric, 2) AS avg_revenue, ROUND(SUM(lifetime_net_revenue)::numeric, 2) AS total_revenue FROM gold.mart_customer_segments GROUP BY 1 ORDER BY total_revenue DESC;"

show-products:
	docker compose exec -T warehouse psql -U postgres -d warehouse -c "SELECT product_name, category_name, list_price, avg_selling_price, price_gap, lifetime_units_sold, stock_status FROM gold.mart_product_performance ORDER BY lifetime_units_sold DESC LIMIT 8;"

show-shipping:
	docker compose exec -T warehouse psql -U postgres -d warehouse -c "SELECT company_name, year, total_orders, on_time_shipment_rate, avg_delivery_days, total_freight_paid FROM gold.mart_shipping_performance WHERE year = 1997 ORDER BY total_orders DESC;"

show-reps:
	docker compose exec -T warehouse psql -U postgres -d warehouse -c "SELECT full_name, title, reports_to_name, total_net_revenue, total_orders_handled, avg_order_value, late_shipment_rate FROM gold.mart_employee_performance ORDER BY total_net_revenue DESC;"

show-scd:
	docker compose exec -T warehouse psql -U postgres -d warehouse -c "SELECT product_id, product_name, unit_price, units_in_stock, dbt_valid_from, dbt_valid_to FROM snapshots.products_snapshot LIMIT 8;"

show-counts:
	docker compose exec -T warehouse psql -U postgres -d warehouse -c "SELECT table_name, (xpath('/row/cnt/text()', xml_count))[1]::text::int as row_count FROM (SELECT table_name, query_to_xml(format('select count(*) as cnt from gold.%I', table_name), false, true, '') as xml_count FROM information_schema.tables WHERE table_schema = 'gold') t ORDER BY row_count DESC;"

trigger-dag:
	docker compose exec airflow-scheduler airflow dags trigger northwind_dbt_pipeline

test:
	python -m unittest tests/test_airflow_dags.py -v

lint:
	sqlfluff lint dbt/models --config .sqlfluff
