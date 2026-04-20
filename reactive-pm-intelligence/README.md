# Reactive to PM Intelligence

Reactive to PM Intelligence converts reactive maintenance history into predictive maintenance action. The solution ingests work-order history, detects repeat-failure signatures, predicts recurrence risk, auto-generates PM schedules, and exposes the resulting intelligence through a protected FastAPI backend, a live dashboard, and an executive HTML deck designed for SLT storytelling.

This repository is structured as a pilot-to-production blueprint for CBRE-style smart facilities operations.

## What This Repository Contains

- A working FastAPI backend for ingestion, analytics, PM generation, portfolio views, and assistant interactions.
- A static dashboard for operational users.
- A premium executive HTML deck with embedded application screenshots.
- Synthetic but realistic demo data and schema seeds.
- Engineering documentation, business documentation, architecture diagrams, and OpenAPI documentation.
- Tests covering API and intelligence services.

## Start Here

If you are opening this repository for the first time, use this reading order:

1. Read this `README.md` for the repo map and navigation guide.
2. Read `docs/SETUP_GUIDE.md` to run the solution locally.
3. Open `frontend/dashboard.html` after the backend is running to see the live product.
4. Open `docs/APPLICATION_OVERVIEW.html` for a polished product-level summary.
5. Open `docs/ARCHITECTURE.md` and `docs/diagrams/` to understand the design.
6. Open `docs/openapi.yaml` or `docs/API_REFERENCE.html` to understand the API surface.
7. Open `presentation/reactive_pm_intelligence_deck.html` for the SLT presentation.

## Quick Navigation By Persona

### If You Want To Run The App

- Setup guide: `docs/SETUP_GUIDE.md`
- Backend entry point: `backend/main.py`
- Dashboard: `frontend/dashboard.html`
- Demo data generator: `data/generate_demo_data.py`

### If You Want To Understand The Product Quickly

- Product overview: `docs/APPLICATION_OVERVIEW.html`
- SLT brief: `docs/SLT_USECASE_BRIEF.html`
- Business case: `docs/BUSINESS_CASE.md`
- Executive deck: `presentation/reactive_pm_intelligence_deck.html`

### If You Want To Understand The Architecture

- Architecture narrative: `docs/ARCHITECTURE.md`
- Application design: `docs/APPLICATION_DESIGN.html`
- System diagrams: `docs/diagrams/system-architecture.drawio`
- Service relationships: `docs/diagrams/service-class-diagram.drawio`
- Intelligence pipeline flow: `docs/diagrams/intelligence-flow.drawio`
- Business flow: `docs/diagrams/business-value-flow.drawio`

### If You Want To Understand The APIs

- OpenAPI 3.0.3 contract: `docs/openapi.yaml`
- HTML API documentation: `docs/API_REFERENCE.html`
- Markdown API reference: `docs/API_REFERENCE.md`
- FastAPI routes: `backend/api/routes.py`
- Pydantic schemas: `backend/models/schemas.py`

### If You Want To Understand The Data Model

- Database design: `docs/DATABASE_DESIGN.md`
- Schema design: `docs/SCHEMA_DESIGN.md`
- SQL seed schema: `data/schema.sql`
- ORM models: `backend/models/database.py`

### If You Want To Understand The Intelligence Logic

- Pattern engine: `backend/services/pattern_engine.py`
- Prediction engine: `backend/services/prediction_engine.py`
- PM generator: `backend/services/pm_generator.py`
- Portfolio rollups: `backend/services/portfolio_service.py`
- Assistant orchestration: `backend/services/assistant_service.py`
- Model documentation: `docs/ML_MODEL_CARD.md`

## Solution Summary

### Executive Summary

- Outcome: convert repeat breakdown data into ranked PM opportunities and leadership-ready operational insight.
- Core value: reduce avoidable reactive workload, improve tenant experience, and give planners a defensible PM backlog.
- Delivery form: end-to-end working product including data generation, persistence, analytics, APIs, UI, assistant, documentation, and deployment assets.
- Demo posture: deterministic by default, with optional live LLM integration for the PM Copilot.

### What The Solution Does

