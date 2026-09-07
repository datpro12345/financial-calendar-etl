# Fact Pack 2026-W36 (2026-08-31 → 2026-09-06)
Timezone: Asia/Ho_Chi_Minh. Source: data/gold/mart.

## Coverage
- Total events: 116
- By impact: {'red': 15, 'orange': 12, 'yellow': 88, 'gray': 1}
- Event dates in mart: 2026-08-31 → 2026-09-04

## Liquidity holidays (gray / session closures)
Bank holidays and non-economic closures thin the session for that currency. Use these in Time & liquidity windows.
| Date | Weekday | CCY | Focus | Event | fact_id |
|---|---|---|---|---|---:|
| 2026-08-31 | Monday | GBP | primary | Bank Holiday | 1ce36c9a5aaacc30 |

## Focus split — primary ['USD', 'EUR', 'GBP', 'JPY'] vs secondary ['AUD', 'NZD', 'CAD', 'CHF', 'CNY']
- Primary red (USD/EUR/GBP/JPY): 5
- Secondary red (AUD/NZD/CAD/CHF/CNY): 10

## Currency exposure — PRIMARY (USD EUR GBP JPY)
| Currency | Red | Orange | Yellow | Red share % |
|---|---:|---:|---:|---:|
| USD | 4 | 5 | 19 | 26.7 |
| GBP | 1 | 0 | 9 | 6.7 |
| EUR | 0 | 4 | 25 | 0.0 |
| JPY | 0 | 0 | 9 | 0.0 |

## Currency exposure — SECONDARY (AUD NZD CAD CHF CNY)
| Currency | Red | Orange | Yellow | Red share % |
|---|---:|---:|---:|---:|
| CAD | 5 | 1 | 3 | 33.3 |
| NZD | 4 | 1 | 5 | 26.7 |
| AUD | 1 | 0 | 9 | 6.7 |
| CHF | 0 | 1 | 3 | 0.0 |
| ALL | 0 | 0 | 2 | 0.0 |
| CNY | 0 | 0 | 4 | 0.0 |

## Session exposure (red + orange only, HCM clock)
| Session | Red | Orange | Event count |
|---|---:|---:|---:|
| asia | 5 | 0 | 5 |
| europe | 1 | 4 | 5 |
| us | 9 | 6 | 15 |
| off_hours | 0 | 1 | 1 |
| untimed | 0 | 1 | 1 |

## Clashes (red/orange within 30 minutes)

### Clash 1 — Tuesday 2026-09-01T16:00:00+07:00 (EUR, 2 events)
- [orange] 16:00 EUR Core CPI Flash Estimate y/y (F 2.5% / P 2.5% / A —; fact_id=3e664770b87eba83)
- [orange] 16:00 EUR CPI Flash Estimate y/y (F 3.3% / P 2.9% / A —; fact_id=d0d890f70382b033)

### Clash 2 — Tuesday 2026-09-01T21:00:00+07:00 (USD, 3 events)
- [orange] 21:00 USD ISM Manufacturing Prices (F 70.5 / P 71.1 / A 71.1; fact_id=9a5256cc6476dbce)
- [red] 21:00 USD ISM Manufacturing PMI (F 55.2 / P 55.6 / A —; fact_id=bc260cd7e4cbda85)
- [orange] 21:00 USD JOLTS Job Openings (F 7.33M / P 7.18M / A 7.27M; fact_id=e175b7c6c4161e0f)

### Clash 3 — Tuesday 2026-09-02T08:30:00+07:00 (AUD/NZD, 4 events)
- [red] 08:30 AUD GDP q/q (F 0.3% / P 0.3% / A —; fact_id=db2c8e055c2d995d)
- [red] 09:00 NZD RBNZ Rate Statement (F — / P — / A —; fact_id=39a2ff7d46870b2e)
- [red] 09:00 NZD Official Cash Rate (F 2.75% / P 2.50% / A 2.75%; fact_id=7c0469770c7d9f50)
- [red] 09:00 NZD RBNZ Monetary Policy Statement (F — / P — / A —; fact_id=954badaa751a7697)

