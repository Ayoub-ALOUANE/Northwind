-- ── Northwind Medallion Architecture Initialization for Snowflake ───────────
-- Execute this script in Snowflake worksheet or via SnowSQL with ACCOUNTADMIN / SYSADMIN role.

-- 1. Create Virtual Warehouse
CREATE WAREHOUSE IF NOT EXISTS COMPUTE_WH
    WITH WAREHOUSE_SIZE = 'XSMALL'
    AUTO_SUSPEND = 60
    AUTO_RESUME = TRUE
    INITIALLY_SUSPENDED = TRUE;

-- 2. Create Analytical Database
CREATE DATABASE IF NOT EXISTS NORTHWIND;
USE DATABASE NORTHWIND;

-- 3. Create Medallion Schemas
CREATE SCHEMA IF NOT EXISTS NORTHWIND.BRONZE;      -- Raw Airbyte-replicated source tables
CREATE SCHEMA IF NOT EXISTS NORTHWIND.SILVER;      -- Cleaned, validated models/views (dbt)
CREATE SCHEMA IF NOT EXISTS NORTHWIND.GOLD;        -- Star schema + analytical marts (dbt)
CREATE SCHEMA IF NOT EXISTS NORTHWIND.SNAPSHOTS;   -- SCD Type 2 history tables (dbt snapshot)
CREATE SCHEMA IF NOT EXISTS NORTHWIND.SEEDS;       -- Reference / lookup tables (dbt seed)