1. Ingests CAFM-like reactive work orders.
2. Builds recurring pattern signatures by asset, location, and problem code.
3. Scores repeatability using interval regularity and operating history.
4. Predicts 30, 60, and 90 day recurrence probability.
5. Auto-generates PM schedules when risk crosses the configured threshold.
6. Publishes operational and executive views through APIs, dashboard, and deck.

### Live Product Scope

- 5,000 synthetic work orders across 50 facilities and 500 assets.
- Facility, asset, and technician reference entities synchronized from work-order history.
- FastAPI application with token-protected endpoints.
- Pattern engine using grouped interval analysis and a Regularity Score.
- Random Forest recurrence model with persisted model artifact.
- PM schedule generator with proactive 85 percent interval buffer.
- Interactive PM Copilot with `mock`, `gemini`, `mistral`, and `openai` provider support.
- Enterprise-style static dashboard and HTML presentation deck.

## Complete Repository Structure

```text
reactive-pm-intelligence/
|-- .env.example
|-- DEMO_SCRIPT.md
|-- README.md
|-- requirements.txt
|-- backend/
|   |-- __init__.py
|   |-- config.py
|   |-- main.py
|   |-- scheduler.py
|   |-- api/
|   |   |-- __init__.py
|   |   `-- routes.py
|   |-- models/
|   |   |-- __init__.py
|   |   |-- database.py
|   |   `-- schemas.py
|   |-- services/
|   |   |-- __init__.py
|   |   |-- assistant_service.py
|   |   |-- ingestion_service.py
|   |   |-- pattern_engine.py
|   |   |-- pm_generator.py
|   |   |-- portfolio_service.py
|   |   `-- prediction_engine.py
|   `-- utils/
|       |-- __init__.py
|       |-- helpers.py
|       `-- logger.py
|-- data/
|   |-- generate_demo_data.py
|   |-- sample_work_orders.csv
|   `-- schema.sql
|-- deployment/
|   |-- docker-compose.yml
|   |-- Dockerfile.backend
|   |-- Dockerfile.frontend
|   `-- k8s/
|       |-- deployment.yaml
|       `-- service.yaml
|-- docs/
|   |-- API_REFERENCE.html
|   |-- API_REFERENCE.md
|   |-- APPLICATION_DESIGN.html
|   |-- APPLICATION_OVERVIEW.html
|   |-- ARCHITECTURE.md
|   |-- BUSINESS_CASE.md
|   |-- DATABASE_DESIGN.md
|   |-- DEPLOYMENT_GUIDE.md
|   |-- ML_MODEL_CARD.md
|   |-- openapi.yaml
|   |-- PRODUCTION_ROADMAP.md
|   |-- SCHEMA_DESIGN.md
|   |-- SETUP_GUIDE.md
|   |-- SLT_USECASE_BRIEF.html
|   `-- diagrams/
|       |-- README.md
|       |-- business-value-flow.drawio
|       |-- intelligence-flow.drawio
|       |-- service-class-diagram.drawio
|       `-- system-architecture.drawio
|-- frontend/
|   |-- dashboard.html
|   |-- assets/
|   |   |-- app.js
|   |   `-- style.css
|   `-- components/
|       |-- heatmap.js
|       |-- kpi_cards.js
|       `-- predictions_table.js
|-- ml/
|   |-- evaluate_model.py
|   |-- train_model.py
|   |-- model_artifacts/
|   `-- notebooks/
|-- presentation/
|   |-- reactive_pm_intelligence_deck.html
|   `-- assets/
|       `-- screenshots/
`-- tests/
    |-- conftest.py
    |-- test_api_routes.py
    |-- test_pattern_engine.py
    |-- test_pm_generator.py
    `-- test_prediction_engine.py
```

## How To Read The Project Structure

The repository is intentionally separated by function so different audiences can move directly to what they need.

### `backend/`

This is the application core.

- `main.py` starts the FastAPI app and lifecycle.
- `api/routes.py` exposes the REST endpoints.
- `models/` contains the ORM and API schema contracts.
- `services/` contains the business and intelligence logic.
- `config.py` centralizes runtime settings including LLM configuration.

Read this folder if you want to understand how the platform works.

### `frontend/`

This is the live operational dashboard.

- `dashboard.html` contains the main page shell.
- `assets/app.js` contains client-side orchestration and assistant behavior.
- `assets/style.css` contains the visual design system.
- `components/` contains modular visualization rendering logic.

