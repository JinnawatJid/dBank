# Deep Insights Copilot

This repository contains the solution for the dData Mission Engineer Interview exercise.

## Project Structure

*   `backend/`: FastAPI backend and MCP server logic.
*   `frontend/`: Next.js web application for the UI.
*   `data/`: Raw data (`data/raw/`) and Markdown files for the Knowledge Base (`data/kb/`).
*   `scripts/`: Python scripts for synthetic data generation and embedding ingestion.
*   `docs/`: Architecture diagrams, execution plans, and requirements specifications.

Please see `docs/PROJECT_PLAN.md` and `docs/TASKS.md` for execution details.

## Quick Start

### 1. Environment Setup

Copy the example environment file to `.env`:

```bash
cp .env.example .env
```

Open `.env` and fill in your `GOOGLE_API_KEY` (required for Knowledge Base embeddings and LLM features).

### 2. Run with Docker Compose

Ensure Docker and Docker Compose are installed on your machine. Start the entire application stack by running:

```bash
docker compose up --build -d
```

This will build and spin up the following services:
*   **Database (PostgreSQL + pgvector)**: Running on port `5432`
*   **Backend (FastAPI)**: Running on port `8000` (Access the Swagger UI at `http://localhost:8000/docs`)
*   **Frontend (Next.js)**: Running on port `3000` (Access the web application at `http://localhost:3000`)

### 3. Stop the Application

To shut down the services, run:

```bash
docker compose down
```