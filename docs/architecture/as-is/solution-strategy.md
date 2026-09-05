<!-- Adapted from arc42-template, “04 Solution Strategy”, by Gernot Starke and Peter Hruschka. Changes: condensed for evidence-led data-system review; pattern choice tied to the logical model of this repository. License: CC BY-SA 4.0, https://creativecommons.org/licenses/by-sa/4.0/ -->

<!--
Provenance: architecture-pattern layer. 2026-09-05.
Depends on logical-data-model.md. Names Bronze/Silver/Gold as *roles*, not folders.
Physical paths and jobs belong in physical-data-model.md.
-->

# Solution strategy

## Goal of this layer

Choose a **processing and storage pattern** that fits the logical components and the constraints already evidenced (fragile scrape, need to replay, two different consumers, single operator, keep it simple).

This layer answers *why Medallion* (or why not Mesh / Lambda / a warehouse-only design). It still does not name CSV files or Python modules.

## Building blocks (pattern roles)

| Role | Logical job | Maps from logical model |
|---|---|---|
| **Source preserve** | Keep what the publisher emitted, including incomplete coverage, so occurrence can be rebuilt without scraping again. | Raw shape of Calendar release + reading |
| **Conformed occurrence** | One reliable event record: vocabulary normalised, instant converted, duplicates collapsed, **no consumer filter**. | Release occurrence subject area |
| **Consumer products** | Lossy or reshaped projections owned by a use case. | Operator attention; Analytical occurrence |

Those three roles are the Medallion **Bronze / Silver / Gold** *meanings*. Folders are an implementation detail of the next layer.

## Pattern choice

| Pattern | Fit to this logical design | Verdict |
|---|---|---|
| **Medallion (batch, file)** | Matches: expensive/irreplaceable source → preserve; one event SSOT → two projections that must not pollute each other; rebuild-from-upstream rule. | **Selected (as-is)** |
| Data warehouse only (3NF or star from day one) | Would skip an immutable source copy. Scrape failures and HTML/markdown variants would force re-fetch. Star is useful — as a *Gold* product, not as the first store. | Rejected as the *only* pattern |
| Lakehouse (open table format, catalog, ACID) | Same logical roles, heavier platform. Repo explicitly skips Delta / Unity Catalog. Volume is thousands of rows. | Not justified now |
| Data Mesh | One domain, one owner, no domain team APIs. Mesh would invent organisational structure that does not exist. | Not applicable |
| Lambda / Kappa | No evidenced speed layer or stream. Weekly CDN + monthly HTML are batch. | Not applicable |
| Inmon enterprise warehouse | No enterprise integration bus or multiple source systems of record. One publisher. | Over-structure |

**Why Medallion here, in logical terms:**

1. **Release occurrence must be replayable.** The publisher relationship is brittle (TLS reset, rate limits, missing archive XML). The source-shaped copy is a logical requirement, not a naming fad.
2. **Operator attention is lossy.** If high-impact USD/GBP/EUR lived in the only store, the analytical grain and non-USD releases would be destroyed. Silver (conformed occurrence) must stay unfiltered.
3. **Two products, one event.** Calendar-shaped rows and dimensional facts are incompatible shapes. They are Gold projections, not competing “sources of truth”.
4. **Batch is enough.** Nothing in the logical model requires sub-minute streaming.

## Trade-offs (accepted)

| Gain | Cost |
|---|---|
| Rebuild Gold without scraping | Three stores to keep consistent; operator must know which layer to recompute |
| Attention filter cannot corrupt SSOT | Humans looking at Gold calendar do not see yellow/EUR PMI unless they use Silver/mart |
| Simple local files | No catalog, no concurrent writers, no warehouse engine — **unknown** how Looker actually reads the mart |
| Text measures in Gold | No typed surprise (actual − forecast) until a later fact — documented skip |

## Bronze, Silver, Gold as roles (not folders)

### Bronze — source preserve

Holds the calendar **as published**: dumps plus a parse that does **not** apply the operator attention filter and does **not** invent types.

- **Keeps:** publisher clock strings, publisher impact labels, empty/N/A readings, lineage to the dump.
- **Must not:** drop yellow/gray, drop JPY, convert to operator timezone as the only timestamp, reshape into calendar-import columns.
- **Owner:** ingestion. Downstream must not edit dumps.

### Silver — conformed occurrence

Holds the **Release occurrence** logical component: one row per natural event key, vocabulary normalised, instants in UTC and operator wall clock, nulls cleaned, duplicates collapsed.

- **Keeps:** all currencies and impact classes evidenced in Bronze.
- **Must not:** be the Google Calendar CSV; must not be the only place the attention filter is applied.
- **Owner:** conformance. Gold always rebuilds from here.

### Gold — consumer products

Two projections from the same Silver occurrence:

| Gold product | Logical component | What it does |
|---|---|---|
| Attention calendar | Operator attention | Filter high impact + chosen currencies + timed instant; project operator clock and calendar-import shape |
| Analytical mart | Analytical occurrence | Star of dimensions (date, currency, impact, indicator) + fact at release grain; readings still text |

Gold owns **use-case shape**. It does not own the event definition.

## Running example

Same US Non-Farm Employment Change print:

| Role | What happens to that occurrence |
|---|---|
| Bronze | Stored as the publisher wrote it (clock “7:30pm”, impact high/red, forecast 55K, actual empty). |
| Silver | Becomes one conformed event: date 2026-09-04, USD, high impact, both UTC and operator-local instants, empty actual. |
| Gold attention | **Emitted** — passes the lossy filter; shown on the operator clock. |
| Gold analytical | **Emitted** — one fact, joined to currency/indicator/impact/date. A yellow EUR PMI the same day is in this product and **not** in attention. |

## Evidence

- Pattern named as repo standard: `docs/architecture.md`
- Unfiltered vs filtered products: Silver schema vs `to_google_calendar.py` filter
- Rebuild rule: `scripts/run_medallion.py` does not fetch the network
- Skips (no lakehouse, no numeric measures): `docs/architecture.md` “What we deliberately skip”

No ADR file exists; this document is the sourced strategy record for this pass (ARC-04).

## Output

- This document
- [diagrams/medallion-architecture-view.mmd](diagrams/medallion-architecture-view.mmd) — Medallion Architecture View (roles + logical components)