Read this folder if you want to understand the user experience.

### `data/`

This is the demo data and seed design layer.

- `generate_demo_data.py` creates realistic synthetic work-order data.
- `sample_work_orders.csv` is the working sample ingestion file.
- `schema.sql` documents the seed-oriented SQL shape.

Read this folder if you want to understand what data the demo runs on.

### `docs/`

This is the documentation hub.

- Markdown files explain engineering, deployment, data model, architecture, and roadmap.
- HTML files provide polished review-ready documents for product, API, design, and SLT use case framing.
- `openapi.yaml` is the machine-readable API contract.
- `diagrams/` contains editable draw.io architecture and flow diagrams.

Read this folder if you want explanation, narrative, and reference material.

### `presentation/`

This is the executive storytelling layer.

- `reactive_pm_intelligence_deck.html` is the SLT-ready presentation.
- `assets/screenshots/` contains live application screenshots embedded in the deck.

Read this folder if you want the business pitch and demo narrative.

### `deployment/`

This contains runtime packaging assets.

- Dockerfiles support backend and frontend packaging.
- `docker-compose.yml` supports local container orchestration.
- `k8s/` contains Kubernetes deployment manifests.

Read this folder if you want to package or deploy the solution.

### `tests/`

This contains the regression safety net for the core flows.

- API behavior tests.
- Pattern detection tests.
- Prediction and PM generation tests.

Read this folder if you want to validate or extend the solution safely.

## Documentation Guide

Use this section when you are unsure which document to open.

| Need | Open |
|---|---|
| Local setup and troubleshooting | `docs/SETUP_GUIDE.md` |
| End-to-end architecture narrative | `docs/ARCHITECTURE.md` |
| API route explanation | `docs/API_REFERENCE.md` |
| Formal API contract | `docs/openapi.yaml` |
| Presentation-friendly API summary | `docs/API_REFERENCE.html` |
| Product summary | `docs/APPLICATION_OVERVIEW.html` |
| Design and runtime explanation | `docs/APPLICATION_DESIGN.html` |
| Executive use case framing | `docs/SLT_USECASE_BRIEF.html` |
| Business value and ROI framing | `docs/BUSINESS_CASE.md` |
| Database structure and indexing | `docs/DATABASE_DESIGN.md` |
| Business and API schemas | `docs/SCHEMA_DESIGN.md` |
| Model purpose, features, and risks | `docs/ML_MODEL_CARD.md` |
| Deployment options | `docs/DEPLOYMENT_GUIDE.md` |
| Scale-up plan | `docs/PRODUCTION_ROADMAP.md` |

## Diagram Guide

All editable diagrams live in `docs/diagrams/`.

| Diagram | Purpose |
|---|---|
| `system-architecture.drawio` | End-to-end platform architecture and component interaction |
| `service-class-diagram.drawio` | Service, model, and route relationships |
| `intelligence-flow.drawio` | Reactive work-order to prediction and PM flow |
| `business-value-flow.drawio` | Operational pain to business-value storyline |
| `README.md` | Diagram inventory and usage notes |

## Slides And Demo Assets

- Executive deck: `presentation/reactive_pm_intelligence_deck.html`
- Demo talking points: `DEMO_SCRIPT.md`
- Embedded screenshots for the deck: `presentation/assets/screenshots/`

If you are presenting the solution, start with the deck and use the dashboard as the live product companion.

## API And Runtime Map

### Main Runtime Endpoints

- Backend base URL: `http://127.0.0.1:8000`
- Frontend local URL: `http://127.0.0.1:5500/dashboard.html`
- Auth token endpoint: `POST /api/v1/auth/token`
- Intelligence pipeline endpoint: `POST /api/v1/pipeline/run`
- Portfolio overview endpoint: `GET /api/v1/portfolio/overview`
- Assistant endpoint: `POST /api/v1/assistant/chat`

### Source Of Truth For API Behavior

- Route implementation: `backend/api/routes.py`
- Request and response schemas: `backend/models/schemas.py`
- OpenAPI contract: `docs/openapi.yaml`

## Quick Start

### Local Run

1. Create and activate a virtual environment.
2. Install dependencies.
3. Generate demo data.
4. Start the FastAPI backend.
5. Serve the frontend through a static file server.
6. Open the dashboard and executive deck.

