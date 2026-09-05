<!--
Provenance: logical layer only. 2026-09-05.
Depends on conceptual-data-model.md. Still vendor-neutral: no files, jobs, or cloud products.
Medallion Bronze/Silver/Gold are not used here; they are pattern roles in solution-strategy.md.
-->

# Logical data model

## Goal of this layer

Take the conceptual entities and organise them into **logical data components**: subject areas, data kinds (master / reference / event / analytical), and how those components exchange meaning.

Still no implementation. A logical component can later live in files, tables, or a warehouse without changing this document.

## Building blocks — subject areas

| Subject area | What it contains | Conceptual entities |
|---|---|---|
| **Release occurrence** | The grain: one calendar release as a business event | Calendar release, publication instant, release reading |
| **Reference vocabulary** | Slow-changing codes that classify an occurrence | Currency, economic indicator, market-impact class |
| **Operator attention** | The subset of occurrences a human wants on a personal calendar | Same entities, restricted: high impact + chosen currencies + timed instant |
| **Analytical occurrence** | The same grain arranged for slicing (by date, currency, impact, indicator) | All conceptual entities, all occurrences, not the attention filter |

There is a single **domain** (macroeconomic release calendar). These are components *inside* that domain, not separate data products owned by different teams.

## Data kinds

| Logical component | Kind | Why |
|---|---|---|
| Currency | **Master** | Stable identifier of an economy’s money; reused on every release. |
| Economic indicator | **Master** | Named catalog of statistics/policy events; reused across dates. |
| Market-impact class | **Reference** | Small closed list (high / medium / low / none) with an ordering (how market-moving). |
| Calendar date parts of the instant | **Reference** | Date is not a business entity of its own, but analysts slice by year/week/weekday. |
| Calendar release + reading | **Event / transactional** | Happens at a time; actual/forecast/previous belong to that occurrence. Grain: currency + indicator + date + clock-as-published. |
| Operator attention slice | **Analytical (consumer-shaped)** | Not a new entity — a *filter and clock projection* of the event for human scheduling. |
| Analytical occurrence star | **Analytical** | Same event grain, dimensions for counting and filtering; values stay textual until a later numeric contract exists. |

**Not present (unknown / out of scope):** streaming tick, slowly-changing type-2 history of indicator definitions, revision events when a print is restated.

## How components depend and exchange

```text
Reference vocabulary  ──classifies──►  Release occurrence
Release occurrence    ──projects──►   Operator attention
Release occurrence    ──projects──►   Analytical occurrence
```

Rules (logical, not jobs):

1. **Vocabulary does not depend on occurrences.** You can list currencies and impact classes without a date.
2. **Occurrences depend on vocabulary.** An occurrence is invalid without currency, indicator, and impact class (even if the class is “none”).
3. **Attention and analytical both depend on occurrence**, never on each other. Changing the calendar filter must not rewrite the analytical grain, and vice versa.
4. **Attention is lossy on purpose:** it drops untimed releases, non-high impact, and currencies outside the operator set. The occurrence component must keep those rows.
5. **Timezone is a concern of occurrence, not of vocabulary.** The same release has one source clock and may be *shown* in the operator’s wall clock. That conversion is a property of the occurrence record, not a new entity.

## Running example

Same occurrence as the conceptual model, now typed:

| Logical component | Kind | Instance |
|---|---|---|
| Currency | master | USD |
| Economic indicator | master | Non-Farm Employment Change |
| Market-impact class | reference | high (ordered above medium/low) |
| Calendar release | event | USD × that indicator × 2026-09-04 × 7:30pm source clock |
| Release reading | event attributes | forecast 55K; previous −23K; actual empty |
| Operator attention | analytical slice | **included** — high impact, USD, timed |
| Analytical occurrence | analytical | **included** — no filter; this row is one fact among all currencies/impacts |

A yellow EUR PMI the same week is in **Release occurrence** and **Analytical occurrence**, and **out** of **Operator attention**.

## Assumptions and unknowns

| Item | Class | Note |
|---|---|---|
| Operator currency set is {USD, GBP, EUR} | fact from products/docs | Logical filter, not a conceptual entity. |
| Indicator master is the display name only | assumption | No official code (e.g. BLS series id) in the source. |
| Impact “none” (gray) is a valid class | fact in parsers/tests | May be absent in some monthly dumps. |
| Numeric typed measures | unknown / deferred | Readings stay as published text at this layer. |

## Output

- This document
- [diagrams/logical-data.mmd](diagrams/logical-data.mmd) — Logical Data Diagram
