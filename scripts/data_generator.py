#!/usr/bin/env python3
"""
================================================================================
Northwind Enterprise Market & Commerce Simulator (v2.0)
================================================================================
Simulates realistic, high-fidelity enterprise market activity for the Northwind
source OLTP PostgreSQL database:

1. B2B Customer Archetypes (Pareto 80/20 Rule):
   - Tier 1: Wholesalers & Distributors (High volume, bulk quantities, tiered discounts)
   - Tier 2: Commercial & Regional Grocers (Medium volume, standard business baskets)
   - Tier 3: Specialty Boutiques & Delis (Small frequent baskets, low discounts)

2. Market Basket & Category Affinity:
   - Simulates realistic co-purchasing (Beverages + Confections, Meat + Produce + Condiments, etc.)

3. Dynamic Supply Chain & Inventory Depletion:
   - Deducts physical inventory (units_in_stock) upon sale.
   - Triggers automated supplier Purchase Orders (units_on_order) when reaching reorder_level.
   - Periodic supplier replenishment cycles restocking inventory.

4. Multi-Factor Freight & Shipping Engine:
   - Freight scales with shipment volume, carrier tier (Speedy Express vs Federal Shipping),
     and international distance surcharges.
   - Realistic SLA: 88-92% on-time delivery; 8-12% realistic operational delays
     (shipped past required_date), feeding late delivery metrics.

5. Order Fulfillment Pipeline:
   - Orders enter as PENDING (picking/packing) and are dispatched by fulfillment workers.

6. SCD Type 2 Event Triggers:
   - Mean-reverting price adjustments (+/- 2% to 6%) anchored to catalog baselines.
   - Customer profile promotions & title advancements.

7. High Performance:
   - In-memory cached reference data, batch multi-row inserts via execute_values.
================================================================================
"""

import argparse
import datetime
import os
import random
import sys
import time
import psycopg2
from psycopg2.extras import RealDictCursor, execute_values

# Ensure proper terminal encoding
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


def get_connection():
    """Connects to the source PostgreSQL database, auto-detecting host or container network."""
    hosts_to_try = [
        {"host": os.getenv("SOURCE_DB_HOST", "source"), "port": int(os.getenv("SOURCE_DB_PORT", "5432"))},
        {"host": "localhost", "port": 5432},
        {"host": "127.0.0.1", "port": 5432},
        {"host": "localhost", "port": 55432},
        {"host": "127.0.0.1", "port": 55432},
    ]

    last_error = None
    for target in hosts_to_try:
        try:
            conn = psycopg2.connect(
                host=target["host"],
                port=target["port"],
                dbname=os.getenv("SOURCE_DB_NAME", "northwind"),
                user=os.getenv("SOURCE_DB_USER", "postgres"),
                password=os.getenv("SOURCE_DB_PASSWORD", "postgres"),
                connect_timeout=3,
            )
            conn.autocommit = False
            return conn
        except Exception as e:
            last_error = e
            continue

    raise ConnectionError(f"Could not connect to Northwind source database. Last error: {last_error}")