### Clash 4 — Wednesday 2026-09-02T20:45:00+07:00 (CAD, 2 events)
- [red] 20:45 CAD Overnight Rate (F 2.25% / P 2.25% / A 2.25%; fact_id=e995897e92ef7b17)
- [red] 20:45 CAD BOC Rate Statement (F — / P — / A —; fact_id=937c2fd98cf88949)

### Clash 5 — Friday 2026-09-04T19:30:00+07:00 (CAD/USD, 5 events)
- [red] 19:30 CAD Unemployment Rate (F 6.4% / P 6.4% / A —; fact_id=40e7af12f722121c)
- [red] 19:30 CAD Employment Change (F 15.1K / P 75.1K / A —; fact_id=94a5f89a3752319d)
- [red] 19:30 USD Unemployment Rate (F 4.1% / P 4.1% / A —; fact_id=55b315bdcd164e6d)
- [red] 19:30 USD Average Hourly Earnings m/m (F 0.3% / P 0.1% / A —; fact_id=624939138e6092ee)
- [red] 19:30 USD Non-Farm Employment Change (F 55K / P -23K / A —; fact_id=b8cdd1caa71837e7)


## Red events
| Date | Weekday | HCM | CCY | Event | Forecast | Previous | Actual | fact_id |
|---|---|---|---|---|---|---|---|---:|
| 2026-09-01 | Tuesday | 21:00 | USD | ISM Manufacturing PMI | 55.2 | 55.6 | — | bc260cd7e4cbda85 |
| 2026-09-01 | Tuesday | 08:30 | AUD | GDP q/q | 0.3% | 0.3% | — | db2c8e055c2d995d |
| 2026-09-02 | Wednesday | 09:00 | NZD | RBNZ Rate Statement | — | — | — | 39a2ff7d46870b2e |
| 2026-09-02 | Wednesday | 09:00 | NZD | Official Cash Rate | 2.75% | 2.50% | 2.75% | 7c0469770c7d9f50 |
| 2026-09-02 | Wednesday | 09:00 | NZD | RBNZ Monetary Policy Statement | — | — | — | 954badaa751a7697 |
| 2026-09-02 | Wednesday | 10:00 | NZD | RBNZ Press Conference | — | — | — | 20a7d8c0e12546ba |
| 2026-09-02 | Wednesday | 20:45 | CAD | BOC Rate Statement | — | — | — | 937c2fd98cf88949 |
| 2026-09-02 | Wednesday | 20:45 | CAD | Overnight Rate | 2.25% | 2.25% | 2.25% | e995897e92ef7b17 |
| 2026-09-02 | Wednesday | 21:30 | CAD | BOC Press Conference | — | — | — | b0937fb6a33c4c1e |
| 2026-09-04 | Friday | 15:50 | GBP | BOE Gov Bailey Speaks | — | — | — | 7b596a88c9beb08c |
| 2026-09-04 | Friday | 19:30 | CAD | Unemployment Rate | 6.4% | 6.4% | — | 40e7af12f722121c |
| 2026-09-04 | Friday | 19:30 | CAD | Employment Change | 15.1K | 75.1K | — | 94a5f89a3752319d |
| 2026-09-04 | Friday | 19:30 | USD | Unemployment Rate | 4.1% | 4.1% | — | 55b315bdcd164e6d |
| 2026-09-04 | Friday | 19:30 | USD | Average Hourly Earnings m/m | 0.3% | 0.1% | — | 624939138e6092ee |
| 2026-09-04 | Friday | 19:30 | USD | Non-Farm Employment Change | 55K | -23K | — | b8cdd1caa71837e7 |

## Expectation shifts (red, forecast ≠ previous)

- 2026-09-01 21:00 USD ISM Manufacturing PMI: forecast 55.2 vs previous 55.6 (fact_id=bc260cd7e4cbda85)
- 2026-09-02 09:00 NZD Official Cash Rate: forecast 2.75% vs previous 2.50% (fact_id=7c0469770c7d9f50)
- 2026-09-04 19:30 CAD Employment Change: forecast 15.1K vs previous 75.1K (fact_id=94a5f89a3752319d)
- 2026-09-04 19:30 USD Average Hourly Earnings m/m: forecast 0.3% vs previous 0.1% (fact_id=624939138e6092ee)
- 2026-09-04 19:30 USD Non-Farm Employment Change: forecast 55K vs previous -23K (fact_id=b8cdd1caa71837e7)

