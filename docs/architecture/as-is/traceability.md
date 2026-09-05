<!--
Provenance: traceability chain for the running example. 2026-09-05.
Read after conceptual → logical → pattern → physical. Do not use this table as a substitute for those layers.
-->

# Traceability chain

**Business concept → Conceptual entity → Logical component → Architecture pattern → Bronze/Silver/Gold role → Physical table/service**

Running example: *US Non-Farm Payrolls, high-impact, 4 September 2026* (forecast 55K, previous −23K, actual not printed in the captured dump).

| Step | Artifact | This occurrence |
|---|---|---|
| **Business concept** | Motivation / product language | “High-impact US jobs print I want on my calendar and in analysis.” |
| **Conceptual entity** | Calendar release + Currency + Economic indicator + Market-impact class + Release reading + Publication instant | USD × Non-Farm Employment Change × high impact × 4 Sep 2026 evening × forecast 55K / previous −23K / actual empty |
| **Logical component** | Event (release occurrence) classified by masters/references; also in **Operator attention** and **Analytical occurrence** | Event grain included; attention **yes** (high + USD + timed); analytical **yes** (unfiltered star) |
| **Architecture pattern** | Medallion: preserve → conform → project | Must survive in source preserve; must be the SSOT event; must be copied into both Gold products without becoming the SSOT itself |
| **Bronze** | Source preserve | Dump under `data/bronze/raw/calendar/2026/09_*.html` (and/or md); landing row in `data/bronze/landing/calendar_events/2026_09.csv` (`Sep 4,7:30pm,USD,red,…`) |
| **Silver** | Conformed occurrence | `data/silver/calendar_events/2026_09.csv` — `2026-09-04`, `7:30pm`, `event_datetime_hcm=…19:30+07:00`, `USD`, `red`, empty actual, `55K`, `-23K` |
| **Gold** | Consumer products | Attention: `data/gold/google_calendar/2026-09-news.csv` Subject `Non-Farm Employment Change`, 19:30–20:30 HCM. Analytical: `fact_calendar_release` + `dim_event` name Non-Farm Employment Change, `dim_currency` USD, `dim_impact` red |
| **Physical service** | Local CLI, not a hosted service | Built by `scripts/run_medallion.py --year 2026` (offline rebuild). Fetch is a separate physical path (`fetch_bronze_months.py`). Calendar import and Looker load are **not** services in this repo |

## Counter-example (same chain, dropped by attention)

A yellow EUR manufacturing PMI is the same **conceptual** Calendar release and the same **logical** occurrence / analytical fact. It is **out** of Operator attention and therefore **absent** from `gold/google_calendar`, and **present** in Silver and `fact_calendar_release`. That is the point of separating SSOT from Gold.

## Open questions that would extend this chain

1. If Looker is wired, the last hop becomes a specific connection — currently **unknown**.
2. If prints are revised later, a new conceptual entity (revision) would appear — currently **unknown**.
3. If an official indicator code appears, Indicator master would gain a key other than the display name — currently **assumption** that the name is the master key.