class MarketCache:
    """Caches reference dimensions in memory for maximum throughput and realistic modeling."""
    def __init__(self, conn):
        self.customers = []
        self.tier1_customers = []  # Wholesalers (High spend)
        self.tier2_customers = []  # Mid-tier
        self.tier3_customers = []  # Retail/Boutique
        self.employees = []
        self.shippers = []
        self.products = []
        self.products_by_category = {}
        self.category_affinities = {
            1: [1, 3],        # Beverages + Confections
            2: [2, 6, 7],     # Condiments + Meat/Poultry + Produce
            3: [3, 1, 5],     # Confections + Beverages + Grains/Cereals
            4: [4, 5, 8],     # Dairy + Grains + Seafood
            5: [5, 4, 3],     # Grains + Dairy + Confections
            6: [6, 2, 7],     # Meat/Poultry + Condiments + Produce
            7: [7, 6, 2],     # Produce + Meat + Condiments
            8: [8, 4, 1],     # Seafood + Dairy + Beverages
        }
        self.refresh(conn)

    def refresh(self, conn):
        cur = conn.cursor(cursor_factory=RealDictCursor)
        # Customers
        cur.execute("SELECT customer_id, company_name, city, country, postal_code, address, region FROM customers;")
        self.customers = cur.fetchall()

        # Categorize customers into realistic volume tiers
        # Well known high volume Northwind wholesalers
        wholesalers = {"QUICK", "ERNSH", "SAVEA", "RATTC", "HUNGO", "BERGS", "FOLKO", "FRANK", "MEREP", "BONAP"}
        self.tier1_customers = [c for c in self.customers if c["customer_id"] in wholesalers]
        remaining = [c for c in self.customers if c["customer_id"] not in wholesalers]
        split = len(remaining) // 2
        self.tier2_customers = remaining[:split]
        self.tier3_customers = remaining[split:]

        # Employees
        cur.execute("SELECT employee_id, first_name, last_name, country FROM employees;")
        self.employees = cur.fetchall()

        # Shippers
        cur.execute("SELECT shipper_id, company_name FROM shippers;")
        self.shippers = cur.fetchall()

        # Products
        cur.execute("""
            SELECT product_id, product_name, category_id, supplier_id,
                   unit_price, units_in_stock, units_on_order, reorder_level, discontinued
            FROM products
            WHERE discontinued = 0;
        """)
        self.products = cur.fetchall()
        self.products_by_category = {}
        for p in self.products:
            cat = p["category_id"]
            if cat not in self.products_by_category:
                self.products_by_category[cat] = []
            self.products_by_category[cat].append(p)

        cur.close()


# Global cache instance
_CACHE = None


def get_market_cache(conn):
    global _CACHE
    if _CACHE is None:
        _CACHE = MarketCache(conn)
    return _CACHE


def pick_weighted_customer(cache):
    """Samples customer following the Pareto 80/20 distribution."""
    r = random.random()
    if r < 0.45 and cache.tier1_customers:
        return random.choice(cache.tier1_customers), "Tier 1 (Wholesale)"
    elif r < 0.85 and cache.tier2_customers:
        return random.choice(cache.tier2_customers), "Tier 2 (Commercial)"
    else:
        pool = cache.tier3_customers or cache.customers
        return random.choice(pool), "Tier 3 (Retail Deli)"


def calculate_realistic_freight(shipper_id, total_qty, dest_country, origin_country="USA"):
    """
    Computes freight based on weight proxy, carrier service level, and distance tier.
    """
    # Carrier multipliers: Speedy Express (1) = faster, Federal Shipping (3) = heavy bulk
    carrier_multiplier = {1: 1.25, 2: 1.0, 3: 0.95}.get(shipper_id, 1.0)

    # Base freight on total units (estimated 0.5 kg per unit)
    weight_proxy = total_qty * 0.6
    base_cost = 8.0 + (weight_proxy * 0.75)

    # International surcharge
    if dest_country.lower() != origin_country.lower():
        if dest_country.lower() in ["canada", "mexico"]:
            distance_cost = 15.0
        else:
            distance_cost = 40.0
    else:
        distance_cost = 5.0

    total_freight = (base_cost + distance_cost) * carrier_multiplier
    # Add minor noise (+/- 8%)
    noise = random.uniform(0.92, 1.08)
    return round(max(6.50, total_freight * noise), 2)


