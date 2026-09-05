# Data layout (Medallion)

See [`docs/architecture.md`](../docs/architecture.md).

```
bronze/raw/calendar/          immutable source dumps
bronze/landing/calendar_events/   parsed, unfiltered landing
silver/calendar_events/       cleaned SSOT
gold/google_calendar/         red USD/GBP/EUR, one file per month (`YYYY-MM-news.csv`)
gold/mart/                    Kimball dims + fact
```

GCal descriptions come from `docs/analyst/semantics/gcal_red.yml` (Vietnamese, no LLM).
