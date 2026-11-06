import os
import json
import urllib.request
from superset.app import create_app

app = create_app()
with app.app_context():
    from superset.extensions import db
    from superset.models.core import Database
    from superset.connectors.sqla.models import SqlaTable, TableColumn, SqlMetric
    from superset.models.slice import Slice
    from superset.models.dashboard import Dashboard

    account = os.environ.get("SNOWFLAKE_ACCOUNT", "")
    user = os.environ.get("SNOWFLAKE_USER", "")
    password = os.environ.get("SNOWFLAKE_PASSWORD", "")
    role = os.environ.get("SNOWFLAKE_ROLE", "ACCOUNTADMIN")
    database_name = os.environ.get("SNOWFLAKE_DATABASE", "NORTHWIND")
    warehouse = os.environ.get("SNOWFLAKE_WAREHOUSE", "COMPUTE_WH")
    schema_name = "GOLD"

    # Snowflake connection URI
    uri = f"snowflake://{user}:{password}@{account}/{database_name}/{schema_name}?warehouse={warehouse}&role={role}"

    db_record = db.session.query(Database).filter_by(database_name="Snowflake Northwind").first()
    if not db_record:
        db_record = Database(
            database_name="Snowflake Northwind",
            sqlalchemy_uri=uri,
            expose_in_sqllab=True,
            allow_run_async=True,
            allow_ctas=True,
            allow_cvas=True,
            allow_dml=False
        )
        db.session.add(db_record)
        db.session.commit()
        print("Database 'Snowflake Northwind' registered.")
    else:
        db_record.sqlalchemy_uri = uri
        db.session.commit()
        print("Database 'Snowflake Northwind' URI verified.")

    # Datasets in Snowflake GOLD schema
    tables = [
        "FACT_SALES",
        "MART_SALES_SUMMARY",
        "MART_CUSTOMER_SEGMENTS",
        "MART_PRODUCT_PERFORMANCE",
        "MART_EMPLOYEE_PERFORMANCE",
        "MART_SHIPPING_PERFORMANCE"
    ]

    registered_datasets = {}
    for tbl_name in tables:
        dataset = db.session.query(SqlaTable).filter_by(database_id=db_record.id, table_name=tbl_name, schema=schema_name).first()
        if not dataset:
            dataset = SqlaTable(
                database_id=db_record.id,
                table_name=tbl_name,
                schema=schema_name
            )
            db.session.add(dataset)
            db.session.commit()
        try:
            dataset.fetch_metadata()
            db.session.commit()
        except Exception as e:
            print(f"Metadata sync notice for {tbl_name}: {e}")
        registered_datasets[tbl_name] = dataset
        print(f"Dataset '{tbl_name}' synchronized (ID: {dataset.id}).")

    fact_sales = registered_datasets["FACT_SALES"]
    mart_sales = registered_datasets["MART_SALES_SUMMARY"]
    mart_cust = registered_datasets["MART_CUSTOMER_SEGMENTS"]
    mart_prod = registered_datasets["MART_PRODUCT_PERFORMANCE"]
    mart_emp = registered_datasets["MART_EMPLOYEE_PERFORMANCE"]
    mart_ship = registered_datasets["MART_SHIPPING_PERFORMANCE"]

    # --------------------------------------------------------------------------
    # 14 High-Impact Executive & Analytical Charts (100% Tested & Snowflake-Aligned)
    # --------------------------------------------------------------------------
    charts_spec = [
        # --- Section 1: Executive KPI Scorecard ---
        {
            "slice_name": "KPI: Total Net Revenue",
            "viz_type": "big_number_total",
            "table": fact_sales,
            "params": {
                "viz_type": "big_number_total",
                "metric": {"expressionType": "SQL", "sqlExpression": "ROUND(SUM(NET_REVENUE), 2)", "label": "Net Revenue ($)"},
                "subheader": "All-Time Net Sales (After Discounts)",
                "adhoc_filters": []
            },
            "queries": [{
                "metrics": [{"expressionType": "SQL", "sqlExpression": "ROUND(SUM(NET_REVENUE), 2)", "label": "Net Revenue ($)"}],
                "filters": []
            }],
            "width": 2, "height": 24
        },
        {
            "slice_name": "KPI: Total Gross Revenue",
            "viz_type": "big_number_total",
            "table": fact_sales,
            "params": {
                "viz_type": "big_number_total",
                "metric": {"expressionType": "SQL", "sqlExpression": "ROUND(SUM(GROSS_REVENUE), 2)", "label": "Gross Revenue ($)"},
                "subheader": "Sales Volume Before Discounts",
                "adhoc_filters": []
            },
            "queries": [{
                "metrics": [{"expressionType": "SQL", "sqlExpression": "ROUND(SUM(GROSS_REVENUE), 2)", "label": "Gross Revenue ($)"}],
                "filters": []
            }],
            "width": 2, "height": 24
        },
        {
            "slice_name": "KPI: Total Orders",
            "viz_type": "big_number_total",
            "table": fact_sales,
            "params": {
                "viz_type": "big_number_total",
                "metric": {"expressionType": "SQL", "sqlExpression": "COUNT(DISTINCT ORDER_ID)", "label": "Total Orders"},
                "subheader": "Completed Customer Orders",
                "adhoc_filters": []
            },
            "queries": [{
                "metrics": [{"expressionType": "SQL", "sqlExpression": "COUNT(DISTINCT ORDER_ID)", "label": "Total Orders"}],
                "filters": []
            }],
            "width": 2, "height": 24
        },
        {
            "slice_name": "KPI: Total Units Sold",
            "viz_type": "big_number_total",
            "table": fact_sales,
            "params": {
                "viz_type": "big_number_total",
                "metric": {"expressionType": "SQL", "sqlExpression": "SUM(QUANTITY)", "label": "Units Sold"},
                "subheader": "Total Physical Units Sold",
                "adhoc_filters": []
            },
            "queries": [{
                "metrics": [{"expressionType": "SQL", "sqlExpression": "SUM(QUANTITY)", "label": "Units Sold"}],
                "filters": []
            }],
            "width": 2, "height": 24
        },
        {
            "slice_name": "KPI: Average Order Value (AOV)",
            "viz_type": "big_number_total",
            "table": fact_sales,
            "params": {
                "viz_type": "big_number_total",
                "metric": {"expressionType": "SQL", "sqlExpression": "ROUND(SUM(NET_REVENUE) / NULLIF(COUNT(DISTINCT ORDER_ID), 0), 2)", "label": "Avg Order Value ($)"},
                "subheader": "Average Net Spend per Order",
                "adhoc_filters": []
            },
            "queries": [{
                "metrics": [{"expressionType": "SQL", "sqlExpression": "ROUND(SUM(NET_REVENUE) / NULLIF(COUNT(DISTINCT ORDER_ID), 0), 2)", "label": "Avg Order Value ($)"}],
                "filters": []
            }],
            "width": 2, "height": 24
        },
        {
            "slice_name": "KPI: Late Shipment Rate",
            "viz_type": "big_number_total",
            "table": fact_sales,
            "params": {
                "viz_type": "big_number_total",
                "metric": {"expressionType": "SQL", "sqlExpression": "ROUND(SUM(CASE WHEN IS_LATE_SHIPMENT = TRUE THEN 1 ELSE 0 END)::NUMERIC / NULLIF(COUNT(*), 0) * 100, 1)", "label": "Late Shipment %"},
                "subheader": "% Orders Delayed Past SLA",
                "adhoc_filters": []
            },
            "queries": [{
                "metrics": [{"expressionType": "SQL", "sqlExpression": "ROUND(SUM(CASE WHEN IS_LATE_SHIPMENT = TRUE THEN 1 ELSE 0 END)::NUMERIC / NULLIF(COUNT(*), 0) * 100, 1)", "label": "Late Shipment %"}],
                "filters": []
            }],
            "width": 2, "height": 24
        },

        # --- Section 2: Financial Evolution & Customer Segmentation ---
        {
            "slice_name": "Monthly Revenue Trends & Evolution",
            "viz_type": "echarts_timeseries_line",
            "table": fact_sales,
            "params": {
                "viz_type": "echarts_timeseries_line",
                "x_axis": "ORDER_DATE_ID",
                "time_grain_sqla": "P1M",
                "metrics": [
                    {"expressionType": "SQL", "sqlExpression": "ROUND(SUM(NET_REVENUE), 2)", "label": "Net Revenue"},
                    {"expressionType": "SQL", "sqlExpression": "ROUND(SUM(GROSS_REVENUE), 2)", "label": "Gross Revenue"}
                ],
                "adhoc_filters": []
            },
            "queries": [{
                "columns": ["ORDER_DATE_ID"],
                "time_grain_sqla": "P1M",
                "metrics": [
                    {"expressionType": "SQL", "sqlExpression": "ROUND(SUM(NET_REVENUE), 2)", "label": "Net Revenue"},
                    {"expressionType": "SQL", "sqlExpression": "ROUND(SUM(GROSS_REVENUE), 2)", "label": "Gross Revenue"}
                ],
                "filters": []
            }],
            "width": 8, "height": 50
        },
        {
            "slice_name": "Customer RFM Segments Share",
            "viz_type": "pie",
            "table": mart_cust,
            "params": {
                "viz_type": "pie",
                "groupby": ["CUSTOMER_SEGMENT"],
                "metric": {"expressionType": "SQL", "sqlExpression": "ROUND(SUM(TOTAL_NET_REVENUE), 2)", "label": "Revenue By Segment"},
                "donut": True,
                "show_legend": True,
                "adhoc_filters": []
            },
            "queries": [{
                "columns": ["CUSTOMER_SEGMENT"],
                "metrics": [{"expressionType": "SQL", "sqlExpression": "ROUND(SUM(TOTAL_NET_REVENUE), 2)", "label": "Revenue By Segment"}],
                "filters": []
            }],
            "width": 4, "height": 50
        },

        # --- Section 3: Category & Geographic Insights ---
        {
            "slice_name": "Revenue & Volume by Product Category",
            "viz_type": "table",
            "table": mart_sales,
            "params": {
                "viz_type": "table",
                "groupby": ["CATEGORY_NAME"],
                "metrics": [
                    {"expressionType": "SQL", "sqlExpression": "ROUND(SUM(TOTAL_NET_REVENUE), 2)", "label": "Total Net Revenue ($)"},
                    {"expressionType": "SQL", "sqlExpression": "SUM(TOTAL_UNITS_SOLD)", "label": "Units Sold"},
                    {"expressionType": "SQL", "sqlExpression": "SUM(TOTAL_ORDERS)", "label": "Orders Handled"},
                    {"expressionType": "SQL", "sqlExpression": "ROUND(AVG(AVG_DISCOUNT_PCT), 2)", "label": "Avg Discount %"}
                ],
                "order_by_cols": ["[\"ROUND(SUM(TOTAL_NET_REVENUE), 2)\", false]"],
                "adhoc_filters": []
            },
            "queries": [{
                "columns": ["CATEGORY_NAME"],
                "metrics": [
                    {"expressionType": "SQL", "sqlExpression": "ROUND(SUM(TOTAL_NET_REVENUE), 2)", "label": "Total Net Revenue ($)"},
                    {"expressionType": "SQL", "sqlExpression": "SUM(TOTAL_UNITS_SOLD)", "label": "Units Sold"},
                    {"expressionType": "SQL", "sqlExpression": "SUM(TOTAL_ORDERS)", "label": "Orders Handled"},
                    {"expressionType": "SQL", "sqlExpression": "ROUND(AVG(AVG_DISCOUNT_PCT), 2)", "label": "Avg Discount %"}
                ],
                "orderby": [[{"expressionType": "SQL", "sqlExpression": "ROUND(SUM(TOTAL_NET_REVENUE), 2)", "label": "Total Net Revenue ($)"}, False]],
                "filters": []
            }],
            "width": 6, "height": 45
        },
        {
            "slice_name": "Top Geographic Markets (By Country)",
            "viz_type": "table",
            "table": mart_sales,
            "params": {
                "viz_type": "table",
                "groupby": ["CUSTOMER_COUNTRY"],
                "metrics": [
                    {"expressionType": "SQL", "sqlExpression": "ROUND(SUM(TOTAL_NET_REVENUE), 2)", "label": "Net Revenue ($)"},
                    {"expressionType": "SQL", "sqlExpression": "SUM(TOTAL_ORDERS)", "label": "Distinct Orders"},
                    {"expressionType": "SQL", "sqlExpression": "SUM(TOTAL_UNITS_SOLD)", "label": "Units Delivered"}
                ],
                "order_by_cols": ["[\"ROUND(SUM(TOTAL_NET_REVENUE), 2)\", false]"],
                "adhoc_filters": []
            },
            "queries": [{
                "columns": ["CUSTOMER_COUNTRY"],
                "metrics": [
                    {"expressionType": "SQL", "sqlExpression": "ROUND(SUM(TOTAL_NET_REVENUE), 2)", "label": "Net Revenue ($)"},
                    {"expressionType": "SQL", "sqlExpression": "SUM(TOTAL_ORDERS)", "label": "Distinct Orders"},
                    {"expressionType": "SQL", "sqlExpression": "SUM(TOTAL_UNITS_SOLD)", "label": "Units Delivered"}
                ],
                "orderby": [[{"expressionType": "SQL", "sqlExpression": "ROUND(SUM(TOTAL_NET_REVENUE), 2)", "label": "Net Revenue ($)"}, False]],
                "row_limit": 15,
                "filters": []
            }],
            "width": 6, "height": 45
        },

        # --- Section 4: Operational Intelligence & Product Performance ---
        {
            "slice_name": "Top Products & Inventory Health Analysis",
            "viz_type": "table",
            "table": mart_prod,
            "params": {
                "viz_type": "table",
                "query_mode": "raw",
                "all_columns": [
                    "PRODUCT_NAME",
                    "CATEGORY_NAME",
                    "STOCK_STATUS",
                    "TOTAL_UNITS_SOLD",
                    "TOTAL_NET_REVENUE",
                    "ACTUAL_AVG_SELLING_PRICE",
                    "PRICE_VS_LIST_GAP"
                ],
                "order_by_cols": ["[\"TOTAL_NET_REVENUE\", false]"],
                "server_page_length": 10,
                "adhoc_filters": []
            },
            "queries": [{
                "columns": [
                    "PRODUCT_NAME",
                    "CATEGORY_NAME",
                    "STOCK_STATUS",
                    "TOTAL_UNITS_SOLD",
                    "TOTAL_NET_REVENUE",
                    "ACTUAL_AVG_SELLING_PRICE",
                    "PRICE_VS_LIST_GAP"
                ],
                "orderby": [["TOTAL_NET_REVENUE", False]],
                "row_limit": 25,
                "filters": []
            }],
            "width": 6, "height": 50
        },
        {
            "slice_name": "Carrier Shipping Performance & Logistics SLAs",
            "viz_type": "table",
            "table": mart_ship,
            "params": {
                "viz_type": "table",
                "groupby": ["SHIPPER_NAME"],
                "metrics": [
                    {"expressionType": "SQL", "sqlExpression": "SUM(TOTAL_SHIPMENTS)", "label": "Total Shipments"},
                    {"expressionType": "SQL", "sqlExpression": "ROUND(AVG(AVG_DAYS_TO_SHIP), 1)", "label": "Avg Delivery Speed (Days)"},
                    {"expressionType": "SQL", "sqlExpression": "ROUND(AVG(LATE_SHIPMENT_RATE_PCT), 1)", "label": "Late Shipment Rate (%)"},
                    {"expressionType": "SQL", "sqlExpression": "ROUND(SUM(TOTAL_FREIGHT_CHARGED), 2)", "label": "Total Freight Cost ($)"}
                ],
                "order_by_cols": ["[\"SUM(TOTAL_SHIPMENTS)\", false]"],
                "adhoc_filters": []
            },
            "queries": [{
                "columns": ["SHIPPER_NAME"],
                "metrics": [
                    {"expressionType": "SQL", "sqlExpression": "SUM(TOTAL_SHIPMENTS)", "label": "Total Shipments"},
                    {"expressionType": "SQL", "sqlExpression": "ROUND(AVG(AVG_DAYS_TO_SHIP), 1)", "label": "Avg Delivery Speed (Days)"},
                    {"expressionType": "SQL", "sqlExpression": "ROUND(AVG(LATE_SHIPMENT_RATE_PCT), 1)", "label": "Late Shipment Rate (%)"},
                    {"expressionType": "SQL", "sqlExpression": "ROUND(SUM(TOTAL_FREIGHT_CHARGED), 2)", "label": "Total Freight Cost ($)"}
                ],
                "orderby": [[{"expressionType": "SQL", "sqlExpression": "SUM(TOTAL_SHIPMENTS)", "label": "Total Shipments"}, False]],
                "filters": []
            }],
            "width": 6, "height": 50
        },

        # --- Section 5: Team Performance & Commercial Leadership ---
        {
            "slice_name": "Sales Rep Leaderboard & Territory Coverage",
            "viz_type": "table",
            "table": mart_emp,
            "params": {
                "viz_type": "table",
                "query_mode": "raw",
                "all_columns": [
                    "FULL_NAME",
                    "TITLE",
                    "REGIONS_COVERED",
                    "TOTAL_ORDERS",
                    "TOTAL_UNITS_SOLD",
                    "TOTAL_NET_REVENUE",
                    "AVG_ORDER_VALUE",
                    "AVG_MONTHLY_REVENUE",
                    "LATE_SHIPMENT_RATE_PCT"
                ],
                "order_by_cols": ["[\"TOTAL_NET_REVENUE\", false]"],
                "adhoc_filters": []
            },
            "queries": [{
                "columns": [
                    "FULL_NAME",
                    "TITLE",
                    "REGIONS_COVERED",
                    "TOTAL_ORDERS",
                    "TOTAL_UNITS_SOLD",
                    "TOTAL_NET_REVENUE",
                    "AVG_ORDER_VALUE",
                    "AVG_MONTHLY_REVENUE",
                    "LATE_SHIPMENT_RATE_PCT"
                ],
                "orderby": [["TOTAL_NET_REVENUE", False]],
                "row_limit": 20,
                "filters": []
            }],
            "width": 12, "height": 45
        },
        {
            "slice_name": "Discount Tier Impact & Volume",
            "viz_type": "table",
            "table": fact_sales,
            "params": {
                "viz_type": "table",
                "groupby": ["DISCOUNT_TIER"],
                "metrics": [
                    {"expressionType": "SQL", "sqlExpression": "COUNT(*)", "label": "Order Lines"},
                    {"expressionType": "SQL", "sqlExpression": "ROUND(SUM(GROSS_REVENUE), 2)", "label": "Gross Revenue ($)"},
                    {"expressionType": "SQL", "sqlExpression": "ROUND(SUM(NET_REVENUE), 2)", "label": "Net Revenue ($)"},
                    {"expressionType": "SQL", "sqlExpression": "ROUND(SUM(DISCOUNT_AMOUNT), 2)", "label": "Total Discounts ($)"}
                ],
                "order_by_cols": ["[\"ROUND(SUM(NET_REVENUE), 2)\", false]"],
                "adhoc_filters": []
            },
            "queries": [{
                "columns": ["DISCOUNT_TIER"],
                "metrics": [
                    {"expressionType": "SQL", "sqlExpression": "COUNT(*)", "label": "Order Lines"},
                    {"expressionType": "SQL", "sqlExpression": "ROUND(SUM(GROSS_REVENUE), 2)", "label": "Gross Revenue ($)"},
                    {"expressionType": "SQL", "sqlExpression": "ROUND(SUM(NET_REVENUE), 2)", "label": "Net Revenue ($)"},
                    {"expressionType": "SQL", "sqlExpression": "ROUND(SUM(DISCOUNT_AMOUNT), 2)", "label": "Total Discounts ($)"}
                ],
                "orderby": [[{"expressionType": "SQL", "sqlExpression": "ROUND(SUM(NET_REVENUE), 2)", "label": "Net Revenue ($)"}, False]],
                "filters": []
            }],
            "width": 12, "height": 38
        }
    ]

    slices = []
    slice_layout_info = []

    for spec in charts_spec:
        slc = db.session.query(Slice).filter_by(slice_name=spec["slice_name"]).first()
        if not slc:
            slc = Slice(slice_name=spec["slice_name"])
            db.session.add(slc)

        slc.viz_type = spec["viz_type"]
        slc.datasource_type = "table"
        slc.datasource_id = spec["table"].id

        spec["params"]["datasource"] = f"{spec['table'].id}__table"
        slc.params = json.dumps(spec["params"])

        # Precompute query_context so Superset 6.x Chart Data API succeeds instantly without 400 errors
        qc = {
            "datasource": {"id": spec["table"].id, "type": "table"},
            "force": False,
            "queries": spec["queries"],
            "result_format": "json",
            "result_type": "full"
        }
        slc.query_context = json.dumps(qc)
        db.session.commit()
        slices.append(slc)
        slice_layout_info.append({
            "id": slc.id,
            "name": spec["slice_name"],
            "width": spec["width"],
            "height": spec["height"]
        })
        print(f"Chart '{spec['slice_name']}' synchronized (ID: {slc.id}).")

    # --------------------------------------------------------------------------
    # Build Production Grid Position Layout (12-Column Responsive Dashboard)
    # --------------------------------------------------------------------------
    # Layout Structure:
    # Row 1: 6 KPI Cards (each 2 cols = 12)
    # Row 2: Monthly Trends (8 cols) + RFM Segments (4 cols) = 12
    # Row 3: Category Performance (6 cols) + Top Markets (6 cols) = 12
    # Row 4: Top Products (6 cols) + Carrier Shipping (6 cols) = 12
    # Row 5: Employee Leaderboard (12 cols)
    # Row 6: Discount Tier Impact (12 cols)

    position_dict = {
        "DASHBOARD_VERSION_KEY": "v2",
        "ROOT_ID": {
            "type": "ROOT",
            "id": "ROOT_ID",
            "children": ["GRID_ID"]
        },
        "GRID_ID": {
            "type": "GRID",
            "id": "GRID_ID",
            "children": [
                "ROW_KPIS",
                "ROW_TRENDS",
                "ROW_MARKETS",
                "ROW_OPS",
                "ROW_TEAM",
                "ROW_DISCOUNTS"
            ],
            "parents": ["ROOT_ID"]
        },
        "ROW_KPIS": {
            "type": "ROW",
            "id": "ROW_KPIS",
            "children": [f"CHART_{s['id']}" for s in slice_layout_info[0:6]],
            "meta": {"background": "BACKGROUND_TRANSPARENT"},
            "parents": ["ROOT_ID", "GRID_ID"]
        },
        "ROW_TRENDS": {
            "type": "ROW",
            "id": "ROW_TRENDS",
            "children": [f"CHART_{s['id']}" for s in slice_layout_info[6:8]],
            "meta": {"background": "BACKGROUND_TRANSPARENT"},
            "parents": ["ROOT_ID", "GRID_ID"]
        },
        "ROW_MARKETS": {
            "type": "ROW",
            "id": "ROW_MARKETS",
            "children": [f"CHART_{s['id']}" for s in slice_layout_info[8:10]],
            "meta": {"background": "BACKGROUND_TRANSPARENT"},
            "parents": ["ROOT_ID", "GRID_ID"]
        },
        "ROW_OPS": {
            "type": "ROW",
            "id": "ROW_OPS",
            "children": [f"CHART_{s['id']}" for s in slice_layout_info[10:12]],
            "meta": {"background": "BACKGROUND_TRANSPARENT"},
            "parents": ["ROOT_ID", "GRID_ID"]
        },
        "ROW_TEAM": {
            "type": "ROW",
            "id": "ROW_TEAM",
            "children": [f"CHART_{slice_layout_info[12]['id']}"],
            "meta": {"background": "BACKGROUND_TRANSPARENT"},
            "parents": ["ROOT_ID", "GRID_ID"]
        },
        "ROW_DISCOUNTS": {
            "type": "ROW",
            "id": "ROW_DISCOUNTS",
            "children": [f"CHART_{slice_layout_info[13]['id']}"],
            "meta": {"background": "BACKGROUND_TRANSPARENT"},
            "parents": ["ROOT_ID", "GRID_ID"]
        }
    }

    # Add each chart node to the position dict
    for s_info in slice_layout_info:
        node_id = f"CHART_{s_info['id']}"
        position_dict[node_id] = {
            "type": "CHART",
            "id": node_id,
            "children": [],
            "meta": {
                "chartId": s_info["id"],
                "width": s_info["width"],
                "height": s_info["height"],
                "sliceName": s_info["name"]
            }
        }

    dash = db.session.query(Dashboard).filter_by(dashboard_title="Northwind Executive Analytics (Snowflake)").first()
    if not dash:
        dash = Dashboard(
            dashboard_title="Northwind Executive Analytics (Snowflake)",
            slug="northwind-executive-analytics",
            published=True
        )
        db.session.add(dash)
        db.session.commit()

    dash.slices = slices
    dash.position_json = json.dumps(position_dict)
    dash.json_metadata = json.dumps({
        "color_scheme": "supersetColors",
        "refresh_frequency": 0,
        "expanded_slices": {},
        "label_colors": {},
        "timed_refresh_immune_slices": []
    })
    dash.published = True
    db.session.commit()
    print("Dashboard 'Northwind Executive Analytics (Snowflake)' published with complete grid layout!")

