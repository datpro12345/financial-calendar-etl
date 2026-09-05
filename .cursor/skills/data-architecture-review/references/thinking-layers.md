# Thinking layers

Use this order to keep reasoning tied to decisions instead of diagram production. These names are **our thinking flow**, not official chapters of a single framework.

A layer can be `evidenced`, `partly evidenced`, `unknown`, or `not applicable`.

| # | Thinking layer | Question | Typical repository evidence | You are reasoning about | Terms to use |
|---|---|---|---|---|---|
| 1 | Motivation | Why are we doing this? | README, product brief, KPIs, stakeholder docs | why | Driver, Goal, Principle, Stakeholder |
| 2 | Requirements | What must be true? | tickets, acceptance tests, SLAs/SLOs, schemas, policies | conditions that must hold | Requirement, Constraint, Quality Attribute |
| 3 | Context | What is in/out of scope? | API clients, IaC, integrations, secrets/config names | boundary and external world | Context model / Context view |
| 4 | Static Architecture | What things exist? | directories, packages, dbt/Dagster/Airflow assets, schemas, contracts | the things and how they connect | **Building blocks / elements + relationships** |
| 5 | Runtime / Behavior | How do those things interact? | DAGs, stream jobs, schedules, retries, tests, runbooks | interactions over time | Runtime view, Scenario |
| 6 | Solution Strategy | What approach/pattern do we choose? | platform choices, shared libraries, ADRs, design docs | overall approach | **Pattern**, Strategy, Reference architecture |
| 7 | Deployment | Where/how does it physically run? | Terraform, Helm, compose, CI/CD, cloud manifests | logical → physical mapping | Deployment model / view |
| 8 | Cross-cutting | What rules apply across everything? | auth, catalog, lineage, observability, data quality, governance | spanning rules | Concern, Policy, Concept |
| 9 | Decisions | Why this instead of alternatives? | ADRs, PRs, issue links, config conventions | choice among options | Architecture Decision / ADR |
| 10 | Deliverable | What package do we give stakeholders? | release docs, runbooks, contracts, dashboards | handover package | **Deliverable** (contains artifacts) |

**View / Viewpoint** are how a stakeholder *looks* at the model (communication). They are not a numbered layer and not building blocks.

**Artifact** is a work product (diagram, matrix, catalog, ADR). **Document** is the file that holds it. See [terminology.md](terminology.md).

For data systems, inspect orchestration definitions, transformation projects, schemas/contracts, streaming topology, infrastructure-as-code, environment configuration, observability, access policies, and operational documentation before marking a gap.
