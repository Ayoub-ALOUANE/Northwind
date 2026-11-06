#!/bin/bash
set -e

# Background process: wait for PostgreSQL to start up, then launch the live generator
(
  echo "⏳ [Generator] Waiting for PostgreSQL server to become ready..."
  until pg_isready -h localhost -p 5432 -U "${POSTGRES_USER:-postgres}" -d "${POSTGRES_DB:-northwind}" > /dev/null 2>&1; do
    sleep 2
  done
  echo "✅ [Generator] PostgreSQL is ready! Launching OLTP Live Data Generator in stream mode..."
  sleep 5
  python3 -u /opt/generator/data_generator.py --stream
) &

# Execute the official PostgreSQL entrypoint
exec docker-entrypoint.sh "$@"
