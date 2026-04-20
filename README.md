# Smart PM Configurers

Smart PM Configurers is the repository wrapper for the Reactive to PM Intelligence solution.

The main application, documentation, diagrams, API contract, dashboard, and executive presentation live inside the `reactive-pm-intelligence/` folder.

## Repository Entry Point

Start here:

- Main project guide: `reactive-pm-intelligence/README.md`

## What Is Inside This Repository

- `.github/`: Copilot agent assets, prompts, skills, and supporting repo-level materials.
- `AGENT.md`: master agent contract used to generate and evolve the solution.
- `reactive-pm-intelligence/`: complete product codebase and documentation set.

## Main Solution Navigation

Inside `reactive-pm-intelligence/` you will find:

- `backend/`: FastAPI backend, services, schemas, scheduler, and data models.
- `frontend/`: dashboard UI, styling, and visualization components.
- `data/`: synthetic demo data generator, sample CSV, and SQL seed schema.
- `docs/`: architecture, API docs, HTML documentation, database and schema docs, roadmap, and business case.
- `docs/diagrams/`: editable draw.io architecture, flow, and class diagrams.
- `presentation/`: executive HTML deck and embedded screenshots.
- `deployment/`: Docker, Compose, Kubernetes, and CI/CD assets.
- `tests/`: API and analytics test coverage.

## Recommended Reading Order

1. `reactive-pm-intelligence/README.md`
2. `reactive-pm-intelligence/docs/SETUP_GUIDE.md`
3. `reactive-pm-intelligence/docs/APPLICATION_OVERVIEW.html`
4. `reactive-pm-intelligence/docs/ARCHITECTURE.md`
5. `reactive-pm-intelligence/docs/openapi.yaml`
6. `reactive-pm-intelligence/presentation/reactive_pm_intelligence_deck.html`

## Key Assets

- Main README: `reactive-pm-intelligence/README.md`
- Setup guide: `reactive-pm-intelligence/docs/SETUP_GUIDE.md`
- OpenAPI contract: `reactive-pm-intelligence/docs/openapi.yaml`
- HTML API docs: `reactive-pm-intelligence/docs/API_REFERENCE.html`
- Application overview: `reactive-pm-intelligence/docs/APPLICATION_OVERVIEW.html`
- Application design: `reactive-pm-intelligence/docs/APPLICATION_DESIGN.html`
- SLT brief: `reactive-pm-intelligence/docs/SLT_USECASE_BRIEF.html`
- Executive deck: `reactive-pm-intelligence/presentation/reactive_pm_intelligence_deck.html`

## Local Run

```powershell
cd reactive-pm-intelligence
pip install -r requirements.txt
python data/generate_demo_data.py
uvicorn backend.main:app --reload
```

Serve the dashboard separately:

```powershell
python -m http.server 5500 --directory frontend
```

## GitHub Homepage Note

GitHub renders the repository homepage README only from the repository root. This file exists specifically to make the repo homepage understandable and to direct readers into the full solution under `reactive-pm-intelligence/`.