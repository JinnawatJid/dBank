#!/bin/bash
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    -- 1. Create schemas and extensions
    CREATE SCHEMA IF NOT EXISTS raw;
    CREATE SCHEMA IF NOT EXISTS marts;
    CREATE SCHEMA IF NOT EXISTS snapshots;
    CREATE EXTENSION IF NOT EXISTS pgcrypto;

    -- 2. Create the dbt user (has read/write on analytics schemas)
    DO \$\$ BEGIN
        IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = '$DBT_USER') THEN
            CREATE USER $DBT_USER WITH PASSWORD '$DBT_PASSWORD';
        ELSE
            ALTER USER $DBT_USER WITH PASSWORD '$DBT_PASSWORD';
        END IF;
    END \$\$;
    GRANT CONNECT ON DATABASE $POSTGRES_DB TO $DBT_USER;

    -- dbt needs read access to raw data
    GRANT USAGE ON SCHEMA raw TO $DBT_USER;
    GRANT SELECT ON ALL TABLES IN SCHEMA raw TO $DBT_USER;
    ALTER DEFAULT PRIVILEGES IN SCHEMA raw GRANT SELECT ON TABLES TO $DBT_USER;

    -- dbt needs write access to its target schemas
    GRANT ALL ON SCHEMA marts TO $DBT_USER;
    GRANT ALL ON SCHEMA snapshots TO $DBT_USER;

    -- 3. Create the app user (strict read-only, NO access to raw)
    DO \$\$ BEGIN
        IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = '$APP_USER') THEN
            CREATE USER $APP_USER WITH PASSWORD '$APP_PASSWORD';
        ELSE
            ALTER USER $APP_USER WITH PASSWORD '$APP_PASSWORD';
        END IF;
    END \$\$;
    GRANT CONNECT ON DATABASE $POSTGRES_DB TO $APP_USER;

    -- App user only gets access to transformed/masked data in the marts schema
    GRANT USAGE ON SCHEMA marts TO $APP_USER;
    GRANT SELECT ON ALL TABLES IN SCHEMA marts TO $APP_USER;
    ALTER DEFAULT PRIVILEGES FOR USER $DBT_USER IN SCHEMA marts GRANT SELECT ON TABLES TO $APP_USER;
EOSQL
