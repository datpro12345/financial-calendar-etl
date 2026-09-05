# Selection rules

Terms: [terminology.md](terminology.md). Instantiate a **template** into an **artifact** (diagram, matrix, catalog, or ADR). Do not call the template, the view, or the pattern an artifact until it is project evidence written down.

## Gap triage

Create an **artifact** only when all applicable conditions hold:

1. The thinking layer is architecturally relevant to the review question or a stakeholder **concern** (the **viewpoint**).
2. The repository has enough evidence to make the artifact useful, or the artifact is explicitly an evidence-request/open-question record.
3. No existing maintained **document** already answers the question at the needed level.
4. The artifact has a named audience or decision/use case.

Prefer a short evidence **matrix** or a single updated artifact over a complete arc42-style **deliverable**. Mark a missing source **template** as a gap; do not silently invent a new “standard” one.

## Repository output convention

Preserve an existing repository documentation convention when one exists. Otherwise, use `docs/architecture/as-is/` for current-state observations and reserve `docs/architecture/to-be/` for an explicitly requested target architecture. See [output-conventions.md](output-conventions.md) before writing files.

For a first pass limited to Motivation, Requirements, and Context, the smallest durable **documents** are normally `as-is/evidence-map.md` (matrix artifact), optionally `as-is/foundation.md`, and `as-is/diagrams/system-context.mmd` (diagram artifact for the Context **view**). File names are a repository convention, not a new template: instantiate ARC-01 and ARC-03 only when evidence warrants it.

## Diagram choice

| Need | Default | Escalate when |
|---|---|---|
| Context, static data-flow, simple deployment | Mermaid flowchart | a durable architecture **model** with several **views** is required: LikeC4/Structurizr |
| Interaction across jobs/services | Mermaid sequence diagram | timing, branching, or BPMN notation is materially required |
| Entity/contract relationships | Mermaid ER diagram | a data modeling tool is already authoritative |
| Complex editable workshop or presentation diagram | `.drawio` | retain the source `.drawio`; also export a reviewable SVG/PNG when requested |

Never create a **diagram** merely because a **template** asks for one. Each node (building block / element), edge (**relationship**), label, and boundary must be traceable to evidence or annotated as an assumption. Do not mix abstraction levels in one diagram.

## Consistency review

Before treating work as a **deliverable**, compare every generated **artifact** with the repository for names, interfaces, directions, schemas, schedules, retries, environment, identity, SLO, retention, privacy, governance claims, ADR status, and links. Report conflicts and missing evidence; do not resolve them by invention.