### Commands

```powershell
cd reactive-pm-intelligence
pip install -r requirements.txt
python data/generate_demo_data.py
uvicorn backend.main:app --reload
```

Serve the frontend with any static host, for example:

```powershell
python -m http.server 5500 --directory frontend
```

Open:

- Dashboard: `http://127.0.0.1:5500/dashboard.html`
- API root: `http://127.0.0.1:8000`
- Executive deck: `presentation/reactive_pm_intelligence_deck.html`

## Authentication

Protected routes use the pilot bearer token. Fetch it with:

```bash
curl -X POST http://127.0.0.1:8000/api/v1/auth/token
```

Default demo token:

```text
innovate2026-demo-token
```

## Optional LLM Setup

The PM Copilot is reliable out of the box in deterministic `mock` mode. To connect a live model, add a `.env` file in the repository root.

Gemini example:

```env
LLM_PROVIDER=gemini
LLM_MODEL=gemini-2.0-flash
LLM_API_KEY=your-gemini-api-key
```

Mistral example:

```env
LLM_PROVIDER=mistral
LLM_MODEL=mistral-small-latest
LLM_API_KEY=your-mistral-api-key
```

OpenAI example:

```env
LLM_PROVIDER=openai
LLM_MODEL=gpt-4.1-mini
LLM_API_KEY=your-openai-api-key
```

Supported providers:

- `mock`
- `gemini`
- `mistral`
- `openai`

## Architecture At A Glance

```text
CAFM-like work orders
  -> ingestion service
  -> SQLite pilot store
  -> pattern engine
  -> recurrence prediction engine
  -> PM generator
  -> FastAPI routes
  -> dashboard, assistant, executive deck
```

## Documentation Set

- `docs/SETUP_GUIDE.md`: workstation setup, environment, local run, troubleshooting.
- `docs/ARCHITECTURE.md`: system context, runtime flow, components, security, and scale view.
- `docs/API_REFERENCE.md`: route-by-route contract documentation.
- `docs/openapi.yaml`: OpenAPI 3.0.3 YAML contract for the API surface.
- `docs/API_REFERENCE.html`: premium HTML API documentation for review and presentation.
- `docs/APPLICATION_OVERVIEW.html`: premium HTML overview of product purpose, users, and outcomes.
- `docs/APPLICATION_DESIGN.html`: premium HTML design narrative across runtime, UX, and system structure.
- `docs/SLT_USECASE_BRIEF.html`: SLT-level HTML use case brief with business-value framing.
- `docs/SCHEMA_DESIGN.md`: business entities, response contracts, and schema decisions.
- `docs/DATABASE_DESIGN.md`: physical data model, indexing, storage strategy, and migration path.
- `docs/DEPLOYMENT_GUIDE.md`: local, Docker, Kubernetes, and production deployment approach.
- `docs/ML_MODEL_CARD.md`: model intent, features, metrics, risks, and governance notes.
- `docs/PRODUCTION_ROADMAP.md`: rollout phases, controls, and scaling roadmap.
- `docs/BUSINESS_CASE.md`: SLT-level ROI framing, value case, trade-offs, and adoption path.
- `docs/diagrams/`: draw.io architecture, class, intelligence flow, and business flow diagrams.

## Key Business Messages

- Reduce reactive maintenance dependence by converting repeat failures into scheduled intervention.
- Improve technician productivity by moving predictable work out of emergency response.
- Protect tenant experience by acting before high-visibility failures recur.
- Give leadership a quantified, explainable pathway from data to savings.

## Validation

Representative validation already included in the repo:

- Data generator for realistic demo workload.
- API tests for health, portfolio, pipeline, and assistant coverage.
- Modular analytics services with deterministic fallback behavior.

## Production Direction

The current implementation is intentionally optimized for pilot demonstration speed and clarity.

Production target direction:

- Replace SQLite with PostgreSQL.
- Move rate limiting to a durable shared store.
- Split scheduler and analytics execution into worker jobs.
- Add model versioning, observability, and approval workflow for PM publication.
- Integrate with live CAFM, BMS, and IoT signals.

## License And Usage

This repository is currently structured as a hackathon and pilot demonstration asset. Review organizational licensing and security requirements before external distribution.