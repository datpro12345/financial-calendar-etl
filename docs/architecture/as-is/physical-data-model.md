<!-- Adapted from arc42-template, “05 Building Block View”, by Gernot Starke and Peter Hruschka. Changes: physical mapping of the logical model and Medallion roles for this repository. License: CC BY-SA 4.0, https://creativecommons.org/licenses/by-sa/4.0/ -->

<!--
Provenance: physical layer only. 2026-09-05.
Depends on solution-strategy.md. This is the first document allowed to name files, jobs, and formats.
-->

# Physical data model / implementation

## Goal of this layer

Map logical components and Medallion **roles** onto the **actual** stores, formats, jobs, and ownership in this repository. Nothing here invents a warehouse or scheduler that is not in the tree.

## Building blocks

| Physical block | Medallion role | Logical component | Location / contract | Evidence |
|---|---|---|---|---|
| HTML/Markdown dumps | Bronze dump | Source-shaped calendar release | `data/bronze/raw/calendar/{year}/{mm}_{red\|orange\|yellow\|all}.{html\|md}` | files exist for 2026; `BRONZE_RAW_CALENDAR_DIR` |
| Landing CSV + sidecar | Bronze parse | Unfiltered release + lineage | `data/bronze/landing/calendar_events/{yyyy}_{mm}.csv` + `*.meta.json` | `BRONZE_LANDING_COLUMNS`; meta `source_timezone` |
| Silver month CSV | Silver SSOT | Conformed occurrence | `data/silver/calendar_events/{yyyy}_{mm}.csv` | `SILVER_COLUMNS`; `to_silver.py` |
| GCal month CSV | Gold attention | Operator attention | `data/gold/google_calendar/{yyyy-mm}-news.csv` | `GOOGLE_CALENDAR_COLUMNS`; filter in `to_google_calendar.py` |
| Kimball CSVs | Gold analytical | Analytical occurrence | `data/gold/mart/dim_*.csv`, `fact_calendar_release.csv` | `to_kimball.py` |
| Fetch HTML months | Ingestion job | — | `scripts/extract/fetch_bronze_months.py` | scrape_strategy |
| Fetch this week | Ingestion job | — | `scripts/extract/fetch_weekly.py` → `nfs.faireconomy.media` | config + tests |
| Rebuild year | Orchestration | bronze→silver→gold, **no network** | `scripts/run_medallion.py --year 2026` | docstring |
| Legacy monthly folders | Deprecated | — | `data/bronze/monthly`, `data/silver/monthly` | `config.py` comments; `DEPRECATED.md` |

**Format (all current layers):** CSV (and source HTML/Markdown). No Parquet, Delta, or database. **Partitioning:** one file per calendar month (and impact-layer dumps in raw). **Runtime:** local Python CLI; owner is the repository operator. **No** CI, compose, or `scripts/load/`.

## Source → Bronze → Silver → Gold (same occurrence)

**Instance:** Non-Farm Employment Change, USD, 4 Sep 2026.

### Source

Forex Factory calendar HTML (and/or markdown dump) for September 2026, impact layers red/orange/yellow. Weekly CDN is a different physical path for *this week only*, not this historical month.

### Bronze

1. **Dump (immutable):** e.g. `data/bronze/raw/calendar/2026/09_red.html` (and orange/yellow; optional `09_all.md`). Never edit.
2. **Landing (parse, no business filter):** `data/bronze/landing/calendar_events/2026_09.csv`

Observed landing row (strings as published):

| date | time | currency | impact | event | actual | forecast | previous |
|---|---|---|---|---|---|---|---|
| Sep 4 | 7:30pm | USD | red | Non-Farm Employment Change | N/A | 55K | -23K |

`*.meta.json` records `source_timezone` (observed `Asia/Novosibirsk` under WARP) and coverage.

**Ownership:** extract scripts. **Consumers of Bronze:** only Silver (and humans debugging parse). Not Looker, not Calendar.

### Silver

Job: `landing_to_silver` in `scripts/transform/to_silver.py` (also via `build_month` / `run_medallion.py`).

Transforms: parse date + year → `event_date`; parse clock; convert to `event_datetime_utc` and `event_datetime_hcm`; clean N/A; keep all impacts/currencies; natural key `(event_date, time_raw, currency, event)`.

Observed silver row:

| event_date | time_raw | event_datetime_hcm | currency | impact | event | actual | forecast | previous | source_timezone |
|---|---|---|---|---|---|---|---|---|---|
| 2026-09-04 | 7:30pm | 2026-09-04T19:30:00+07:00 | USD | red | Non-Farm Employment Change | *(empty)* | 55K | -23K | Asia/Novosibirsk |

**Ownership:** transform. **Consumers of Silver:** Gold jobs only (plus anyone who needs the full unfiltered SSOT).

### Gold — attention

Job: `silver_to_google_calendar`. Filter: `currency ∈ {USD,GBP,EUR}` AND `impact = red` AND non-empty `event_datetime_hcm`. Project GCal columns; 1-hour duration; HCM clock.

Observed gold calendar row:

| Subject | Start Date | Start Time | Description | Location |
|---|---|---|---|---|
| Non-Farm Employment Change | 09/04/2026 | 19:30 | Forecast: 55K \| Actual: N/A \| Previous: -23K \| TZ: Asia/Ho_Chi_Minh | USD |

**Ownership:** gold export. **Intended consumer:** Google Calendar CSV import (**assumption** — no API job in repo).

### Gold — analytical

Job: `silver_to_kimball`. Builds `dim_date`, `dim_currency`, `dim_impact`, `dim_event`, `fact_calendar_release` (grain = one release; `actual_txt` / `forecast_txt` / `previous_txt`).

This NFP row is one fact keyed to USD, red, “Non-Farm Employment Change”, date 20260904.

**Ownership:** gold export. **Intended consumer:** BI / Looker (**unknown** feed — README URL only).

## What each layer keeps, changes, owns, serves

| Layer | Keeps | Changes | Owner | Consumer |
|---|---|---|---|---|
| Bronze raw | Bytes from publisher | None | Extract | Landing parser |
| Bronze landing | All parsed rows as strings + source path | HTML/MD → columns | Extract | Silver |
| Silver | All currencies/impacts, typed instants | Clean, tz, dedupe | Transform | Gold jobs |
| Gold GCal | Attention subset only | Filter + calendar shape + HCM | Transform | Operator / Calendar import |
| Gold mart | Full grain as star | Keys + date parts; values still text | Transform | BI (unwired) |

Recompute: change Gold → rebuild from Silver. Change Silver → rebuild from landing/raw. Scrape only if Bronze is missing (`docs/architecture.md`).

## Physical star (mart)

Logical “analytical occurrence” is implemented as:

- `dim_currency.currency_code`
- `dim_event.event_name` (indicator **name** only — no official series id)
- `dim_impact.impact_code` + `impact_rank`
- `dim_date.date_key`
- `fact_calendar_release` fact_id + those keys + time and `*_txt` measures

## Assumptions and unknowns

| Item | Class |
|---|---|
| Calendar import is manual | assumption |
| Looker reads `gold/mart` | unknown |
| `dim_impact` in the current mart files lists yellow/orange/red only (no gray) | fact from `dim_impact.csv` — gray may be absent if no silver row used it |
| Deployment host / cron | unknown |

## Output

- This document
- [diagrams/physical-data-flow.mmd](diagrams/physical-data-flow.mmd) — Physical Data Model / flow
