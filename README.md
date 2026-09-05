# Forex calendar → Kimball mart → weekly macro outlook

Deterministic ETL for the Forex Factory calendar, plus a **linted** weekly brief for swing trading USD / EUR / GBP / JPY.

The LLM never invents the calendar. Python computes the Fact Pack. The model only reasons. A linter rejects numbers that are not in the pack.

**Samples:** [English](reports/weekly/2026-W36-macro-outlook.en.md) · [Tiếng Việt](reports/weekly/2026-W36-macro-outlook.vi.md)

```text
nfs.faireconomy.media (this week, no WARP)
        │
        ▼
 bronze → silver SSOT → gold Kimball mart
        │
        ▼
 Fact Pack (counts, clashes, HCM clocks, fact_id)
        │
        ▼
 LLM outlook (--lang en|vi|…)  →  report lint
```

## What you get

- **Medallion + Kimball** — bronze landing, silver events, gold dims/facts, optional Google Calendar CSV
- **ABCD weekly job** — fetch → ingest → Fact Pack → outlook. Fail-stop: no LLM if fetch/transform fails
- **Soros contract** — hypothesis + falsification; no new primary swing entries in red windows
- **Language flag** — `--lang en`, `--lang vi`, or any language name

## Quick start

```bash
cp .env.template .env          # set OPENROUTER_API_KEY
docker compose build
docker compose run --rm -e REPORT_LANG=en weekly
```

Without Docker:

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.template .env
python scripts/run_weekly_abcd.py --fmt csv --lang en
```

Output: `reports/weekly/{YYYY}-W{WW}-macro-outlook.{lang}.md`

| You fill in | Where |
|---|---|
| `OPENROUTER_API_KEY` | [openrouter.ai/keys](https://openrouter.ai/keys) |
| `OPENROUTER_MODEL` | default `inclusionai/ling-3.0-flash-fin:free` (fallback MiniMax M3) |
| `REPORT_LANG` | optional, `en` or `vi` |

Deploy on Windows Docker Desktop or an Oracle Always Free VM: **[docs/docker.md](docs/docker.md)**.

## Layout

```text
scripts/extract/     fetch this-week + Cloudflare playbook
scripts/transform/   landing → silver → Kimball
scripts/analyst/     Fact Pack, lint, language, LLM client
scripts/run_weekly_abcd.py
data/{bronze,silver,gold}/
reports/weekly/      sample outlooks (en / vi)
docs/analyst/        prompt + Control Lane semantics
```

## Tests

```bash
pip install -r requirements.txt
python -m pytest -q -m "not integration"
```

## Docs

[Index](docs/INDEX.md) · [Scrape strategy](docs/scrape_strategy.md) · [Analyst roadmap](docs/analyst-roadmap.md) · [Docker](docs/docker.md)

MIT — see [LICENSE](LICENSE). Do not commit `.env`.
