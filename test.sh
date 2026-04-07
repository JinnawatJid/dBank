#!/bin/bash
export DBT_USER=myuser
export DBT_PASSWORD=mypass
cat <<-EOSQL
    DO \$\$ BEGIN
        IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = '$DBT_USER') THEN
            CREATE USER $DBT_USER WITH PASSWORD '$DBT_PASSWORD';
        ELSE
            ALTER USER $DBT_USER WITH PASSWORD '$DBT_PASSWORD';
        END IF;
    END \$\$;
EOSQL
