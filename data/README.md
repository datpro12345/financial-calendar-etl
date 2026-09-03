# Data layout (Medallion)

See [`docs/architecture.md`](../docs/architecture.md).

```
bronze/raw/calendar/          immutable source dumps
bronze/landing/calendar_events/   parsed, unfiltered landing
silver/calendar_events/       cleaned SSOT
gold/google_calendar/         Google Calendar import CSVs (HCM)
gold/mart/                    Kimball dims + fact
```

Legacy folders `bronze/monthly/` and `silver/monthly/` are deprecated — do not write new files there.
