# Deployment Guide

## 1. Deployment Objective

The application is intentionally deployable in three modes:

- local demo mode
- containerized pilot mode
- production-ready target architecture

## 2. Local Deployment

### Backend

```powershell
uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```

### Frontend

```powershell
python -m http.server 5500 --directory frontend
```

### Expected URLs

- API: `http://127.0.0.1:8000`
- Dashboard: `http://127.0.0.1:5500/dashboard.html`
- Deck: open `presentation/reactive_pm_intelligence_deck.html`

## 3. Environment Variables

Primary runtime variables:

- `DATABASE_URL`
- `API_TOKEN`
- `FRONTEND_ORIGIN`
- `RATE_LIMIT_PER_MINUTE`
- `PM_PROBABILITY_THRESHOLD`
- `LLM_PROVIDER`
- `LLM_MODEL`
- `LLM_API_KEY`
- `LLM_BASE_URL`
- `LLM_TIMEOUT_SECONDS`

Example `.env`:

```env
DATABASE_URL=sqlite:///data/reactive_pm.db
API_TOKEN=innovate2026-demo-token
FRONTEND_ORIGIN=http://127.0.0.1:5500
LLM_PROVIDER=mock
LLM_MODEL=gemini-2.0-flash
```

## 4. Docker Deployment

The repository already includes:

- `deployment/Dockerfile.backend`
- `deployment/Dockerfile.frontend`
- `deployment/docker-compose.yml`

Recommended pilot run:

```powershell
cd deployment
docker compose up --build
```

Pilot container responsibilities:

- backend container serves FastAPI
- frontend container serves dashboard and deck assets
- compose network wires the experience and API together

## 5. Kubernetes Deployment

Provided manifests:

- `deployment/k8s/deployment.yaml`
- `deployment/k8s/service.yaml`

Recommended production additions:

- ingress
- HPA
- ConfigMaps for non-secret settings
- Secrets for API tokens and LLM keys
- separate worker deployment for scheduler and batch pipeline jobs

## 6. Deployment Topologies

### Pilot Topology

- one backend container
- one frontend container
- SQLite volume or mounted data directory

### Enterprise Topology

- scalable API deployment
- PostgreSQL database
- Redis cache and distributed limiter
- asynchronous worker tier
- observability stack
- secret management and CI/CD governed release process

## 7. Release Sequence

1. build and tag application artifacts
2. deploy backend
3. deploy frontend
4. validate `/health`
5. run pipeline validation
6. smoke-test dashboard and assistant
7. publish executive deck assets if required

## 8. Production Hardening Checklist

- replace SQLite with PostgreSQL
- move auth to enterprise identity
- externalize all secrets
- add request tracing and centralized logs
- add metrics and alerting
- isolate scheduler from request-serving nodes
- implement PM approval workflow before downstream publication

## 9. Rollback Strategy

- keep previous backend image tag available
- keep previous frontend static artifact available
- version model artifacts separately from code deploys
- disable PM generation route if scoring quality regresses

## 10. Operational Validation

Post-deploy validation sequence:

```powershell
Invoke-RestMethod -Method Get -Uri "http://127.0.0.1:8000/"
Invoke-RestMethod -Method Get -Uri "http://127.0.0.1:8000/api/v1/health"
```

Then obtain a token and run:

- `POST /api/v1/pipeline/run`
- `GET /api/v1/dashboard/kpis`
- `GET /api/v1/portfolio/overview`
- `POST /api/v1/assistant/chat`