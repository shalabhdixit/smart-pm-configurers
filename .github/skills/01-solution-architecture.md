# Skill 01: Solution Architecture

Use this skill to shape the overall solution before implementation starts.

## Objective

Translate the business problem into a structured, buildable product architecture for Reactive to PM Intelligence.

## Problem Framing

Facility management is stuck in reactive mode. Historical work-order data contains recurring patterns that should be converted into planned maintenance.

The solution must demonstrate that work-order history can be turned into predictive operational intelligence.

## Required Architecture Layers

### Layer 1: Data Ingestion

- Ingest synthetic CSV or JSON work orders.
- Validate required fields.
- Normalize dates, priority labels, problem codes, and identifiers.
- Deduplicate near-duplicate or repeated entries.
- Store cleaned records in SQLite.
- Document how the same schema migrates to PostgreSQL.

### Layer 2: Intelligence Engine

- Stage A: detect recurring patterns using grouped work-order behavior.
- Stage B: estimate recurrence probability for the next 30, 60, and 90 days.
- Stage C: generate preventive maintenance schedules for high-risk patterns.

### Layer 3: Application API

Build FastAPI endpoints for ingest, pattern retrieval, prediction retrieval, PM generation, PM listing, dashboard KPIs, and health status.

### Layer 4: Dashboard Experience

The dashboard must clearly demonstrate that the system found patterns, predicted future failures, and generated PM schedules.

### Layer 5: Integration And Automation

- Mock CAFM integration.
- Scheduler-driven daily inference.
- Webhook-style notification hook.
- Deployment assets for local and production-like startup.

## Exact Work Order Schema

Use these fields across data generation, storage, services, and API contracts:

- `work_order_id`
- `asset_id`
- `location_id`
- `problem_code`
- `problem_description`
- `created_date`
- `closed_date`
- `technician_id`
- `priority`
- `cost`
- `resolution_code`

Add supporting fields when useful, such as asset category, asset age bucket, resolution duration, or seasonal markers, as long as the primary schema remains intact.

## File Structure Requirement

The solution must target this layout:

```text
reactive-pm-intelligence/
backend/
ml/
data/
frontend/
presentation/
docs/
tests/
deployment/
requirements.txt
.env.example
README.md
DEMO_SCRIPT.md
```

Use subfolders and filenames that match the original master prompt requirements.

## Execution Guidance

- Create data generation before the backend services.
- Create storage models before service logic.
- Create service logic before routes.
- Create API and data outputs before the dashboard.
- Create the presentation after the implementation and dashboard story are clear.
- Finish with documentation, deployment, and verification.

## Business Story Requirements

Weave these facts into the product and collateral:

- 70% repeat reactive work orders.
- 1:3.5 PM to reactive cost ratio.
- 40% technician efficiency gain potential.
- 28% CSAT uplift target.
- 35% operational cost savings target by converting the top 20% recurring patterns.

## Architectural Decision Biases

- Favor clarity over novelty.
- Favor deterministic demo behavior over brittle complexity.
- Favor implementation paths that can be demonstrated locally.
- Favor outputs that are strong enough for leadership review.