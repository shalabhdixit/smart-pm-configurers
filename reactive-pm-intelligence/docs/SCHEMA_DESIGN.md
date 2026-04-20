# Schema Design

## 1. Design Objective

The schema design supports two outcomes at once:

- a realistic operational data backbone for the demo application
- a credible migration path to enterprise-scale portfolio intelligence

The schema therefore separates raw operational facts, derived analytics, and reference entities.

## 2. Domain Entity Groups

### Raw Operational Entity

#### WorkOrder

Represents the atomic reactive maintenance event.

Key attributes:

- work order identity
- asset and location identity
- problem classification
- timestamps
- technician assignment
- cost, duration, priority, and seasonal context

Why it matters:

- this is the base fact table from which all intelligence is derived

### Reference Entities

#### Facility

Represents the operating location or managed property.

Business role:

- portfolio rollups
- hotspot analysis
- SLT storytelling by geography and property type

#### Asset

Represents the physical equipment item subject to failure recurrence.

Business role:

- risk ranking
- health scoring
- PM recommendation targeting

#### Technician

Represents maintenance workforce context.

Business role:

- skill mapping
- labor framing
- workforce planning narratives

### Derived Intelligence Entities

#### PatternRecord

Represents a recurring signature aggregated from multiple work orders.

Business key:

- `pattern_key = asset_id | location_id | problem_code`

Why it exists:

- creates an explainable intermediate layer between raw tickets and model output

#### PredictionRecord

Represents the recurrence probability for a detected pattern.

Why it exists:

- separates model output from source features and allows scoring history to evolve independently

#### PMSchedule

Represents the recommended preventive maintenance action derived from a high-risk pattern.

Why it exists:

- translates analytics into an executable operating artifact

## 3. Logical Schema Principles

### Principle 1: Keep Raw Data Intact

Work orders retain source-oriented fields instead of prematurely normalizing away useful operational detail.

### Principle 2: Derived Tables Are Rebuildable

Patterns, predictions, and PM schedules are intentionally regenerable from current history.

### Principle 3: Reference Data Supports Storytelling

Facilities, assets, and technicians are modeled explicitly because leadership narratives require entity context, not just anonymous pattern keys.

## 4. API Schema Families

### Request Schemas

- `WorkOrderIn`
- `IngestRequest`
- `AssistantRequest`

### Response Schemas

- `IngestResponse`
- `PatternResponse`
- `PredictionResponse`
- `PMScheduleResponse`
- `KPIResponse`
- `HealthResponse`
- `GeneratePMResponse`
- `AuthTokenResponse`
- `AssistantResponse`
- `PortfolioOverviewResponse`

### Nested Response Schemas

- `AssistantAction`
- `FacilitySummary`
- `AssetSummary`

## 5. Pattern Schema Rationale

The `PatternRecord` entity contains both statistical features and planning-oriented fields.

Statistical fields:

- occurrence count
- average interval
- standard deviation
- coefficient of variation
- regularity score

Planning fields:

- priority mode
- assigned skill set
- average resolution hours
- average cost
- timeline

This combination allows one record to support data science, PM generation, dashboard rendering, and assistant explanation.

## 6. Prediction Schema Rationale

The prediction schema keeps probabilities and confidence bounds directly accessible while storing explanation in a JSON payload.

Reasoning:

- scalar fields support simple sorting and filtering in APIs and UI
- JSON explanation keeps the response extensible without repeated schema churn

## 7. PM Schedule Schema Rationale

`PMSchedule` includes both normalized fields and the originating `source_payload`.

Why:

- normalized fields support operational display and downstream posting
- the payload preserves the reason the PM exists and what pattern generated it

## 8. Schema Evolution Path

Likely future additions:

- tenant or client identifier for multi-tenancy
- site SLA tier and contract metadata
- PM publication status and approval owner
- closed-loop feedback for whether generated PM avoided a reactive recurrence
- model version and scoring timestamp fields

## 9. Anti-Patterns Avoided

- storing predictions directly on raw work-order rows
- mixing reference data and analytics output in one table
- hard-coding UI-only fields into database entities
- forcing strict normalization that would reduce analytics flexibility

## 10. Recommended Production Schema Extensions

- partition work-order history by tenant and time window
- add audit tables for PM publication actions
- keep model inference lineage for governed operations
- introduce event tables for IoT and BMS signals when moving beyond history-only analytics