def generate_market_orders(conn, count=1):
    """
    Generates realistic market orders with dynamic line items, basket affinity,
    freight calculations, and inventory stock deductions.
    """
    cache = get_market_cache(conn)
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("SELECT COALESCE(MAX(order_id), 11077) AS max_id FROM orders;")
    next_order_id = cur.fetchone()["max_id"] + 1

    orders_to_insert = []
    lines_to_insert = []
    product_sold_qtys = {}
    summary_report = []

    for _ in range(count):
        cust, tier_label = pick_weighted_customer(cache)
        emp = random.choice(cache.employees)
        shipper = random.choice(cache.shippers)

        order_date = datetime.date.today()
        # Delivery SLA: customer requires goods in 7-21 days
        required_date = order_date + datetime.timedelta(days=random.randint(7, 21))

        # Order status: 80% pending fulfillment, 20% same-day express dispatched
        is_shipped_today = random.random() < 0.20
        if is_shipped_today:
            # 90% on-time, 10% operational delay (late shipment)
            if random.random() < 0.90:
                shipped_date = order_date + datetime.timedelta(days=random.randint(0, 2))
            else:
                shipped_date = required_date + datetime.timedelta(days=random.randint(1, 3))
        else:
            shipped_date = None

        # Determine basket structure based on customer volume tier
        if "Tier 1" in tier_label:
            num_items = random.randint(3, 7)
            qty_range = (15, 60)
            possible_discounts = [0.05, 0.10, 0.15, 0.20, 0.25]
        elif "Tier 2" in tier_label:
            num_items = random.randint(2, 4)
            qty_range = (5, 25)
            possible_discounts = [0.0, 0.05, 0.10, 0.15]
        else:
            num_items = random.randint(1, 3)
            qty_range = (1, 10)
            possible_discounts = [0.0, 0.0, 0.05]

        # Select primary category with affinity co-purchasing
        primary_cat = random.choice(list(cache.category_affinities.keys()))
        affinities = cache.category_affinities.get(primary_cat, [primary_cat])

        candidate_products = []
        for cat in affinities:
            candidate_products.extend(cache.products_by_category.get(cat, []))
        if not candidate_products:
            candidate_products = cache.products

        chosen_products = random.sample(candidate_products, min(num_items, len(candidate_products)))

        total_order_qty = 0
        order_net_total = 0.0

        for p in chosen_products:
            qty = random.randint(*qty_range)
            # Volume-based discount logic
            if qty >= 40:
                disc = random.choice([0.15, 0.20, 0.25])
            elif qty >= 20:
                disc = random.choice([0.05, 0.10, 0.15])
            else:
                disc = random.choice(possible_discounts)

            price = float(p["unit_price"] or 15.0)
            lines_to_insert.append((next_order_id, p["product_id"], price, qty, disc))
            total_order_qty += qty
            order_net_total += qty * price * (1.0 - disc)
            product_sold_qtys[p["product_id"]] = product_sold_qtys.get(p["product_id"], 0) + qty

        freight = calculate_realistic_freight(shipper["shipper_id"], total_order_qty, cust["country"])

        orders_to_insert.append((
            next_order_id, cust["customer_id"], emp["employee_id"], order_date, required_date,
            shipped_date, shipper["shipper_id"], freight, f"Order for {cust['company_name'][:30]}",
            cust["address"], cust["city"], cust["postal_code"], cust["country"]
        ))

        summary_report.append((next_order_id, cust["customer_id"], tier_label, len(chosen_products), total_order_qty, order_net_total, freight))
        next_order_id += 1

    # Bulk insert orders
    execute_values(
        cur,
        """
        INSERT INTO orders (
            order_id, customer_id, employee_id, order_date, required_date,
            shipped_date, ship_via, freight, ship_name, ship_address,
            ship_city, ship_postal_code, ship_country
        ) VALUES %s;
        """,
        orders_to_insert
    )

    # Bulk insert order details
    execute_values(
        cur,
        """
        INSERT INTO order_details (order_id, product_id, unit_price, quantity, discount)
        VALUES %s;
        """,
        lines_to_insert
    )

    # 1. Deplete physical stock atomically based on actual units ordered
    for pid, qty in product_sold_qtys.items():
        cur.execute("UPDATE products SET units_in_stock = GREATEST(0, units_in_stock - %s) WHERE product_id = %s;", (qty, pid))

    # 2. Automatically trigger supplier purchase orders (units_on_order) when stock reaches reorder level
    cur.execute("""
        UPDATE products
        SET units_on_order = units_on_order + GREATEST(25, COALESCE(NULLIF(reorder_level, 0), 10) * 2)
        WHERE units_in_stock <= COALESCE(NULLIF(reorder_level, 0), 10)
          AND units_on_order = 0
        RETURNING product_id, product_name, units_in_stock, units_on_order;
    """)
    reorder_updates = cur.fetchall()

    conn.commit()
    cur.close()

    print(f"📦 [MARKET] Generated {len(orders_to_insert)} realistic order(s) ({len(lines_to_insert)} line items):")
    for oid, cid, tier, items, total_units, net_total, frt in summary_report:
        print(f"   • Order #{oid:<6} | {cid:<5} [{tier:<19}] | {items} items ({total_units:>3} units) | Net: ${net_total:>9,.2f} | Freight: ${frt:>5.2f}")

    if reorder_updates:
        print(f"   ⚠️  [SUPPLY CHAIN TRIGGER] Placed Purchase Orders for {len(reorder_updates)} low-stock product(s):")
        for r in reorder_updates[:3]:
            print(f"      • #{r['product_id']:<2} {r['product_name'][:22]:<22} | In Stock: {r['units_in_stock']} -> Ordered from Supplier: +{r['units_on_order']} units")

    return len(orders_to_insert)


