# Extract / Cloudflare trial log

Keep appending. Strategy that shipped: `docs/scrape_strategy.md`.

## 2026-09-02 … 2026-09-03

| Try | Result | Decision |
|-----|--------|----------|
| `requests` / naive HTML scrape | 403 / CF challenge | Do not use |
| `curl_cffi` + `firefox135` from **local VN IP** | TLS reset `SSL_ERROR_SYSCALL` / unexpected EOF | Egress problem, not parser |
| CloudScraper vs `www.forexfactory.com` | Same TLS EOF | JS bypass useless if handshake dies |
| Playwright Chrome + undetected-chromedriver | `net::ERR_CONNECTION_CLOSED` | Stealth browser ≠ new IP |
| Cursor WebFetch / markdown permalink (early) | Sometimes worked; later timeout/challenge | Fallback: save dumps, `build_month_from_markdown.py` |
| Weekly `nfs.faireconomy.media/ff_calendar_thisweek.{csv,xml,json}` | **200** from local IP | Use for **current week only**; JSON 429 if hammered |
| Guessed historical XML `ff_calendar_01042026.xml` (+ variants) on faireconomy | **404** | No public week archive; do not loop Sundays |
| `www.forexfactory.com/ff_calendar_*.xml` | TLS fail (same IP block) | Not an alternate path |
| Cloudflare WARP **Traffic and DNS (UDP)** | FF HTML **200**, IP `104.28.x` | **Required egress for historical months** |
| WARP Local proxy / Traffic only | Not used for the YTD run | Prefer UDP so Python inherits tunnel |
| YTD fetch `impacts=3,2,1` + gap 45s + curl_cffi | Jan–Sep 2026 **3121** rows R/O/Y | Ship this. Occasional 403 recovered on retry |
| Parse dumps as markdown | Empty — files are HTML | Detect HTML → `parse_calendar_html`; save `.html` |
| Copy raw onto itself during build | `SameFileError` | Skip copy when src==dest |
| FF `timezone_name` under WARP | `Asia/Novosibirsk` (UTC+7) | Persist in meta; do not assume New York |

## Commands that produced YTD

```bash
# WARP connected (UDP)
.venv/bin/python scripts/extract/fetch_bronze_months.py \
  --year 2026 --months jan feb mar apr may jun jul aug sep --gap 45 --strategy http
.venv/bin/python scripts/transform/to_kimball.py
```
