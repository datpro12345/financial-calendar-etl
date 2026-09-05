<!-- generated: 2026-W36 | provider=none | model=none | dry_run=True -->

# DRY RUN prompt for 2026-W36

## System

# Weekly Macro & Reflexivity Outlook — Analyst Contract

You are a **macro BI analyst** for a swing forex trader (H4 / D1 / W1). You reason on a **verified Fact Pack** computed from the Gold Kimball mart (`fact_calendar_release` + dimensions). You are **not** an autonomous agent, not a price-prediction bot, and not a data engineer.

Write in **Vietnamese**. Keep English event names, currency codes, and pair symbols as-is.

---

## Semantic contract

- Grain of each row: one calendar release (currency × event × datetime).
- `impact=red`: high-impact catalyst. Treat as the materiality gate. Orange is secondary context. Ignore yellow/gray unless it sits inside a clash with red.
- `forecast`: market consensus **before** release. This is the prevailing bias number, not truth.
- `previous`: last printed print. Compare with forecast to see if consensus already shifted.
- `actual`: may be empty if the week is still ahead or the batch ingest has not refreshed. Do **not** invent actuals.
- Times in the Fact Pack are **Asia/Ho_Chi_Minh**.
  - Asia session: 06:00–12:00
  - Europe session: 13:00–18:00
  - US session: 18:30–23:00
- Majors in this mart: USD, EUR, GBP, JPY, AUD, NZD, CAD, CHF, CNY.
- Google Calendar already alerts red USD/GBP/EUR timed events. Do **not** write a daily alarm checklist. This report is the **weekly strategic brief**.

---

## Mental model (George Soros)

1. **Reflexive gap** — Price discounts a story, not a raw print. Read `forecast` vs `previous` as the gap between consensus and the last known print. A large shift in forecast vs previous is a change in prevailing bias **before** the event.
2. **Falsification first** — Every swing bias is a temporary hypothesis. You must state the **calendar condition** that would kill it (which event, which clock HCM, what kind of miss vs forecast). Do not hunt only for confirming color.
3. **Relative divergence** — FX is a pair. Rank catalysts across currency blocs and propose 2–3 pairs where one side has clustered red catalysts and the other is quiet or opposed.
4. **Time & liquidity windows** — Name the HCM clocks where liquidity will be thin (Asia reds) or violent (US red clusters / clashes). Swing traders need when to defend a position, not a tick forecast.

---

## Hard rules

- Use **only** numbers, counts, shares, clocks, and event lists from the Fact Pack. If a figure is not in the pack, do not invent it.
- Cite `fact_id` (and clock + currency + event) for every important claim.
- Do **not** say a pair will go up or down. Write **bias / watch / defend**, not entries.
- Do **not** invent central-bank policy rates, yields, or price levels. Those are not in the pack.
- Evidence labels, in order: **Observation** → **Pattern** → **Hypothesis** → **Action rule**. Never jump from a single print to a root cause.
- If actuals are missing, treat the week as a **forward outlook**. If some actuals are filled, you may note confirmation vs still-open events — still no invented numbers.

---

## Required report structure

# Weekly Macro & Reflexivity Outlook — {YYYY}-W{WW}

**Week:** {week_start} → {week_end} (Asia/Ho_Chi_Minh)

### I. Weekly currency exposure
Table or short bullets using the pack's red/orange counts and red_share_pct. One sentence on which bloc absorbs the week's risk.

### II. Tier-1 schedule and clashes (HCM)
List material red / tier-1 events by session. Then list each clash with currencies and why the pair is exposed (e.g. USD+CAD at the same 19:30 clock).

### III. Macro reflexive read
Prevailing bias implied by forecast vs previous on red events. Where consensus already moved vs last print. What story the calendar is testing this week.

### IV. Soros falsification criteria
For each swing hypothesis you keep, write: *this bias is invalid if [event] at [HCM clock] prints [direction vs forecast]*. Be specific and calendar-bound.

### V. Swing watchlist
Exactly 2–3 pairs. For each: why the calendar is asymmetric, which HCM window matters, what to defend (not how to enter).

### VI. What remains uncertain
Missing actuals, speeches without a number, incomplete coverage. Do not paper over gaps.

---

End the report. No extra sections, no daily checklist, no trading signals.


## User

Dưới đây là Fact Pack đã tính sẵn từ gold/mart. Mọi số đếm, tỷ trọng, giờ HCM và fact_id đều đã xác minh. Viết báo cáo theo contract. Không tự tính lại số.

# Fact Pack 2026-W36 (2026-08-31 → 2026-09-06)
Timezone: Asia/Ho_Chi_Minh. Source: data/gold/mart.

