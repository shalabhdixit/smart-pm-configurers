# Setup Guide

## Purpose

This guide explains how to stand up Reactive to PM Intelligence locally for engineering, demo rehearsal, and stakeholder walkthroughs.

## Prerequisites

- Python 3.11 or later.
- PowerShell or any shell capable of activating a virtual environment.
- Network access for optional live LLM providers.
- A static file host for the dashboard, such as VS Code Live Server or Python's built-in HTTP server.

## Recommended Local Environment

- OS: Windows, macOS, or Linux.
- Python environment: virtualenv or venv.
- Browser: modern Chromium-based browser for the best dashboard and deck experience.

## Installation

### 1. Create A Virtual Environment

```powershell
python -m venv .venv
```

### 2. Activate It

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

macOS or Linux:

```bash
source .venv/bin/activate
```

### 3. Install Python Dependencies

```powershell
cd reactive-pm-intelligence
pip install -r requirements.txt
```

## Generate Demo Data

The application expects realistic synthetic data to exist before runtime.

```powershell
python data/generate_demo_data.py
```

Generated assets include:

- `data/sample_work_orders.csv`
- `data/reactive_pm.db`
- seed schema artifacts used for documentation and modeling

## Run The Backend

```powershell
uvicorn backend.main:app --reload
```

Expected backend URL:

```text
http://127.0.0.1:8000
```

On startup, the app will:

1. Initialize the database.
2. Load the sample work-order file if present.
3. Synchronize facilities, assets, and technicians.
4. Start the scheduler if not already running.

## Serve The Frontend

Option 1:

```powershell
python -m http.server 5500 --directory frontend
```

Option 2:

- Open `frontend/dashboard.html` using VS Code Live Server.

Expected frontend URL:

```text
http://127.0.0.1:5500/dashboard.html
```

## Run The Demo Flow

1. Open the dashboard.
2. Click `Generate Intelligence`.
3. Wait for the staged loader to complete.
4. Review KPI cards, pattern timeline, top risks, and PM schedules.
5. Use the PM Copilot quick actions or type targeted prompts.
6. Open `presentation/reactive_pm_intelligence_deck.html` for the SLT narrative.

## Authentication Flow

Protected endpoints require a bearer token.

Fetch it with:

```powershell
$token = (Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:8000/api/v1/auth/token").access_token
```

Use it in subsequent calls:

```powershell
Invoke-RestMethod -Method Get -Uri "http://127.0.0.1:8000/api/v1/dashboard/kpis" -Headers @{ Authorization = "Bearer $token" }
```

## Optional LLM Configuration

Create a `.env` file in the repository root.

Example using Gemini:

```env
LLM_PROVIDER=gemini
LLM_MODEL=gemini-2.0-flash
LLM_API_KEY=your-key
```

Example using Mistral:

```env
LLM_PROVIDER=mistral
LLM_MODEL=mistral-small-latest
LLM_API_KEY=your-key
```

If no key is configured, the application uses deterministic `mock` responses for demo reliability.

## Useful Operational Endpoints

- `POST /api/v1/auth/token`
- `GET /api/v1/health`
- `POST /api/v1/pipeline/run`
- `GET /api/v1/dashboard/kpis`
- `GET /api/v1/portfolio/overview`
- `POST /api/v1/assistant/chat`

## Troubleshooting

### Dashboard Loads But Shows No Intelligence

- Ensure the backend is running.
- Click `Generate Intelligence` manually.
- Confirm `POST /api/v1/pipeline/run` succeeds.

### Assistant Returns Fallback Responses

- This is expected in `mock` mode.
- Confirm `.env` exists and includes provider, model, and API key if using a live model.

### Frontend Cannot Reach Backend

- Confirm the backend is on `http://127.0.0.1:8000`.
- Confirm the frontend is served from an allowed origin such as `http://127.0.0.1:5500`.

### Database Appears Empty

- Re-run `python data/generate_demo_data.py`.
- Restart the backend so startup ingestion executes again.

## Demo Readiness Checklist

- Virtual environment active.
- Dependencies installed.
- Sample data regenerated.
- Backend reachable.
- Dashboard reachable.
- Intelligence pipeline successfully runs.
- PM Copilot opens and responds.
- Executive deck opens with embedded screenshots.