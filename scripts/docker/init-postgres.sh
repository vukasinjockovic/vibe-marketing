#!/bin/bash
# Creates the database Convex expects (derived from INSTANCE_NAME).
# Mounted into postgres container via docker-compose.yml at
# /docker-entrypoint-initdb.d/ — runs automatically on first boot only.
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<-EOSQL
    CREATE DATABASE vibe_marketing OWNER $POSTGRES_USER;
EOSQL