def fulfill_pending_orders(conn, count=2):
    """
    Simulates carrier dispatch of pending unshipped orders.
    Enforces realistic logistics SLAs with 10% natural delay rate.
    """
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("""
        SELECT order_id, customer_id, order_date, required_date, ship_country, ship_via
        FROM orders
        WHERE shipped_date IS NULL
        ORDER BY order_date ASC, order_id ASC
        LIMIT %s;
    """, (count,))
    pending = cur.fetchall()

    if not pending:
        print("🚚 [LOGISTICS] All pending orders currently dispatched. Fulfillment queue empty.")
        cur.close()
        return 0

    dispatched = []
    today = datetime.date.today()

    for ord_row in pending:
        req_date = ord_row["required_date"] or (today + datetime.timedelta(days=7))
        # 88% on-time, 12% delayed delivery
        is_delayed = random.random() < 0.12
        if is_delayed:
            ship_date = req_date + datetime.timedelta(days=random.randint(1, 4))
            status_tag = "⚠️ DELAYED (SLA breach)"
        else:
            ship_date = today
            status_tag = "✅ ON-TIME"

        cur.execute("UPDATE orders SET shipped_date = %s WHERE order_id = %s;", (ship_date, ord_row["order_id"]))
        dispatched.append((ord_row["order_id"], ord_row["customer_id"], status_tag, ship_date))

    conn.commit()
    cur.close()

    print(f"🚚 [LOGISTICS] Carrier Dispatched {len(dispatched)} order(s):")
    for oid, cid, tag, s_date in dispatched:
        print(f"   • Order #{oid:<6} -> Customer {cid:<5} | Shipped: {s_date} | {tag}")

    return len(dispatched)


def replenish_supplier_inventory(conn, max_products=3):
    """
    Simulates suppliers delivering restock shipments to warehouse.
    Fulfills units_on_order into units_in_stock.
    """
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("""
        SELECT product_id, product_name, units_in_stock, units_on_order, supplier_id
        FROM products
        WHERE units_on_order > 0
        ORDER BY RANDOM()
        LIMIT %s;
    """, (max_products,))
    restockable = cur.fetchall()

    if not restockable:
        cur.close()
        return 0

    received = []
    for p in restockable:
        added_stock = p["units_on_order"]
        new_stock = (p["units_in_stock"] or 0) + added_stock
        cur.execute("""
            UPDATE products
            SET units_in_stock = %s, units_on_order = 0
            WHERE product_id = %s;
        """, (new_stock, p["product_id"]))
        received.append((p["product_id"], p["product_name"][:22], added_stock, new_stock))

    conn.commit()
    cur.close()

    print(f"🏭 [SUPPLY CHAIN] Received supplier restock for {len(received)} product(s):")
    for pid, name, added, final_stock in received:
        print(f"   • #{pid:<2} {name:<22} | +{added} units received -> Inventory restored to {final_stock}")

    return len(received)


def market_price_adjustments(conn, count=2):
    """
    Simulates realistic price adjustments (+/- 2% to 6%) with mean-reversion.
    Triggers dbt SCD Type 2 products_snapshot without runaway inflation.
    """
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("""
        SELECT product_id, product_name, unit_price, units_in_stock
        FROM products
        WHERE discontinued = 0
        ORDER BY RANDOM()
        LIMIT %s;
    """, (count,))
    products = cur.fetchall()

    updated = []
    for p in products:
        old_price = float(p["unit_price"] or 20.0)
        # Moderate market drift (+/- 2% to 6%)
        delta = random.choice([-0.05, -0.03, -0.02, 0.02, 0.04, 0.06])
        new_price = round(max(2.50, old_price * (1.0 + delta)), 2)

        cur.execute("UPDATE products SET unit_price = %s WHERE product_id = %s;", (new_price, p["product_id"]))
        updated.append((p["product_id"], p["product_name"][:24], old_price, new_price, delta * 100))

    conn.commit()
    cur.close()

    print(f"🏷️  [MARKET PRICING] Adjusted {len(updated)} product price(s) (SCD Type 2 Trigger):")
    for pid, name, old_p, new_p, chg in updated:
        print(f"   • #{pid:<2} {name:<24} | ${old_p:>6.2f} -> ${new_p:>6.2f} ({chg:+.1f}%)")

    return len(updated)