## Next week look-ahead (2026-W37)

Available. Dates 2026-09-07 → 2026-09-13. Total 65. Impact {'red': 8, 'orange': 1, 'yellow': 54, 'gray': 2}. Primary red 8 / secondary red 0.

### Next week primary exposure
| Currency | Red | Orange | Yellow | Red share % |
|---|---:|---:|---:|---:|
| USD | 6 | 1 | 8 | 75.0 |
| EUR | 2 | 0 | 13 | 25.0 |
| GBP | 0 | 0 | 10 | 0.0 |
| JPY | 0 | 0 | 11 | 0.0 |

### Next week secondary exposure
| Currency | Red | Orange | Yellow | Red share % |
|---|---:|---:|---:|---:|
| AUD | 0 | 0 | 3 | 0.0 |
| CAD | 0 | 0 | 0 | 0.0 |
| CHF | 0 | 0 | 3 | 0.0 |
| CNY | 0 | 0 | 5 | 0.0 |
| NZD | 0 | 0 | 1 | 0.0 |

### Next week red events
| Date | Weekday | HCM | CCY | Focus | Event | Forecast | Previous | Actual | fact_id |
|---|---|---|---|---|---|---|---|---|---:|
| 2026-09-10 | Thursday | 19:30 | EUR | primary | Monetary Policy Statement | — | — | — | ee908909b8e667e5 |
| 2026-09-10 | Thursday | 19:30 | USD | primary | PPI m/m | — | 0.0% | — | 51cbc35b6655fc80 |
| 2026-09-10 | Thursday | 19:30 | USD | primary | Core PPI m/m | — | 0.2% | — | 839276399fb5a133 |
| 2026-09-10 | Thursday | 19:45 | EUR | primary | ECB Press Conference | — | — | — | 58030600895635de |
| 2026-09-11 | Friday | 19:30 | USD | primary | CPI m/m | — | 0.1% | — | 0b4de7803fc53493 |
| 2026-09-11 | Friday | 19:30 | USD | primary | Core CPI y/y | — | 2.5% | — | 9fe2b446c0d5b588 |
| 2026-09-11 | Friday | 19:30 | USD | primary | CPI y/y | — | 3.4% | — | f5a1906011b99eee |
| 2026-09-11 | Friday | 19:30 | USD | primary | Core CPI m/m | — | 0.2% | — | ffb565f963a7a791 |

### Next week liquidity holidays
| Date | Weekday | CCY | Focus | Event | fact_id |
|---|---|---|---|---|---:|
| 2026-09-07 | Monday | CAD | secondary | Bank Holiday | 2e56a364285afafa |
| 2026-09-07 | Monday | USD | primary | Bank Holiday | 1cd08f4f313f6948 |

### Next week clashes

- Clash 1: Thursday 2026-09-10T19:30:00+07:00 (EUR/USD, 4 events)
  - [red/primary] 19:30 EUR Monetary Policy Statement (F — / P —; fact_id=ee908909b8e667e5)
  - [red/primary] 19:30 USD PPI m/m (F — / P 0.0%; fact_id=51cbc35b6655fc80)
  - [red/primary] 19:30 USD Core PPI m/m (F — / P 0.2%; fact_id=839276399fb5a133)
  - [red/primary] 19:45 EUR ECB Press Conference (F — / P —; fact_id=58030600895635de)
- Clash 2: Friday 2026-09-11T19:30:00+07:00 (USD, 4 events)
  - [red/primary] 19:30 USD CPI m/m (F — / P 0.1%; fact_id=0b4de7803fc53493)
  - [red/primary] 19:30 USD Core CPI y/y (F — / P 2.5%; fact_id=9fe2b446c0d5b588)
  - [red/primary] 19:30 USD CPI y/y (F — / P 3.4%; fact_id=f5a1906011b99eee)
  - [red/primary] 19:30 USD Core CPI m/m (F — / P 0.2%; fact_id=ffb565f963a7a791)
