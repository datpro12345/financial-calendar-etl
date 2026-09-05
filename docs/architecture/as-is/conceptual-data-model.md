<!--
Provenance: conceptual layer only. 2026-09-05.
Evidence: meaning of fields observed in calendar dumps and products, expressed as business language.
No tables, folders, vendors, or Medallion roles in this file.
-->

# Conceptual data model

## Goal of this layer

Name the **business things** the platform is about, what each thing *means*, and how they relate — independent of storage, pipelines, or products.

This is not a database design. If a word would change when we switched from files to a warehouse, it does not belong here.

## Domain

**Macroeconomic release calendar for foreign-exchange attention.**

The business cares about *when an economy publishes a named statistic or policy event*, *how market-moving that print is expected to be*, and *what number was expected / printed / printed last time*. That is the whole conceptual domain evidenced in this repository. Trading accounts, orders, prices, and customers are **not** in the domain.

## Building blocks

| Conceptual entity | Meaning | Evidenced by (business signal, not a table) |
|---|---|---|
| **Currency** | The currency (and by convention the economy) the release is about. | Source rows always carry a currency code such as USD, GBP, EUR. |
| **Economic indicator** | The named statistic or policy event being published (payrolls, CPI, bank rate, FOMC statement, …). | The source always names the event; “Non-Farm Employment Change” and “ADP Non-Farm Employment Change” are different indicators. |
| **Market-impact class** | The publisher’s assessment of how sensitive markets are to that print (high / medium / low / none). | Source impact icons/labels; products treat “high” as the attention slice. |
| **Calendar release** | One occurrence: this indicator, for this currency, at this publication instant. Grain of the domain. | One dump row is one release, not a time series of a country. |
| **Release reading** | The three figures attached to that occurrence: expected, just printed, previously printed. | Forecast / actual / previous travel with the release; they are not a separate operational process. |
| **Publication instant** | When the release is scheduled or occurred, in the calendar’s own clock. | Clock strings such as “7:30pm”, “All Day”, or missing time. |

**Out of this model (they are context, not conceptual data):** the calendar website, the CDN weekly file, the human operator, Google Calendar, Looker. Those are neighbors (see the context diagram).

## Business-level relationships

- A **Currency** is the subject of many **Calendar releases**.
- An **Economic indicator** is published many times (recurring calendar).
- Each **Calendar release** is exactly one Currency × one Indicator × one Publication instant.
- Each **Calendar release** has exactly one **Market-impact class** (as assigned by the publisher for that occurrence).
- Each **Calendar release** has at most one **Release reading** (actual/forecast/previous may be empty when not yet printed).
- **Publication instant** may lack a clock (“All Day”, tentative) — the release still exists; only the precise instant is unknown.

No many-to-many between Currency and Indicator is stored as a separate business object; the association *is* the release.

## Running example

**Business concept:** “US Non-Farm Payrolls, high-impact, 4 September 2026.”

| Entity | Instance |
|---|---|
| Currency | US dollar (the US labour-market print) |
| Economic indicator | Non-Farm Employment Change — not the ADP variant |
| Market-impact class | High |
| Publication instant | 4 September 2026, evening on the source calendar clock |
| Calendar release | That one payrolls print |
| Release reading | Forecast 55 thousand; previous −23 thousand; actual not yet printed in the dump we hold |

## Assumptions and unknowns

| Item | Class | Note |
|---|---|---|
| Currency stands in for “economy / country” | assumption | EUR is a shared currency; the source keys by currency, not country. |
| Impact class is a property of the *occurrence*, not a fixed property of the indicator | fact from dumps | The same indicator name can appear with different impact labels across rows. |
| Forecast vs actual vs previous are one reading object, not three entities | assumption | Fits the source; a later “surprise / revision” process is **unknown**. |
| Official statistical agency (BLS, ONS, Eurostat) as a conceptual entity | unknown | Not present in the source; only the calendar publisher’s naming. |

## Output

- This document
- [diagrams/conceptual-data.mmd](diagrams/conceptual-data.mmd) — Conceptual Data Diagram

Do not add keys, schemas, or layer names to that diagram.