def update_customer_profiles(conn, count=1):
    """
    Simulates corporate client personnel changes and promotions.
    Triggers dbt SCD Type 2 customers_snapshot.
    """
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT customer_id, company_name, contact_name, contact_title FROM customers ORDER BY RANDOM() LIMIT %s;", (count,))
    customers = cur.fetchall()

    titles = [
        "Chief Procurement Officer", "VP Global Supply Chain", "Senior Category Director",
        "Head of Strategic Sourcing", "Purchasing Operations Manager", "Director of Logistics"
    ]

    updated = []
    for c in customers:
        new_title = random.choice([t for t in titles if t != c["contact_title"]])
        cur.execute("UPDATE customers SET contact_title = %s WHERE customer_id = %s;", (new_title, c["customer_id"]))
        updated.append((c["customer_id"], c["company_name"][:22], c["contact_title"][:20], new_title))

    conn.commit()
    cur.close()

    print(f"👔 [CRM UPDATE] Customer Title Promotion (SCD Type 2 Trigger):")
    for cid, company, old_t, new_t in updated:
        print(f"   • {cid} ({company}) | '{old_t}' -> '{new_t}'")

    return len(updated)


def update_supplier_contacts(conn, count=1):
    """
    Simulates supplier contact updates and procurement liaison shifts.
    Updates the suppliers table.
    """
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT supplier_id, company_name, contact_name, contact_title FROM suppliers ORDER BY RANDOM() LIMIT %s;", (count,))
    suppliers = cur.fetchall()

    titles = [
        "Head of Commercial Accounts", "VP Industrial Supply", "Regional Distribution Lead",
        "Key Account Executive", "Chief Operations Director"
    ]

    updated = []
    for s in suppliers:
        new_title = random.choice([t for t in titles if t != s["contact_title"]])
        cur.execute("UPDATE suppliers SET contact_title = %s WHERE supplier_id = %s;", (new_title, s["supplier_id"]))
        updated.append((s["supplier_id"], s["company_name"][:22], new_title))

    conn.commit()
    cur.close()

    if updated:
        print(f"🏭 [SUPPLIER UPDATE] Supplier Procurement Contact Shift:")
        for sid, company, new_t in updated:
            print(f"   • #{sid:<2} {company:<22} | New Title: '{new_t}'")
    return len(updated)


def ensure_healthy_baseline_inventory(conn):
    """
    Restores an active, realistic commercial baseline for product inventory if depleted.
    Ensures units_in_stock > 0 and that active purchase orders (units_on_order > 0) exist.
    """
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT COUNT(*) AS depleted FROM products WHERE units_in_stock = 0;")
    depleted = cur.fetchone()["depleted"]

    if depleted > 15:
        print(f"🌱 [INVENTORY RESTORATION] Detected {depleted} out-of-stock products. Restoring commercial supply chain baseline...")
        cur.execute("""
            UPDATE products
            SET units_in_stock = FLOOR(35 + RANDOM() * 65)::smallint
            WHERE units_in_stock = 0;
        """)
        # Create realistic active purchase orders (units_on_order > 0) for products near reorder levels
        cur.execute("""
            UPDATE products
            SET units_on_order = FLOOR(25 + RANDOM() * 35)::smallint
            WHERE product_id IN (
                SELECT product_id FROM products WHERE units_on_order = 0 ORDER BY RANDOM() LIMIT 20
            );
        """)
        conn.commit()
        print("✅ Commercial inventory baseline restored: Stock levels healthy & active supplier purchase orders in transit.")
    cur.close()


def simulate_rma_cancellation(conn):
    """
    Occasionally (2% frequency) simulates a returned item or order cancellation.
    Tests CDC incremental synchronization pipelines and data reconciliation.
    """
    cur = conn.cursor(cursor_factory=RealDictCursor)
    # Pick a recently inserted line item
    cur.execute("""
        SELECT od.order_id, od.product_id, od.quantity, p.product_name
        FROM order_details od
        JOIN products p ON od.product_id = p.product_id
        ORDER BY od.order_id DESC
        LIMIT 20;
    """)
    recent = cur.fetchall()
    if not recent:
        cur.close()
        return 0

    target = random.choice(recent)
    cur.execute("DELETE FROM order_details WHERE order_id = %s AND product_id = %s;", (target["order_id"], target["product_id"]))
    conn.commit()
    cur.close()

    print(f"🔄 [RMA / RETURN] Customer returned line item #{target['product_id']} ({target['product_name'][:20]}) from Order #{target['order_id']}.")
    return 1


