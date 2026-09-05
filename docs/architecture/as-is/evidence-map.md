<!--
Provenance: as-is review of ff-transform-data, 2026-09-05.
Scope: Motivation / Requirements / Context only. No solution-architecture inference.
Audience: repository owner deciding what as-is documentation to keep.
-->

# Evidence map — Motivation, Requirements, Context

Current-state observation. Claims below are tagged **fact**, **assumption**, or **unknown**. Counts were taken from files on 2026-09-05.

## Layer status

| Layer | Status | Why |
|---|---|---|
| Motivation / Why | partly evidenced | Purpose and two products are stated, but README and later docs disagree on project phase and destinations. No named stakeholders, KPIs, or constraints document. |
| Requirements | partly evidenced | Functional filters, schemas, and parse tests exist. No SLA/SLO, freshness target, or sourced quality scenarios. |
| Context | partly evidenced | Source systems and file products are named in code. Consumer systems (Google Calendar, Looker Studio) are intended, not wired in this repository. |

Static / solution / physical for the **calendar-release domain** are documented in thinking order (not as a jump to folders): [thinking-order.md](thinking-order.md). Runtime, deployment, and cross-cutting were not reviewed.

## Evidence matrix

### Motivation / Why

| ID | Claim | Class | Evidence |
|---|---|---|---|
| M1 | The repository exists to extract Forex Factory economic calendar data, transform it, and produce analysis/scheduling products. | fact | `README.md` goals 1–2; `docs/architecture.md` purpose; `docs/INDEX.md` |
| M2 | One intended product is a Google Calendar import CSV of high-impact events. | fact | `README.md` goal 2 (“Done”); `scripts/transform/to_google_calendar.py` (`TARGET_CURRENCIES`, `impact="red"`); files `data/gold/google_calendar/2026-0{1-9}-news.csv` |
| M3 | Another intended product is analytics / BI, including a Looker report. | partly evidenced | **fact:** README links [Looker Studio](https://lookerstudio.google.com/reporting/eef5b556-a5d4-4d54-be00-27cbc59f30d2). **fact:** `docs/architecture.md` says the Kimball mart is “for BI / Looker”. **unknown:** whether that report reads this repo’s files, and who the audience is. |
| M4 | The operator cares about USD, GBP, and EUR high-impact events on an HCM wall clock. | fact | README “major currencies (USD, GBP, EUR)” + high-impact; `to_google_calendar.py` filters; `docs/HANDOFF.md` “HCM, red + USD/GBP/EUR”; gold CSV `TZ: Asia/Ho_Chi_Minh` |
| M5 | The current operating phase is “Medallion ETL live for 2026 YTD extract.” | fact (ops log) | `docs/HANDOFF.md` (2026-09-03); `docs/INDEX.md` treats HANDOFF as current |
| M6 | The current operating phase is “Phase 2 notebook transformation.” | fact (stale doc) | `README.md` “Current Phase: Phase 2”; `docs/INDEX.md` labels `docs/README.md` “legacy… partially outdated” |
| M7 | Named business stakeholders, success metrics, budget, or legal/ToS constraints for scraping. | unknown | LICENSE is MIT, copyright datpro12345. No product brief, KPI, or stakeholder list. |
| M8 | Primary user of the pipeline is the repository owner running local CLI. | assumption | No scheduler, CI, or multi-user auth. Scripts are argparse CLIs (`scripts/run_medallion.py`, `scripts/extract/fetch_*.py`). |

### Requirements

| ID | Claim | Class | Evidence |
|---|---|---|---|
| R1 | Bronze landing must preserve source fields as strings, without currency/impact business filters. | fact (documented contract) | `docs/architecture.md` bronze landing table; `scripts/extract/config.py` `BRONZE_LANDING_COLUMNS` |
| R2 | Silver is the SSOT: typed datetimes, HCM+UTC, all currencies/impacts, natural-key dedupe. | fact (documented contract) | `docs/architecture.md` silver rules; `scripts/transform/to_silver.py`; `SILVER_COLUMNS` in `config.py` |
| R3 | Gold Google Calendar CSV must keep red + `{USD,GBP,EUR}` + timed (non-empty `event_datetime_hcm`) events, HCM clock, GCal column set. | fact | `scripts/transform/to_google_calendar.py` filter and `GOOGLE_CALENDAR_COLUMNS`; `docs/architecture.md` gold product table |
| R4 | Allowed currency codes for the pipeline include AUD, CAD, CHF, CNY, EUR, GBP, JPY, NZD, USD. | fact | `config.py` `ALLOWED_CURRENCIES` |
| R5 | Parser output for HTML and weekly CSV must match the bronze 8-column schema. | fact | `tests/test_extract_bronze.py`; `BRONZE_COLUMNS` |
| R6 | Live fetch against Forex Factory is optional and may be skipped when the network fails. | fact | `pytest.ini` marker `integration`; `test_live_bronze_extract` skips on exception |
| R7 | Historical HTML fetch must pace impact layers (~45s + jitter) and prefer WARP or `FF_HTTP_PROXY` from a VN residential IP. | fact (operational constraint) | `docs/scrape_strategy.md`; `config.py` `IMPACT_FETCH_GAP_SECONDS`, `PROXY_ENV_KEYS`; `client.py` docstring |
| R8 | This-week refresh must use `https://nfs.faireconomy.media/ff_calendar_thisweek.{csv,xml,json}` and is rate-limited (~2 / 5 min). | fact (documented) | `config.py` `FF_WEEKLY_EXPORT_*`; `docs/scrape_strategy.md`; `docs/HANDOFF.md` |
| R9 | Dated archive XML (`ff_calendar_*.xml` by date) is not a valid source. | fact (negative requirement) | `client.py` and `docs/scrape_strategy.md`: CDN 404 |
| R10 | Freshness SLA, completeness SLO, data-retention, PII/privacy policy, or numeric parsing of actual/forecast. | unknown / explicitly deferred | `docs/architecture.md` “What we deliberately skip”; no tickets or SLO files |
| R11 | Automated load into Google Calendar, Google Sheets, or Looker. | unknown as a requirement | `docs/README.md` names `load_to_gsheets.py` and `scripts/load/` — **those paths do not exist**. Gold is file CSV only. |

### Context

| ID | Claim | Class | Evidence |
|---|---|---|---|
| C1 | System under review is this git repository: local Python scripts writing CSV under `data/`. | fact | layout `scripts/`, `data/`, `requirements.txt`; no `config/`, no `.github/` workflows, no `scripts/load/` |
| C2 | Upstream: `https://www.forexfactory.com/calendar` HTML, month permalinks with `impacts=3\|2\|1`. | fact | `config.py` `FF_CALENDAR_URL`; `client.py` `build_impact_url` |
| C3 | Upstream: `https://nfs.faireconomy.media/ff_calendar_thisweek.{csv,xml,json}`. | fact | `config.py` `FF_WEEKLY_EXPORT_BASE`; `tests/test_extract_bronze.py` URL assertion |
| C4 | Egress neighbors: Cloudflare WARP (Traffic and DNS UDP) and optional HTTP(S) proxy env vars. | fact | `docs/scrape_strategy.md`; `client.py` `_proxy_url`; `PROXY_ENV_KEYS` |
| C5 | Source page timezone observed under WARP was `Asia/Novosibirsk` (UTC+7). | fact | `data/bronze/landing/calendar_events/2026_01.meta.json` `source_timezone`; `docs/HANDOFF.md` |
| C6 | 2026 Jan–Sep landing/silver contain 3121 rows; gold GCal contains 221 rows; gold mart files exist. | fact | counted `data/silver/calendar_events/2026_*.csv` (3121), matching landing; `data/gold/google_calendar/2026-*-news.csv` (221); `data/gold/mart/{dim_*,fact_calendar_release}.csv` |
| C7 | Downstream: Google Calendar consumes the gold CSV via Calendar’s CSV import. | assumption | Files and column names match GCal import. No Calendar API client, token, or import job in the repo. |
| C8 | Downstream: Looker Studio report is a consumer of this pipeline. | unknown | README URL only. No Looker connector, BigQuery, Sheets ID, or load script. |
| C9 | Google Sheets is a load target. | unknown / contradicted | Stated in `docs/README.md`; no `scripts/load/` or Sheets client. |
| C10 | Runtime host, schedule, and multi-environment deployment. | unknown | No compose, Terraform, cron, GitHub Actions. Operation described as local CLI in HANDOFF. |

## Conflicts (do not resolve by invention)

1. **Phase:** `README.md` says transformation is still in a notebook and tests are not implemented. `docs/HANDOFF.md`, `scripts/run_medallion.py`, `tests/test_extract_bronze.py`, and 2026 silver/gold files show a closed extract/YTD phase with modular scripts.
2. **Directory contract:** `docs/README.md` describes `data/raw`, `data/processed`, `config/config.yaml`, `scripts/load/load_to_gsheets.py`, `docs/architecture.md` as a future tree. Actual tree is medallion folders in `data/` plus `docs/architecture.md` as the medallion standard.
3. **Looker vs files:** a Looker Studio URL is published; no evidenced interface from `gold/mart` to that report.

## Gap list (this pass only)

| Gap | Layer | Artifact? | Reason |
|---|---|---|---|
| Single current purpose statement (README vs HANDOFF) | Motivation | no ARC-01 | Evidence conflicts; writing Introduction and Goals would pick a narrative. |
| Named stakeholders / quality goals with measures | Motivation, Requirements | no ARC-10 | No SLA, KPI, or stakeholder evidence. |
| Business + technical context document | Context | no ARC-03 prose | Neighbors are clear enough for a diagram; a full context paper would restate this map. |
| Context diagram of evidenced neighbors | Context | **yes** — `diagrams/system-context.mmd` | Source systems and file products are named; Looker/GCal import marked assumption. |
| Combined `foundation.md` | Motivation–Context | **no** | Not enough consistent motivation/requirements to freeze a foundation without mixing stale README text. |

## Artifact decisions

Created:

- this file
- `diagrams/system-context.mmd` (Mermaid, MER-01) — conservative; dashed edges are assumptions

Not created: ARC-01, ARC-03 markdown, ARC-10, `foundation.md`, any static/runtime/deployment view.

## Open questions

1. Who uses the Looker Studio report, and from which dataset?
2. Is Google Calendar import a manual operator step or an uncommitted automation?
3. Is Forex Factory scraping permitted for this use, and what is the retention/attribution policy?
4. Should `README.md` / `docs/README.md` be marked legacy or rewritten to match HANDOFF?
