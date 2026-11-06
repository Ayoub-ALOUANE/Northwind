-- ── Medallion Layers ─────────────────────────────────────────────────────────
CREATE SCHEMA IF NOT EXISTS bronze;     -- Raw Airbyte-replicated source tables
CREATE SCHEMA IF NOT EXISTS silver;     -- Cleaned, validated views (dbt)
CREATE SCHEMA IF NOT EXISTS gold;       -- Star schema + analytical marts (dbt)

-- ── Supporting Schemas ───────────────────────────────────────────────────────
CREATE SCHEMA IF NOT EXISTS snapshots;  -- SCD Type 2 history tables (dbt snapshot)
CREATE SCHEMA IF NOT EXISTS seeds;      -- Reference/lookup tables (dbt seed)
