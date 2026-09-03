# Handoff — close extract/YTD phase (2026-09-03)

Phase closed: Medallion ETL (bronze raw/landing → silver SSOT → gold GCal + Kimball) is live and documented in `docs/architecture.md`.
YTD 2026 Jan–Sep fetched via WARP: **3121** silver rows (red 380 / orange 254 / yellow 2487). GCal CSVs: `data/gold/google_calendar/2026-*-news.csv` (HCM, red + USD/GBP/EUR).
**Reuse CF/FF:** `docs/scrape_strategy.md`. Trial log: `docs/LOG.md`. Code: `scripts/extract/client.py`.
Historical path that worked: WARP **Traffic and DNS (UDP)** + `curl_cffi`/`firefox135` + R/O/Y layers `--gap 45`. This-week path: `nfs.faireconomy.media` weekly export (no archive XML).
Local IP without WARP: TLS `SSL_ERROR_SYSCALL` — browser stealth cannot bypass. Dated `ff_calendar_*.xml` URLs 404.
Page timezone under WARP was `Asia/Novosibirsk` (UTC+7 ≈ HCM); stored in landing `*.meta.json`.
Next: weekly refresh (`fetch_weekly.py` or one month `--strategy http` with WARP); Oct+ same `fetch_bronze_months.py`; keep gap; do not fetch without working egress.
