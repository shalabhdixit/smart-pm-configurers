# Skill 04: Docs, Deployment, And Validation

Use this skill when finishing the solution and preparing it for handoff, demo, and review.

## Documentation Set Required

Create and align the following:

- `README.md`
- `docs/ARCHITECTURE.md`
- `docs/API_REFERENCE.md`
- `docs/DEPLOYMENT_GUIDE.md`
- `docs/ML_MODEL_CARD.md`
- `docs/PRODUCTION_ROADMAP.md`
- `DEMO_SCRIPT.md`

## README Expectations

The README should feel launch-ready and should include:

- project summary
- badges
- architecture overview
- key features
- quick start steps
- API examples
- local run guidance
- performance or demo benchmarks
- contribution guidance

## Architecture Document Expectations

Include:

- system context
- container or component diagrams
- data flow
- ERD
- AI decision flow
- security posture
- scale considerations

## Model Card Expectations

Document:

- model purpose
- training data characteristics
- features
- metrics
- limitations
- bias considerations
- retraining process

## Production Roadmap Expectations

Document:

- phased rollout
- feature flags
- observability plan
- rollback plan
- SLA ideas
- cost by scale tier

## Deployment Assets Required

Create:

- `deployment/docker-compose.yml`
- `deployment/Dockerfile.backend`
- `deployment/Dockerfile.frontend`
- `deployment/k8s/deployment.yaml`
- `deployment/k8s/service.yaml`
- `deployment/.github/workflows/ci-cd.yml`

The workflow should cover linting, tests, Docker build, and security scanning.

## Security And Operations Checklist

Implement or document:

- input validation
- JWT token expiry
- no hardcoded secrets
- rate limiting
- CORS whitelist behavior
- SQL injection avoidance
- HTTPS in production guidance
- logging and metrics
- retry logic
- connection pooling
- backup strategy
- HPA-ready Kubernetes deployment

## Validation Standard

Before considering the solution complete, verify:

1. File structure is complete.
2. Core routes and services are implemented.
3. Documentation matches the delivered implementation.
4. Tests exist for critical logic.
5. The dashboard and presentation are demo-ready.
6. Deployment assets are coherent.

## Demo Script Expectations

Write a five-minute script that walks from dashboard KPIs to pattern discovery, prediction, PM generation, ROI, and the final executive ask.