## Coverage
- Total events: 96
- By impact: {'red': 12, 'orange': 6, 'yellow': 78, 'gray': 0}
- Event dates in mart: 2026-08-31 → 2026-09-04

## Currency exposure (red share of all red events)
| Currency | Red | Orange | Yellow | Red share % |
|---|---:|---:|---:|---:|
| CAD | 5 | 0 | 3 | 41.7 |
| NZD | 4 | 0 | 5 | 33.3 |
| USD | 3 | 4 | 15 | 25.0 |
| CHF | 0 | 1 | 3 | 0.0 |
| EUR | 0 | 1 | 23 | 0.0 |
| AUD | 0 | 0 | 9 | 0.0 |
| CNY | 0 | 0 | 4 | 0.0 |
| GBP | 0 | 0 | 7 | 0.0 |
| JPY | 0 | 0 | 9 | 0.0 |

## Session exposure (red + orange only, HCM clock)
| Session | Red | Orange | Event count |
|---|---:|---:|---:|
| asia | 4 | 0 | 4 |
| europe | 0 | 1 | 1 |
| us | 8 | 4 | 12 |
| off_hours | 0 | 0 | 0 |
| untimed | 0 | 1 | 1 |

## Clashes (red/orange within 30 minutes)

### Clash 1 — Tuesday 2026-09-01T21:00:00+07:00 (USD, 2 events)
- [orange] 21:00 USD ISM Manufacturing Prices (F 70.5 / P 71.1 / A 71.1; fact_id=2835)
- [orange] 21:00 USD JOLTS Job Openings (F 7.33M / P 7.18M / A 7.27M; fact_id=2836)

### Clash 2 — Wednesday 2026-09-02T09:00:00+07:00 (NZD, 3 events)
- [red] 09:00 NZD Official Cash Rate (F 2.75% / P 2.50% / A 2.75%; fact_id=2846)
- [red] 09:00 NZD RBNZ Monetary Policy Statement (F — / P — / A —; fact_id=2847)
- [red] 09:00 NZD RBNZ Rate Statement (F — / P — / A —; fact_id=2848)

### Clash 3 — Wednesday 2026-09-02T20:45:00+07:00 (CAD, 2 events)
- [red] 20:45 CAD BOC Rate Statement (F — / P — / A —; fact_id=2844)
- [red] 20:45 CAD Overnight Rate (F 2.25% / P 2.25% / A 2.25%; fact_id=2845)

### Clash 4 — Friday 2026-09-04T19:30:00+07:00 (CAD/USD, 5 events)
- [red] 19:30 CAD Employment Change (F 15.1K / P 75.1K / A —; fact_id=2887)
- [red] 19:30 CAD Unemployment Rate (F 6.4% / P 6.4% / A —; fact_id=2888)
- [red] 19:30 USD Average Hourly Earnings m/m (F 0.3% / P 0.1% / A —; fact_id=2889)
- [red] 19:30 USD Non-Farm Employment Change (F 55K / P -23K / A —; fact_id=2890)
- [red] 19:30 USD Unemployment Rate (F 4.1% / P 4.1% / A —; fact_id=2891)


## Red events
| Date | Weekday | HCM | CCY | Event | Forecast | Previous | Actual | fact_id |
|---|---|---|---|---|---|---|---|---:|
| 2026-09-02 | Wednesday | 09:00 | NZD | Official Cash Rate | 2.75% | 2.50% | 2.75% | 2846 |
| 2026-09-02 | Wednesday | 09:00 | NZD | RBNZ Monetary Policy Statement | — | — | — | 2847 |
| 2026-09-02 | Wednesday | 09:00 | NZD | RBNZ Rate Statement | — | — | — | 2848 |
| 2026-09-02 | Wednesday | 10:00 | NZD | RBNZ Press Conference | — | — | — | 2839 |
| 2026-09-02 | Wednesday | 20:45 | CAD | BOC Rate Statement | — | — | — | 2844 |
| 2026-09-02 | Wednesday | 20:45 | CAD | Overnight Rate | 2.25% | 2.25% | 2.25% | 2845 |
| 2026-09-02 | Wednesday | 21:30 | CAD | BOC Press Conference | — | — | — | 2850 |
| 2026-09-04 | Friday | 19:30 | CAD | Employment Change | 15.1K | 75.1K | — | 2887 |
| 2026-09-04 | Friday | 19:30 | CAD | Unemployment Rate | 6.4% | 6.4% | — | 2888 |
| 2026-09-04 | Friday | 19:30 | USD | Average Hourly Earnings m/m | 0.3% | 0.1% | — | 2889 |
| 2026-09-04 | Friday | 19:30 | USD | Non-Farm Employment Change | 55K | -23K | — | 2890 |
| 2026-09-04 | Friday | 19:30 | USD | Unemployment Rate | 4.1% | 4.1% | — | 2891 |