# --------------------------------------------------------------------------
# Automated Verification: Test REST API GET /api/v1/chart/{id}/data/ for 100% of charts
# --------------------------------------------------------------------------
print("\n" + "="*70)
print("RUNNING 100% VERIFICATION CHECK ACROSS ALL DASHBOARD CHARTS")
print("="*70)

login_payload = json.dumps({'username': 'admin', 'password': 'admin', 'provider': 'db', 'refresh': True}).encode('utf-8')
req = urllib.request.Request('http://localhost:8088/api/v1/security/login', data=login_payload, headers={'Content-Type': 'application/json'})
resp = urllib.request.urlopen(req)
token = json.loads(resp.read().decode('utf-8'))['access_token']
headers = {'Authorization': f'Bearer {token}'}

failed_count = 0
for s_info in slice_layout_info:
    cid = s_info["id"]
    cname = s_info["name"]
    url = f"http://localhost:8088/api/v1/chart/{cid}/data/"
    try:
        r = urllib.request.urlopen(urllib.request.Request(url, headers=headers))
        data = json.loads(r.read().decode('utf-8'))
        results = data.get('result', [])
        err = results[0].get('error') if results else None
        status = results[0].get('status') if results else 'unknown'
        rows = len(results[0].get('data', [])) if results else 0
        if err or status != 'success':
            print(f"❌ [FAIL] Chart {cid} '{cname}': status={status}, err={err}")
            failed_count += 1
        else:
            print(f"✅ [100% OK] Chart {cid} '{cname}': {rows} rows returned (HTTP {r.status})")
    except Exception as e:
        print(f"❌ [EXCEPTION] Chart {cid} '{cname}': {e}")
        failed_count += 1

print("="*70)
if failed_count == 0:
    print(f"🎉 ALL {len(slice_layout_info)} CHARTS FUNCTION 100% PERFECTLY IN SUPERSET!")
else:
    print(f"⚠️ {failed_count} charts encountered an issue during verification.")
print("="*70)
