# Production Roadmap

## 1. Roadmap Objective

The roadmap is designed to move the solution from a visually compelling pilot into an operationally governed enterprise capability without losing demo momentum.

## 2. Phase Plan

### Phase 1: Pilot Validation

Timeline:

- weeks 1 to 4

Goals:

- validate data mapping against a real CAFM export
- confirm hotspot and recurrence precision with SMEs
- prove dashboard and PM Copilot value in stakeholder sessions

Deliverables:

- one live account mapped
- pilot scoring runs with SME review
- quantified backlog of PM conversion opportunities

### Phase 2: Production Foundation

Timeline:

- months 2 to 3

Goals:

- integrate live CAFM APIs
- replace SQLite with PostgreSQL
- formalize release pipeline and runtime observability

Deliverables:

- production-grade persistence
- secure secret handling
- operational health dashboards

### Phase 3: Multi-Site Scaling

Timeline:

- months 4 to 6

Goals:

- introduce multi-tenant model strategy
- separate batch jobs from serving layer
- add Redis-backed caching and rate limiting

Deliverables:

- scale across multiple accounts
- better latency for portfolio rollups
- safer concurrent usage

### Phase 4: Closed-Loop Intelligence

Timeline:

- months 7 to 12

Goals:

- incorporate PM outcomes and recurrence avoidance feedback
- enrich features with IoT and BMS signals
- support guided PM approval and downstream publishing

Deliverables:

- feedback-informed model improvement
- stronger financial attribution
- enterprise operations workflow fit

## 3. Capability Stream View

### Data Stream

- CAFM connectors
- tenant partitioning
- telemetry enrichment
- data quality monitoring

### Analytics Stream

- feature store candidate design
- governed training pipeline
- model registry and versioning
- drift and calibration monitoring

### Product Stream

- richer portfolio drill-downs
- approval workflow for PM publishing
- account and regional benchmarking
- persona-specific experiences for planners and account leads

### Platform Stream

- worker jobs
- API scaling
- observability and SRE controls
- security hardening and auditability

## 4. Governance Controls To Add

- model version flag
- PM auto-generation feature flag
- manual approval override
- environment-based LLM provider control
- audit trail for generated PM actions

## 5. SLA Targets

- API uptime target: 99.5 percent or better
- dashboard KPI load target: under 5 seconds for pilot-sized portfolios
- daily batch pipeline completion target: under 15 minutes
- PM generation acknowledgement target: under 2 minutes from scoring completion

## 6. Monitoring And Alerts

Critical alerts:

- health endpoint failure
- analytics pipeline run failure
- sudden drop in pattern count or prediction count
- PM generation anomalies versus historical baseline
- assistant provider failure spikes when live LLM mode is enabled

## 7. Rollback Strategy

- revert backend deployment to prior stable image
- pin previous model artifact version
- disable PM auto-generation and keep intelligence read-only
- route assistant back to deterministic `mock` mode if provider instability appears

## 8. Cost Evolution

### Pilot

- single-node app runtime
- SQLite
- minimal infra overhead

### Growth

- PostgreSQL
- Redis
- object storage or model registry
- basic observability stack

### Enterprise

- managed database and cache
- batch worker infrastructure
- centralized logging and metrics
- security and governance tooling
- possibly multi-region static delivery