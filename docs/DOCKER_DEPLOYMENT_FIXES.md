# Docker Build & Deployment Fixes

This document records the specific issues encountered and resolved during the final Dockerization and local deployment phase.

## 1. Build Failures and Missing Dependencies

### 1.1 Redundant Spacy Download
* **The Issue:** The `backend/Dockerfile` was failing with `exit code: 1` during the `python -m spacy download en_core_web_lg` step.
* **The Fix:** The `spacy` model was already being correctly installed directly from a wheel URL inside `requirements.txt`. The explicit `RUN python -m spacy` command in the Dockerfile was redundant and caused conflicts/timeouts, so it was removed.

### 1.2 Healthcheck Failures (Missing `curl`)
* **The Issue:** The backend container was successfully running but was marked as `unhealthy` by Docker Compose, preventing dependent services (like the frontend) from starting properly.
* **The Fix:** The `docker-compose.yml` healthcheck relies on `curl` to ping the `/docs` endpoint. However, the base image `python:3.11-slim` does not include `curl`. We updated the `apt-get install` list in `backend/Dockerfile` to explicitly install `curl`.

## 2. Configuration and Environment Variables

### 2.1 Postgres Container Crash (Blank Variables)
* **The Issue:** The PostgreSQL database container crashed immediately on startup, failing its healthcheck. The logs showed warnings like `The "POSTGRES_DB" variable is not set`.
* **The Fix:** Docker Compose was not implicitly loading the `.env` file in the user's shell environment. We updated `docker-compose.yml` to include `env_file: - .env` for the `db`, `backend`, and `frontend` services, ensuring credentials and the `GOOGLE_API_KEY` are explicitly passed into the containers.

## 3. Python Module Import Resolution

### 3.1 `ModuleNotFoundError: No module named 'backend'`
* **The Issue:** The backend container crashed with a stack trace indicating it could not import from `backend.api.routes`. This occurred because the `backend/Dockerfile` `WORKDIR` was `/app`, and the `COPY . .` command stripped the `backend/` parent directory. Thus, Python could not resolve absolute imports relying on the `backend` namespace.
* **The Fix:** We updated the `docker-compose.yml` build context for the backend to use the project root directory (`.`). In `backend/Dockerfile`, we adjusted the copy command to `COPY backend /app/backend`, set `ENV PYTHONPATH=/app`, and updated the start command to `uvicorn backend.main:app`. This preserved the module structure and allowed Python to resolve imports perfectly.

## 4. Database Initialization Issues

### 4.1 Missing Executable Files (Windows Line Endings)
* **The Issue:** The Postgres container failed to start and threw the error `/docker-entrypoint-initdb.d/init-kb-schema.sh: cannot execute: required file not found`.
* **The Fix:** When cloned on Windows, git might check out the `.sh` files with CRLF line endings. The Linux Docker container cannot execute shell scripts with CRLF endings. We explicitly enforced LF line endings using `dos2unix` on all files in `db-init/` and ensured `.gitattributes` contained `*.sh text eol=lf`.

### 4.2 Postgres Connection Refused During Startup Initialization
* **The Issue:** The Postgres container skipped creating the database users, and logs showed `psql: error: connection to server at "db" (172.19.0.2), port 5432 failed: Connection refused`. This led to application authentication failures down the line.
* **The Fix:** During the `docker-entrypoint-initdb.d` initialization phase, PostgreSQL runs in local/single-user mode and does not yet listen for TCP/IP network connections. The `psql` command in the initialization scripts was using `-h "$POSTGRES_HOST"`, attempting to connect over the network. We removed the `-h "$POSTGRES_HOST"` argument from `db-init/init-user.sh` and `db-init/init-kb-schema.sh` so that `psql` correctly uses the local Unix socket instead.

## 5. Automated Data Pipeline Orchestration

### 5.1 Missing Database Tables (`relation "marts.fact_tickets" does not exist`)
* **The Issue:** Even after the PostgreSQL database and user roles were successfully initialized, the backend LLM tool executions would fail with `psycopg2.errors.UndefinedTable: relation "marts.fact_tickets" does not exist`. The raw data and dbt transformations had not been executed inside the Docker environment.
* **The Fix:** We introduced a new, ephemeral `dbank_dbt_init` container in `docker-compose.yml`. This container strictly orchestrates the data loading and transformation pipelines. Furthermore, the `backend` container is configured with `depends_on: dbank_dbt_init: condition: service_completed_successfully`, eliminating race conditions by guaranteeing the backend only boots after all database tables are fully populated.

### 5.2 Resolving `dbt` and Data Generator Connection Errors
* **The Issue:** The `dbt_init` container threw `Connection refused` errors when attempting to run `generate_mock_data.py` and `dbt`. Both were hardcoded to connect to `127.0.0.1`. Inside the container, this resolved to the local loopback interface rather than the PostgreSQL `db` container.
* **The Fix:** We updated `scripts/generate_mock_data.py` and `data/dbank_analytics/profiles.yml` to dynamically resolve the `POSTGRES_HOST` environment variable, seamlessly pointing to the `db` container over the Docker network while maintaining fallback compatibility for local sandbox testing.

### 5.3 Strictly Enforcing dbt DAG Execution Order
* **The Issue:** The `dbt_init` container failed during `dbt snapshot` because the `snapshots.customers_snapshot` relation relied on `marts.stg_customers`, which hadn't been built yet.
* **The Fix:** Slowly Changing Dimensions (SCD2) strictly require the staging layer to exist before taking snapshots. We updated the orchestration command to execute the pipeline in the correct topological order:
  1. Generate raw data (`python scripts/generate_mock_data.py`)
  2. Build staging views (`dbt run --select staging`)
  3. Execute snapshots (`dbt snapshot`)
  4. Build fact and dimension marts (`dbt run`)
  5. Generate knowledge base vector embeddings (`python scripts/embed_kb.py`)