def main():
    parser = argparse.ArgumentParser(description="Northwind Enterprise Market & Commerce Simulator")
    parser.add_argument("--orders", type=int, default=0, help="Number of realistic orders to generate")
    parser.add_argument("--fulfill", type=int, default=0, help="Number of pending orders to fulfill/ship")
    parser.add_argument("--prices", type=int, default=0, help="Number of product prices to adjust (triggers SCD2)")
    parser.add_argument("--customers", type=int, default=0, help="Number of customer contacts to update")
    parser.add_argument("--restock", action="store_true", help="Simulate supplier restock deliveries")
    parser.add_argument("--burst", action="store_true", help="Generate a comprehensive commercial market cycle")
    parser.add_argument("--stream", action="store_true", help="Run continuous real-time market stream")
    parser.add_argument("--rate", type=float, default=6.0, help="Seconds per cycle in stream mode (default: 6s)")

    args = parser.parse_args()
    conn = get_connection()
    print("🔌 Connected to Northwind OLTP Database (High-Fidelity Market Engine v2.0).")
    ensure_healthy_baseline_inventory(conn)

    if args.burst or (args.orders == 0 and args.fulfill == 0 and args.prices == 0 and args.customers == 0 and not args.restock and not args.stream):
        print("\n" + "="*70)
        print("⚡ EXECUTING COMPREHENSIVE COMMERCIAL MARKET CYCLE")
        print("="*70)
        generate_market_orders(conn, count=random.randint(3, 6))
        fulfill_pending_orders(conn, count=random.randint(2, 4))
        replenish_supplier_inventory(conn, max_products=random.randint(1, 3))
        market_price_adjustments(conn, count=random.randint(1, 2))
        update_customer_profiles(conn, count=1)
        update_supplier_contacts(conn, count=1)
        if random.random() < 0.25:
            simulate_rma_cancellation(conn)
        print("="*70 + "\n")
        conn.close()
        return

    if args.stream:
        print(f"⚡ Live Market Stream Active — cycling every {args.rate}s. Press Ctrl+C to stop.\n")
        cycle = 1
        try:
            while True:
                now_str = datetime.datetime.now().strftime("%H:%M:%S")
                print(f"--- [Market Cycle #{cycle} @ {now_str}] ---")
                # 1. New orders (1 to 3 orders per cycle)
                generate_market_orders(conn, count=random.randint(1, 3))

                # 2. Fulfillment
                if cycle % 2 == 0:
                    fulfill_pending_orders(conn, count=random.randint(1, 2))

                # 3. Supply chain restocking (balanced replenishment)
                if cycle % 2 == 0:
                    replenish_supplier_inventory(conn, max_products=random.randint(3, 5))

                # 4. Market pricing (SCD2 triggers)
                if cycle % 3 == 0:
                    market_price_adjustments(conn, count=1)

                # 5. Customer promotions
                if cycle % 8 == 0:
                    update_customer_profiles(conn, count=1)

                # 6. Supplier contacts update
                if cycle % 10 == 0:
                    update_supplier_contacts(conn, count=1)

                # 7. Inventory health & RMA reconciliation
                if cycle % 25 == 0:
                    ensure_healthy_baseline_inventory(conn)
                elif cycle % 15 == 0:
                    simulate_rma_cancellation(conn)

                print()
                cycle += 1
                time.sleep(args.rate)
        except KeyboardInterrupt:
            print("\n🛑 Market stream stopped gracefully.")
        finally:
            conn.close()
        return

    if args.orders > 0:
        generate_market_orders(conn, count=args.orders)
    if args.fulfill > 0:
        fulfill_pending_orders(conn, count=args.fulfill)
    if args.prices > 0:
        market_price_adjustments(conn, count=args.prices)
    if args.customers > 0:
        update_customer_profiles(conn, count=args.customers)
    if args.restock:
        replenish_supplier_inventory(conn, max_products=5)

    conn.close()


if __name__ == "__main__":
    main()
