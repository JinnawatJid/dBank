#!/bin/bash
set -e

psql -v ON_ERROR_STOP=1 -h "$POSTGRES_HOST" --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    -- 1. Enable pgvector extension
    CREATE EXTENSION IF NOT EXISTS vector;

    -- 2. Create kb_embeddings table
    CREATE TABLE IF NOT EXISTS public.kb_embeddings (
        id SERIAL PRIMARY KEY,
        filename VARCHAR(255),
        chunk_index INTEGER,
        content TEXT,
        embedding vector(768),
        _ingested_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
    );

    -- 3. Apply Least Privilege: Grant SELECT to APP_USER
    -- $APP_USER is available from environment variables just like in init-user.sh
    GRANT SELECT ON public.kb_embeddings TO $APP_USER;
EOSQL
