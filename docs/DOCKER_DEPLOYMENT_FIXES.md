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