## Expectation shifts (red, forecast ≠ previous)

- 2026-09-02 09:00 NZD Official Cash Rate: forecast 2.75% vs previous 2.50% (fact_id=2846)
- 2026-09-04 19:30 CAD Employment Change: forecast 15.1K vs previous 75.1K (fact_id=2887)
- 2026-09-04 19:30 USD Average Hourly Earnings m/m: forecast 0.3% vs previous 0.1% (fact_id=2889)
- 2026-09-04 19:30 USD Non-Farm Employment Change: forecast 55K vs previous -23K (fact_id=2890)


## Fact Pack JSON

```json
{
  "year": 2026,
  "iso_week": 36,
  "week_label": "2026-W36",
  "week_start": "2026-08-31",
  "week_end": "2026-09-06",
  "timezone": "Asia/Ho_Chi_Minh",
  "source": "data/gold/mart",
  "coverage": {
    "total_events": 96,
    "by_impact": {
      "red": 12,
      "orange": 6,
      "yellow": 78,
      "gray": 0
    },
    "event_date_min": "2026-08-31",
    "event_date_max": "2026-09-04"
  },
  "currency_exposure": [
    {
      "currency": "CAD",
      "red": 5,
      "orange": 0,
      "yellow": 3,
      "red_share_pct": 41.7
    },
    {
      "currency": "NZD",
      "red": 4,
      "orange": 0,
      "yellow": 5,
      "red_share_pct": 33.3
    },
    {
      "currency": "USD",
      "red": 3,
      "orange": 4,
      "yellow": 15,
      "red_share_pct": 25.0
    },
    {
      "currency": "CHF",
      "red": 0,
      "orange": 1,
      "yellow": 3,
      "red_share_pct": 0.0
    },
    {
      "currency": "EUR",
      "red": 0,
      "orange": 1,
      "yellow": 23,
      "red_share_pct": 0.0
    },
    {
      "currency": "AUD",
      "red": 0,
      "orange": 0,
      "yellow": 9,
      "red_share_pct": 0.0
    },
    {
      "currency": "CNY",
      "red": 0,
      "orange": 0,
      "yellow": 4,
      "red_share_pct": 0.0
    },
    {
      "currency": "GBP",
      "red": 0,
      "orange": 0,
      "yellow": 7,
      "red_share_pct": 0.0
    },
    {
      "currency": "JPY",
      "red": 0,
      "orange": 0,
      "yellow": 9,
      "red_share_pct": 0.0
    }
  ],
  "session_exposure": {
    "asia": {
      "red": 4,
      "orange": 0,
      "event_count": 4
    },
    "europe": {
      "red": 0,
      "orange": 1,
      "event_count": 1
    },
    "us": {
      "red": 8,
      "orange": 4,
      "event_count": 12
    },
    "off_hours": {
      "red": 0,
      "orange": 0,
      "event_count": 0
    },
    "untimed": {
      "red": 0,
      "orange": 1,
      "event_count": 1
    }
  },
  "clashes": [
    {
      "datetime_hcm": "2026-09-01T21:00:00+07:00",
      "end_datetime_hcm": "2026-09-01T21:00:00+07:00",
      "weekday": "Tuesday",
      "currencies": [
        "USD"
      ],
      "pair_hint": "USD",
      "event_count": 2,
      "events": [
        {
          "fact_id": 2835,
          "event_date": "2026-09-01",
          "weekday": "Tuesday",
          "datetime_hcm": "2026-09-01T21:00:00+07:00",
          "clock_hcm": "21:00",
          "session": "us",
          "currency": "USD",
          "impact": "orange",
          "event": "ISM Manufacturing Prices",
          "forecast": "70.5",
          "previous": "71.1",
          "actual": "71.1",
          "tier1_group": null,
          "expectation_shifted": true
        },
        {
          "fact_id": 2836,
          "event_date": "2026-09-01",
          "weekday": "Tuesday",
          "datetime_hcm": "2026-09-01T21:00:00+07:00",
          "clock_hcm": "21:00",
          "session": "us",
          "currency": "USD",
          "impact": "orange",
          "event": "JOLTS Job Openings",
          "forecast": "7.33M",
          "previous": "7.18M",
          "actual": "7.27M",
          "tier1_group": null,
          "expectation_shifted": true
        }
      ]
    },
    {
      "datetime_hcm": "2026-09-02T09:00:00+07:00",
      "end_datetime_hcm": "2026-09-02T09:00:00+07:00",
      "weekday": "Wednesday",
      "currencies": [
        "NZD"
      ],
      "pair_hint": "NZD",
      "event_count": 3,
      "events": [
        {
          "fact_id": 2846,
          "event_date": "2026-09-02",
          "weekday": "Wednesday",
          "datetime_hcm": "2026-09-02T09:00:00+07:00",
          "clock_hcm": "09:00",
          "session": "asia",
          "currency": "NZD",
          "impact": "red",
          "event": "Official Cash Rate",
          "forecast": "2.75%",
          "previous": "2.50%",
          "actual": "2.75%",
          "tier1_group": "rates",
          "expectation_shifted": true
        },
        {
          "fact_id": 2847,
          "event_date": "2026-09-02",
          "weekday": "Wednesday",
          "datetime_hcm": "2026-09-02T09:00:00+07:00",
          "clock_hcm": "09:00",
          "session": "asia",
          "currency": "NZD",
          "impact": "red",
          "event": "RBNZ Monetary Policy Statement",
          "forecast": "",
          "previous": "",
          "actual": "",
          "tier1_group": "rates",
          "expectation_shifted": false
        },
        {
          "fact_id": 2848,
          "event_date": "2026-09-02",
          "weekday": "Wednesday",
          "datetime_hcm": "2026-09-02T09:00:00+07:00",
          "clock_hcm": "09:00",
          "session": "asia",
          "currency": "NZD",
          "impact": "red",
          "event": "RBNZ Rate Statement",
          "forecast": "",
          "previous": "",
          "actual": "",
          "tier1_group": "rates",
          "expectation_shifted": false
        }
      ]
    },
    {
      "datetime_hcm": "2026-09-02T20:45:00+07:00",
      "end_datetime_hcm": "2026-09-02T20:45:00+07:00",
      "weekday": "Wednesday",
      "currencies": [
        "CAD"
      ],
      "pair_hint": "CAD",
      "event_count": 2,
      "events": [
        {
          "fact_id": 2844,
          "event_date": "2026-09-02",
          "weekday": "Wednesday",
          "datetime_hcm": "2026-09-02T20:45:00+07:00",
          "clock_hcm": "20:45",
          "session": "us",
          "currency": "CAD",
          "impact": "red",
          "event": "BOC Rate Statement",
          "forecast": "",
          "previous": "",
          "actual": "",
          "tier1_group": "rates",
          "expectation_shifted": false
        },
        {
          "fact_id": 2845,
          "event_date": "2026-09-02",
          "weekday": "Wednesday",
          "datetime_hcm": "2026-09-02T20:45:00+07:00",
          "clock_hcm": "20:45",
          "session": "us",
          "currency": "CAD",
          "impact": "red",
          "event": "Overnight Rate",
          "forecast": "2.25%",
          "previous": "2.25%",
          "actual": "2.25%",
          "tier1_group": "rates",
          "expectation_shifted": false
        }
      ]
    },
    {
      "datetime_hcm": "2026-09-04T19:30:00+07:00",
      "end_datetime_hcm": "2026-09-04T19:30:00+07:00",
      "weekday": "Friday",
      "currencies": [
        "CAD",
        "USD"
      ],
      "pair_hint": "CAD/USD",
      "event_count": 5,
      "events": [
        {
          "fact_id": 2887,
          "event_date": "2026-09-04",
          "weekday": "Friday",
          "datetime_hcm": "2026-09-04T19:30:00+07:00",
          "clock_hcm": "19:30",
          "session": "us",
          "currency": "CAD",
          "impact": "red",
          "event": "Employment Change",
          "forecast": "15.1K",
          "previous": "75.1K",
          "actual": "",
          "tier1_group": "labor",
          "expectation_shifted": true
        },
        {
          "fact_id": 2888,
          "event_date": "2026-09-04",
          "weekday": "Friday",
          "datetime_hcm": "2026-09-04T19:30:00+07:00",
          "clock_hcm": "19:30",
          "session": "us",
          "currency": "CAD",
          "impact": "red",
          "event": "Unemployment Rate",
          "forecast": "6.4%",
          "previous": "6.4%",
          "actual": "",
          "tier1_group": "labor",
          "expectation_shifted": false
        },
        {
          "fact_id": 2889,
          "event_date": "2026-09-04",
          "weekday": "Friday",
          "datetime_hcm": "2026-09-04T19:30:00+07:00",
          "clock_hcm": "19:30",
          "session": "us",
          "currency": "USD",
          "impact": "red",
          "event": "Average Hourly Earnings m/m",
          "forecast": "0.3%",
          "previous": "0.1%",
          "actual": "",
          "tier1_group": "labor",
          "expectation_shifted": true
        },
        {
          "fact_id": 2890,
          "event_date": "2026-09-04",
          "weekday": "Friday",
          "datetime_hcm": "2026-09-04T19:30:00+07:00",
          "clock_hcm": "19:30",
          "session": "us",
          "currency": "USD",
          "impact": "red",
          "event": "Non-Farm Employment Change",
          "forecast": "55K",
          "previous": "-23K",
          "actual": "",
          "tier1_group": "labor",
          "expectation_shifted": true
        },
        {
          "fact_id": 2891,
          "event_date": "2026-09-04",
          "weekday": "Friday",
          "datetime_hcm": "2026-09-04T19:30:00+07:00",
          "clock_hcm": "19:30",
          "session": "us",
          "currency": "USD",
          "impact": "red",
          "event": "Unemployment Rate",
          "forecast": "4.1%",
          "previous": "4.1%",
          "actual": "",
          "tier1_group": "labor",
          "expectation_shifted": false
        }
      ]
    }
  ],
  "tier1_events": [
    {
      "fact_id": 2804,
      "event_date": "2026-09-01",
      "weekday": "Tuesday",
      "datetime_hcm": "",
      "clock_hcm": "",
      "session": "untimed",
      "currency": "EUR",
      "impact": "orange",
      "event": "CPI Flash Estimate y/y",
      "forecast": "3.3%",
      "previous": "2.9%",
      "actual": "3.3%",
      "tier1_group": "inflation",
      "expectation_shifted": true
    },
    {
      "fact_id": 2846,
      "event_date": "2026-09-02",
      "weekday": "Wednesday",
      "datetime_hcm": "2026-09-02T09:00:00+07:00",
      "clock_hcm": "09:00",
      "session": "asia",
      "currency": "NZD",
      "impact": "red",
      "event": "Official Cash Rate",
      "forecast": "2.75%",
      "previous": "2.50%",
      "actual": "2.75%",
      "tier1_group": "rates",
      "expectation_shifted": true
    },
    {
      "fact_id": 2847,
      "event_date": "2026-09-02",
      "weekday": "Wednesday",
      "datetime_hcm": "2026-09-02T09:00:00+07:00",
      "clock_hcm": "09:00",
      "session": "asia",
      "currency": "NZD",
      "impact": "red",
      "event": "RBNZ Monetary Policy Statement",
      "forecast": "",
      "previous": "",
      "actual": "",
      "tier1_group": "rates",
      "expectation_shifted": false
    },
    {
      "fact_id": 2848,
      "event_date": "2026-09-02",
      "weekday": "Wednesday",
      "datetime_hcm": "2026-09-02T09:00:00+07:00",
      "clock_hcm": "09:00",
      "session": "asia",
      "currency": "NZD",
      "impact": "red",
      "event": "RBNZ Rate Statement",
      "forecast": "",
      "previous": "",
      "actual": "",
      "tier1_group": "rates",
      "expectation_shifted": false
    },
    {
      "fact_id": 2839,
      "event_date": "2026-09-02",
      "weekday": "Wednesday",
      "datetime_hcm": "2026-09-02T10:00:00+07:00",
      "clock_hcm": "10:00",
      "session": "asia",
      "currency": "NZD",
      "impact": "red",
      "event": "RBNZ Press Conference",
      "forecast": "",
      "previous": "",
      "actual": "",
      "tier1_group": "rates",
      "expectation_shifted": false
    },
    {
      "fact_id": 2844,
      "event_date": "2026-09-02",
      "weekday": "Wednesday",
      "datetime_hcm": "2026-09-02T20:45:00+07:00",
      "clock_hcm": "20:45",
      "session": "us",
      "currency": "CAD",
      "impact": "red",
      "event": "BOC Rate Statement",
      "forecast": "",
      "previous": "",
      "actual": "",
      "tier1_group": "rates",
      "expectation_shifted": false
    },
    {
      "fact_id": 2845,
      "event_date": "2026-09-02",
      "weekday": "Wednesday",
      "datetime_hcm": "2026-09-02T20:45:00+07:00",
      "clock_hcm": "20:45",
      "session": "us",
      "currency": "CAD",
      "impact": "red",
      "event": "Overnight Rate",
      "forecast": "2.25%",
      "previous": "2.25%",
      "actual": "2.25%",
      "tier1_group": "rates",
      "expectation_shifted": false
    },
    {
      "fact_id": 2850,
      "event_date": "2026-09-02",
      "weekday": "Wednesday",
      "datetime_hcm": "2026-09-02T21:30:00+07:00",
      "clock_hcm": "21:30",
      "session": "us",
      "currency": "CAD",
      "impact": "red",
      "event": "BOC Press Conference",
      "forecast": "",
      "previous": "",
      "actual": "",
      "tier1_group": "rates",
      "expectation_shifted": false
    },
    {
      "fact_id": 2854,
      "event_date": "2026-09-03",
      "weekday": "Thursday",
      "datetime_hcm": "2026-09-03T13:30:00+07:00",
      "clock_hcm": "13:30",
      "session": "europe",
      "currency": "CHF",
      "impact": "orange",
      "event": "CPI m/m",
      "forecast": "0.0%",
      "previous": "-0.1%",
      "actual": "0.4%",
      "tier1_group": "inflation",
      "expectation_shifted": true
    },
    {
      "fact_id": 2877,
      "event_date": "2026-09-03",
      "weekday": "Thursday",
      "datetime_hcm": "2026-09-03T21:00:00+07:00",
      "clock_hcm": "21:00",
      "session": "us",
      "currency": "USD",
      "impact": "orange",
      "event": "ISM Services PMI",
      "forecast": "54.2",
      "previous": "54.1",
      "actual": "",
      "tier1_group": "activity",
      "expectation_shifted": true
    },
    {
      "fact_id": 2887,
      "event_date": "2026-09-04",
      "weekday": "Friday",
      "datetime_hcm": "2026-09-04T19:30:00+07:00",
      "clock_hcm": "19:30",
      "session": "us",
      "currency": "CAD",
      "impact": "red",
      "event": "Employment Change",
      "forecast": "15.1K",
      "previous": "75.1K",
      "actual": "",
      "tier1_group": "labor",
      "expectation_shifted": true
    },
    {
      "fact_id": 2888,
      "event_date": "2026-09-04",
      "weekday": "Friday",
      "datetime_hcm": "2026-09-04T19:30:00+07:00",
      "clock_hcm": "19:30",
      "session": "us",
      "currency": "CAD",
      "impact": "red",
      "event": "Unemployment Rate",
      "forecast": "6.4%",
      "previous": "6.4%",
      "actual": "",
      "tier1_group": "labor",
      "expectation_shifted": false
    },
    {
      "fact_id": 2889,
      "event_date": "2026-09-04",
      "weekday": "Friday",
      "datetime_hcm": "2026-09-04T19:30:00+07:00",
      "clock_hcm": "19:30",
      "session": "us",
      "currency": "USD",
      "impact": "red",
      "event": "Average Hourly Earnings m/m",
      "forecast": "0.3%",
      "previous": "0.1%",
      "actual": "",
      "tier1_group": "labor",
      "expectation_shifted": true
    },
    {
      "fact_id": 2890,
      "event_date": "2026-09-04",
      "weekday": "Friday",
      "datetime_hcm": "2026-09-04T19:30:00+07:00",
      "clock_hcm": "19:30",
      "session": "us",
      "currency": "USD",
      "impact": "red",
      "event": "Non-Farm Employment Change",
      "forecast": "55K",
      "previous": "-23K",
      "actual": "",
      "tier1_group": "labor",
      "expectation_shifted": true
    },
    {
      "fact_id": 2891,
      "event_date": "2026-09-04",
      "weekday": "Friday",
      "datetime_hcm": "2026-09-04T19:30:00+07:00",
      "clock_hcm": "19:30",
      "session": "us",
      "currency": "USD",
      "impact": "red",
      "event": "Unemployment Rate",
      "forecast": "4.1%",
      "previous": "4.1%",
      "actual": "",
      "tier1_group": "labor",
      "expectation_shifted": false
    }
  ],
  "red_events": [
    {
      "fact_id": 2846,
      "event_date": "2026-09-02",
      "weekday": "Wednesday",
      "datetime_hcm": "2026-09-02T09:00:00+07:00",
      "clock_hcm": "09:00",
      "session": "asia",
      "currency": "NZD",
      "impact": "red",
      "event": "Official Cash Rate",
      "forecast": "2.75%",
      "previous": "2.50%",
      "actual": "2.75%",
      "tier1_group": "rates",
      "expectation_shifted": true
    },
    {
      "fact_id": 2847,
      "event_date": "2026-09-02",
      "weekday": "Wednesday",
      "datetime_hcm": "2026-09-02T09:00:00+07:00",
      "clock_hcm": "09:00",
      "session": "asia",
      "currency": "NZD",
      "impact": "red",
      "event": "RBNZ Monetary Policy Statement",
      "forecast": "",
      "previous": "",
      "actual": "",
      "tier1_group": "rates",
      "expectation_shifted": false
    },
    {
      "fact_id": 2848,
      "event_date": "2026-09-02",
      "weekday": "Wednesday",
      "datetime_hcm": "2026-09-02T09:00:00+07:00",
      "clock_hcm": "09:00",
      "session": "asia",
      "currency": "NZD",
      "impact": "red",
      "event": "RBNZ Rate Statement",
      "forecast": "",
      "previous": "",
      "actual": "",
      "tier1_group": "rates",
      "expectation_shifted": false
    },
    {
      "fact_id": 2839,
      "event_date": "2026-09-02",
      "weekday": "Wednesday",
      "datetime_hcm": "2026-09-02T10:00:00+07:00",
      "clock_hcm": "10:00",
      "session": "asia",
      "currency": "NZD",
      "impact": "red",
      "event": "RBNZ Press Conference",
      "forecast": "",
      "previous": "",
      "actual": "",
      "tier1_group": "rates",
      "expectation_shifted": false
    },
    {
      "fact_id": 2844,
      "event_date": "2026-09-02",
      "weekday": "Wednesday",
      "datetime_hcm": "2026-09-02T20:45:00+07:00",
      "clock_hcm": "20:45",
      "session": "us",
      "currency": "CAD",
      "impact": "red",
      "event": "BOC Rate Statement",
      "forecast": "",
      "previous": "",
      "actual": "",
      "tier1_group": "rates",
      "expectation_shifted": false
    },
    {
      "fact_id": 2845,
      "event_date": "2026-09-02",
      "weekday": "Wednesday",
      "datetime_hcm": "2026-09-02T20:45:00+07:00",
      "clock_hcm": "20:45",
      "session": "us",
      "currency": "CAD",
      "impact": "red",
      "event": "Overnight Rate",
      "forecast": "2.25%",
      "previous": "2.25%",
      "actual": "2.25%",
      "tier1_group": "rates",
      "expectation_shifted": false
    },
    {
      "fact_id": 2850,
      "event_date": "2026-09-02",
      "weekday": "Wednesday",
      "datetime_hcm": "2026-09-02T21:30:00+07:00",
      "clock_hcm": "21:30",
      "session": "us",
      "currency": "CAD",
      "impact": "red",
      "event": "BOC Press Conference",
      "forecast": "",
      "previous": "",
      "actual": "",
      "tier1_group": "rates",
      "expectation_shifted": false
    },
    {
      "fact_id": 2887,
      "event_date": "2026-09-04",
      "weekday": "Friday",
      "datetime_hcm": "2026-09-04T19:30:00+07:00",
      "clock_hcm": "19:30",
      "session": "us",
      "currency": "CAD",
      "impact": "red",
      "event": "Employment Change",
      "forecast": "15.1K",
      "previous": "75.1K",
      "actual": "",
      "tier1_group": "labor",
      "expectation_shifted": true
    },
    {
      "fact_id": 2888,
      "event_date": "2026-09-04",
      "weekday": "Friday",
      "datetime_hcm": "2026-09-04T19:30:00+07:00",
      "clock_hcm": "19:30",
      "session": "us",
      "currency": "CAD",
      "impact": "red",
      "event": "Unemployment Rate",
      "forecast": "6.4%",
      "previous": "6.4%",
      "actual": "",
      "tier1_group": "labor",
      "expectation_shifted": false
    },
    {
      "fact_id": 2889,
      "event_date": "2026-09-04",
      "weekday": "Friday",
      "datetime_hcm": "2026-09-04T19:30:00+07:00",
      "clock_hcm": "19:30",
      "session": "us",
      "currency": "USD",
      "impact": "red",
      "event": "Average Hourly Earnings m/m",
      "forecast": "0.3%",
      "previous": "0.1%",
      "actual": "",
      "tier1_group": "labor",
      "expectation_shifted": true
    },
    {
      "fact_id": 2890,
      "event_date": "2026-09-04",
      "weekday": "Friday",
      "datetime_hcm": "2026-09-04T19:30:00+07:00",
      "clock_hcm": "19:30",
      "session": "us",
      "currency": "USD",
      "impact": "red",
      "event": "Non-Farm Employment Change",
      "forecast": "55K",
      "previous": "-23K",
      "actual": "",
      "tier1_group": "labor",
      "expectation_shifted": true
    },
    {
      "fact_id": 2891,
      "event_date": "2026-09-04",
      "weekday": "Friday",
      "datetime_hcm": "2026-09-04T19:30:00+07:00",
      "clock_hcm": "19:30",
      "session": "us",
      "currency": "USD",
      "impact": "red",
      "event": "Unemployment Rate",
      "forecast": "4.1%",
      "previous": "4.1%",
      "actual": "",
      "tier1_group": "labor",
      "expectation_shifted": false
    }
  ],
  "orange_events": [
    {
      "fact_id": 2804,
      "event_date": "2026-09-01",
      "weekday": "Tuesday",
      "datetime_hcm": "",
      "clock_hcm": "",
      "session": "untimed",
      "currency": "EUR",
      "impact": "orange",
      "event": "CPI Flash Estimate y/y",
      "forecast": "3.3%",
      "previous": "2.9%",
      "actual": "3.3%",
      "tier1_group": "inflation",
      "expectation_shifted": true
    },
    {
      "fact_id": 2835,
      "event_date": "2026-09-01",
      "weekday": "Tuesday",
      "datetime_hcm": "2026-09-01T21:00:00+07:00",
      "clock_hcm": "21:00",
      "session": "us",
      "currency": "USD",
      "impact": "orange",
      "event": "ISM Manufacturing Prices",
      "forecast": "70.5",
      "previous": "71.1",
      "actual": "71.1",
      "tier1_group": null,
      "expectation_shifted": true
    },
    {
      "fact_id": 2836,
      "event_date": "2026-09-01",
      "weekday": "Tuesday",
      "datetime_hcm": "2026-09-01T21:00:00+07:00",
      "clock_hcm": "21:00",
      "session": "us",
      "currency": "USD",
      "impact": "orange",
      "event": "JOLTS Job Openings",
      "forecast": "7.33M",
      "previous": "7.18M",
      "actual": "7.27M",
      "tier1_group": null,
      "expectation_shifted": true
    },
    {
      "fact_id": 2854,
      "event_date": "2026-09-03",
      "weekday": "Thursday",
      "datetime_hcm": "2026-09-03T13:30:00+07:00",
      "clock_hcm": "13:30",
      "session": "europe",
      "currency": "CHF",
      "impact": "orange",
      "event": "CPI m/m",
      "forecast": "0.0%",
      "previous": "-0.1%",
      "actual": "0.4%",
      "tier1_group": "inflation",
      "expectation_shifted": true
    },
    {
      "fact_id": 2871,
      "event_date": "2026-09-03",
      "weekday": "Thursday",
      "datetime_hcm": "2026-09-03T19:30:00+07:00",
      "clock_hcm": "19:30",
      "session": "us",
      "currency": "USD",
      "impact": "orange",
      "event": "Unemployment Claims",
      "forecast": "205K",
      "previous": "203K",
      "actual": "",
      "tier1_group": null,
      "expectation_shifted": true
    },
    {
      "fact_id": 2877,
      "event_date": "2026-09-03",
      "weekday": "Thursday",
      "datetime_hcm": "2026-09-03T21:00:00+07:00",
      "clock_hcm": "21:00",
      "session": "us",
      "currency": "USD",
      "impact": "orange",
      "event": "ISM Services PMI",
      "forecast": "54.2",
      "previous": "54.1",
      "actual": "",
      "tier1_group": "activity",
      "expectation_shifted": true
    }
  ],
  "expectation_shifts": [
    {
      "fact_id": 2846,
      "event_date": "2026-09-02",
      "weekday": "Wednesday",
      "datetime_hcm": "2026-09-02T09:00:00+07:00",
      "clock_hcm": "09:00",
      "session": "asia",
      "currency": "NZD",
      "impact": "red",
      "event": "Official Cash Rate",
      "forecast": "2.75%",
      "previous": "2.50%",
      "actual": "2.75%",
      "tier1_group": "rates",
      "expectation_shifted": true
    },
    {
      "fact_id": 2887,
      "event_date": "2026-09-04",
      "weekday": "Friday",
      "datetime_hcm": "2026-09-04T19:30:00+07:00",
      "clock_hcm": "19:30",
      "session": "us",
      "currency": "CAD",
      "impact": "red",
      "event": "Employment Change",
      "forecast": "15.1K",
      "previous": "75.1K",
      "actual": "",
      "tier1_group": "labor",
      "expectation_shifted": true
    },
    {
      "fact_id": 2889,
      "event_date": "2026-09-04",
      "weekday": "Friday",
      "datetime_hcm": "2026-09-04T19:30:00+07:00",
      "clock_hcm": "19:30",
      "session": "us",
      "currency": "USD",
      "impact": "red",
      "event": "Average Hourly Earnings m/m",
      "forecast": "0.3%",
      "previous": "0.1%",
      "actual": "",
      "tier1_group": "labor",
      "expectation_shifted": true
    },
    {
      "fact_id": 2890,
      "event_date": "2026-09-04",
      "weekday": "Friday",
      "datetime_hcm": "2026-09-04T19:30:00+07:00",
      "clock_hcm": "19:30",
      "session": "us",
      "currency": "USD",
      "impact": "red",
      "event": "Non-Farm Employment Change",
      "forecast": "55K",
      "previous": "-23K",
      "actual": "",
      "tier1_group": "labor",
      "expectation_shifted": true
    }
  ],
  "generated_at": "2026-09-05T23:36:54+07:00"
}
```
