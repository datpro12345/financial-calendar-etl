"""Build a deterministic weekly fact pack from the Gold Kimball mart.

All counts, shares, session buckets, and clash clusters are computed here.
The LLM must not recalculate these numbers.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.extract.config import GOLD_MART_DIR

TIMEZONE = "Asia/Ho_Chi_Minh"
CLASH_WINDOW = pd.Timedelta(minutes=30)
MATERIAL_IMPACTS = ("red", "orange")
PRIMARY_CURRENCIES = ("USD", "EUR", "GBP", "JPY")
SECONDARY_CURRENCIES = ("AUD", "NZD", "CAD", "CHF", "CNY")

SESSION_WINDOWS = {
    "asia": ((6, 0), (12, 0)),
    "europe": ((13, 0), (18, 0)),
    "us": ((18, 30), (23, 59)),
}

TIER1_RULES = (
    ("labor", ("non-farm", "employment change", "unemployment rate", "average hourly", "adp")),
    ("inflation", ("cpi", "pce", "ppi", "inflation")),
    ("rates", ("rate statement", "official cash rate", "overnight rate", "federal funds",
               "interest rate", "monetary policy", "press conference", "cash rate")),
    ("growth", ("gdp",)),
    ("activity", ("pmi",)),
)


def iso_week_bounds(year: int, week: int) -> tuple[date, date]:
    monday = date.fromisocalendar(year, week, 1)
    return monday, monday + timedelta(days=6)


def next_iso_week(year: int, week: int) -> tuple[int, int]:
    nxt = iso_week_bounds(year, week)[0] + timedelta(days=7)
    iso = nxt.isocalendar()
    return iso.year, iso.week


def focus_for(currency: str) -> str:
    return "primary" if currency in PRIMARY_CURRENCIES else "secondary"


def _clean_txt(value: Any) -> str:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return ""
    text = str(value).strip()
    if text.lower() in {"", "nan", "n/a", "na", "none"}:
        return ""
    return text


def _parse_hcm(value: Any) -> pd.Timestamp | pd.NaT:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return pd.NaT
    return pd.to_datetime(value, errors="coerce", utc=True)


def load_mart(mart_dir: Path | None = None) -> pd.DataFrame:
    root = mart_dir or GOLD_MART_DIR
    fact = pd.read_csv(root / "fact_calendar_release.csv")
    dim_date = pd.read_csv(root / "dim_date.csv")
    dim_currency = pd.read_csv(root / "dim_currency.csv")
    dim_impact = pd.read_csv(root / "dim_impact.csv")
    dim_event = pd.read_csv(root / "dim_event.csv")
    df = (
        fact.merge(dim_date, on="date_key")
        .merge(dim_currency, on="currency_key")
        .merge(dim_impact, on="impact_key")
        .merge(dim_event, on="event_key")
    )
    df["forecast_txt"] = df["forecast_txt"].map(_clean_txt)
    df["previous_txt"] = df["previous_txt"].map(_clean_txt)
    df["actual_txt"] = df["actual_txt"].map(_clean_txt)
    df["hcm_ts"] = df["event_datetime_hcm"].map(_parse_hcm)
    return df


def classify_tier1(event_name: str) -> str | None:
    lowered = event_name.lower()
    for group, needles in TIER1_RULES:
        if any(needle in lowered for needle in needles):
            return group
    return None


def session_for(ts: pd.Timestamp | pd.NaT) -> str:
    if pd.isna(ts):
        return "untimed"
    local = ts.tz_convert(TIMEZONE)
    minutes = local.hour * 60 + local.minute
    for name, ((sh, sm), (eh, em)) in SESSION_WINDOWS.items():
        if sh * 60 + sm <= minutes <= eh * 60 + em:
            return name
    return "off_hours"


def _event_row(row: pd.Series) -> dict[str, Any]:
    ts = row["hcm_ts"]
    hcm = "" if pd.isna(ts) else ts.tz_convert(TIMEZONE).isoformat()
    clock = "" if pd.isna(ts) else ts.tz_convert(TIMEZONE).strftime("%H:%M")
    return {
        "fact_id": int(row["fact_id"]),
        "event_date": str(row["event_date"]),
        "weekday": str(row["weekday_name"]),
        "datetime_hcm": hcm,
        "clock_hcm": clock,
        "session": session_for(ts),
        "currency": str(row["currency_code"]),
        "impact": str(row["impact_code"]),
        "event": str(row["event_name"]),
        "forecast": row["forecast_txt"],
        "previous": row["previous_txt"],
        "actual": row["actual_txt"],
        "tier1_group": classify_tier1(str(row["event_name"])),
        "focus": focus_for(str(row["currency_code"])),
        "expectation_shifted": bool(
            row["forecast_txt"] and row["previous_txt"] and row["forecast_txt"] != row["previous_txt"]
        ),
    }


def _currency_exposure(week: pd.DataFrame) -> list[dict[str, Any]]:
    red_total = int((week["impact_code"] == "red").sum())
    rows = []
    for currency, group in week.groupby("currency_code"):
        red = int((group["impact_code"] == "red").sum())
        orange = int((group["impact_code"] == "orange").sum())
        yellow = int((group["impact_code"] == "yellow").sum())
        rows.append(
            {
                "currency": currency,
                "red": red,
                "orange": orange,
                "yellow": yellow,
                "red_share_pct": round((red / red_total) * 100, 1) if red_total else 0.0,
            }
        )
    rows.sort(key=lambda r: (r["red"], r["orange"]), reverse=True)
    return rows


def _session_exposure(week: pd.DataFrame) -> dict[str, Any]:
    material = week[week["impact_code"].isin(MATERIAL_IMPACTS)].copy()
    material["session"] = material["hcm_ts"].map(session_for)
    out: dict[str, Any] = {}
    for name in ("asia", "europe", "us", "off_hours", "untimed"):
        slice_df = material[material["session"] == name]
        out[name] = {
            "red": int((slice_df["impact_code"] == "red").sum()),
            "orange": int((slice_df["impact_code"] == "orange").sum()),
            "event_count": int(len(slice_df)),
        }
    return out


def _detect_clashes(week: pd.DataFrame) -> list[dict[str, Any]]:
    material = week[week["impact_code"].isin(MATERIAL_IMPACTS)].copy()
    material = material.dropna(subset=["hcm_ts"]).sort_values("hcm_ts")
    if material.empty:
        return []

    clusters: list[list[pd.Series]] = []
    current: list[pd.Series] = []
    last_ts: pd.Timestamp | None = None
    for _, row in material.iterrows():
        ts = row["hcm_ts"]
        if last_ts is None or ts - last_ts <= CLASH_WINDOW:
            current.append(row)
        else:
            if len(current) >= 2:
                clusters.append(current)
            current = [row]
        last_ts = ts
    if len(current) >= 2:
        clusters.append(current)

    clashes = []
    for cluster in clusters:
        currencies = sorted({str(r["currency_code"]) for r in cluster})
        first = cluster[0]["hcm_ts"].tz_convert(TIMEZONE)
        last = cluster[-1]["hcm_ts"].tz_convert(TIMEZONE)
        clashes.append(
            {
                "datetime_hcm": first.isoformat(),
                "end_datetime_hcm": last.isoformat(),
                "weekday": str(cluster[0]["weekday_name"]),
                "currencies": currencies,
                "pair_hint": "/".join(currencies) if len(currencies) >= 2 else currencies[0],
                "event_count": len(cluster),
                "events": [_event_row(r) for r in cluster],
            }
        )
    return clashes


def _week_core(week_df: pd.DataFrame, year: int, week: int) -> dict[str, Any]:
    monday, sunday = iso_week_bounds(year, week)
    red_events = [_event_row(r) for _, r in week_df[week_df["impact_code"] == "red"].iterrows()]
    orange_events = [_event_row(r) for _, r in week_df[week_df["impact_code"] == "orange"].iterrows()]
    exposure = _currency_exposure(week_df)
    by_impact = (
        week_df.groupby("impact_code").size().reindex(["red", "orange", "yellow", "gray"], fill_value=0)
    )
    primary_red = sum(r["red"] for r in exposure if r["currency"] in PRIMARY_CURRENCIES)
    secondary_red = sum(r["red"] for r in exposure if r["currency"] not in PRIMARY_CURRENCIES)
    return {
        "year": year,
        "iso_week": week,
        "week_label": f"{year}-W{week:02d}",
        "week_start": monday.isoformat(),
        "week_end": sunday.isoformat(),
        "coverage": {
            "total_events": int(len(week_df)),
            "by_impact": {k: int(v) for k, v in by_impact.items()},
            "event_date_min": str(week_df["event_date"].min()),
            "event_date_max": str(week_df["event_date"].max()),
        },
        "focus": {
            "primary": list(PRIMARY_CURRENCIES),
            "secondary": list(SECONDARY_CURRENCIES),
            "primary_red": int(primary_red),
            "secondary_red": int(secondary_red),
        },
        "currency_exposure": exposure,
        "currency_exposure_primary": [r for r in exposure if r["currency"] in PRIMARY_CURRENCIES],
        "currency_exposure_secondary": [r for r in exposure if r["currency"] not in PRIMARY_CURRENCIES],
        "session_exposure": _session_exposure(week_df),
        "clashes": _detect_clashes(week_df),
        "tier1_events": sorted(
            [e for e in red_events + orange_events if e["tier1_group"]],
            key=lambda e: (e["datetime_hcm"], e["currency"]),
        ),
        "red_events": sorted(red_events, key=lambda e: (e["datetime_hcm"], e["currency"])),
        "orange_events": sorted(orange_events, key=lambda e: (e["datetime_hcm"], e["currency"])),
        "expectation_shifts": [
            e for e in red_events
            if e["forecast"] and e["previous"] and e["forecast"] != e["previous"]
        ],
    }


def _next_week_snapshot(df: pd.DataFrame, year: int, week: int) -> dict[str, Any]:
    ny, nw = next_iso_week(year, week)
    monday, sunday = iso_week_bounds(ny, nw)
    label = f"{ny}-W{nw:02d}"
    next_df = df[(df["year"] == ny) & (df["iso_week"] == nw)].copy()
    if next_df.empty:
        return {
            "available": False,
            "year": ny,
            "iso_week": nw,
            "week_label": label,
            "week_start": monday.isoformat(),
            "week_end": sunday.isoformat(),
        }
    core = _week_core(next_df, ny, nw)
    return {
        "available": True,
        "year": core["year"],
        "iso_week": core["iso_week"],
        "week_label": core["week_label"],
        "week_start": core["week_start"],
        "week_end": core["week_end"],
        "coverage": core["coverage"],
        "focus": core["focus"],
        "currency_exposure_primary": core["currency_exposure_primary"],
        "currency_exposure_secondary": core["currency_exposure_secondary"],
        "clashes": core["clashes"],
        "red_events": core["red_events"],
        "expectation_shifts": core["expectation_shifts"],
    }


def build_fact_pack(year: int, week: int, mart_dir: Path | None = None) -> dict[str, Any]:
    df = load_mart(mart_dir)
    week_df = df[(df["year"] == year) & (df["iso_week"] == week)].copy()
    if week_df.empty:
        raise ValueError(f"No mart rows for ISO week {year}-W{week:02d}")
    pack = _week_core(week_df, year, week)
    pack["timezone"] = TIMEZONE
    pack["source"] = "data/gold/mart"
    pack["next_week"] = _next_week_snapshot(df, year, week)
    pack["generated_at"] = datetime.now().astimezone().isoformat(timespec="seconds")
    return pack


def fact_pack_to_markdown(pack: dict[str, Any]) -> str:
    """Human-readable tables for the LLM user message. Numbers stay identical to JSON."""
    lines = [
        f"# Fact Pack {pack['week_label']} ({pack['week_start']} → {pack['week_end']})",
        f"Timezone: {pack['timezone']}. Source: {pack['source']}.",
        "",
        "## Coverage",
        f"- Total events: {pack['coverage']['total_events']}",
        f"- By impact: {pack['coverage']['by_impact']}",
        f"- Event dates in mart: {pack['coverage']['event_date_min']} → {pack['coverage']['event_date_max']}",
        "",
        f"## Focus split — primary {pack['focus']['primary']} vs secondary {pack['focus']['secondary']}",
        f"- Primary red (USD/EUR/GBP/JPY): {pack['focus']['primary_red']}",
        f"- Secondary red (AUD/NZD/CAD/CHF/CNY): {pack['focus']['secondary_red']}",
        "",
        "## Currency exposure — PRIMARY (USD EUR GBP JPY)",
        "| Currency | Red | Orange | Yellow | Red share % |",
        "|---|---:|---:|---:|---:|",
    ]
    for row in pack["currency_exposure_primary"]:
        lines.append(
            f"| {row['currency']} | {row['red']} | {row['orange']} | {row['yellow']} | {row['red_share_pct']} |"
        )
    lines += [
        "",
        "## Currency exposure — SECONDARY (AUD NZD CAD CHF CNY)",
        "| Currency | Red | Orange | Yellow | Red share % |",
        "|---|---:|---:|---:|---:|",
    ]
    for row in pack["currency_exposure_secondary"]:
        lines.append(
            f"| {row['currency']} | {row['red']} | {row['orange']} | {row['yellow']} | {row['red_share_pct']} |"
        )

    lines += ["", "## Session exposure (red + orange only, HCM clock)",
              "| Session | Red | Orange | Event count |",
              "|---|---:|---:|---:|"]
    for name, stats in pack["session_exposure"].items():
        lines.append(f"| {name} | {stats['red']} | {stats['orange']} | {stats['event_count']} |")

    lines += ["", "## Clashes (red/orange within 30 minutes)", ""]
    if not pack["clashes"]:
        lines.append("None.")
    for i, clash in enumerate(pack["clashes"], 1):
        lines.append(
            f"### Clash {i} — {clash['weekday']} {clash['datetime_hcm']} "
            f"({clash['pair_hint']}, {clash['event_count']} events)"
        )
        for ev in clash["events"]:
            lines.append(
                f"- [{ev['impact']}] {ev['clock_hcm']} {ev['currency']} {ev['event']} "
                f"(F {ev['forecast'] or '—'} / P {ev['previous'] or '—'} / A {ev['actual'] or '—'}; fact_id={ev['fact_id']})"
            )
        lines.append("")

    lines += ["", "## Red events",
              "| Date | Weekday | HCM | CCY | Event | Forecast | Previous | Actual | fact_id |",
              "|---|---|---|---|---|---|---|---|---:|"]
    for ev in pack["red_events"]:
        lines.append(
            f"| {ev['event_date']} | {ev['weekday']} | {ev['clock_hcm'] or '—'} | {ev['currency']} "
            f"| {ev['event']} | {ev['forecast'] or '—'} | {ev['previous'] or '—'} | {ev['actual'] or '—'} | {ev['fact_id']} |"
        )

    lines += ["", "## Expectation shifts (red, forecast ≠ previous)", ""]
    if not pack["expectation_shifts"]:
        lines.append("None.")
    for ev in pack["expectation_shifts"]:
        lines.append(
            f"- {ev['event_date']} {ev['clock_hcm']} {ev['currency']} {ev['event']}: "
            f"forecast {ev['forecast']} vs previous {ev['previous']} (fact_id={ev['fact_id']})"
        )

    nxt = pack.get("next_week") or {}
    lines += ["", f"## Next week look-ahead ({nxt.get('week_label', 'n/a')})", ""]
    if not nxt.get("available"):
        lines.append("Next week is not in the mart. Do not invent a look-ahead.")
    else:
        lines.append(
            f"Available. Dates {nxt['week_start']} → {nxt['week_end']}. "
            f"Total {nxt['coverage']['total_events']}. Impact {nxt['coverage']['by_impact']}. "
            f"Primary red {nxt['focus']['primary_red']} / secondary red {nxt['focus']['secondary_red']}."
        )
        lines += [
            "",
            "### Next week primary exposure",
            "| Currency | Red | Orange | Yellow | Red share % |",
            "|---|---:|---:|---:|---:|",
        ]
        for row in nxt["currency_exposure_primary"]:
            lines.append(
                f"| {row['currency']} | {row['red']} | {row['orange']} | {row['yellow']} | {row['red_share_pct']} |"
            )
        lines += [
            "",
            "### Next week secondary exposure",
            "| Currency | Red | Orange | Yellow | Red share % |",
            "|---|---:|---:|---:|---:|",
        ]
        for row in nxt["currency_exposure_secondary"]:
            lines.append(
                f"| {row['currency']} | {row['red']} | {row['orange']} | {row['yellow']} | {row['red_share_pct']} |"
            )
        lines += ["", "### Next week red events",
                  "| Date | Weekday | HCM | CCY | Focus | Event | Forecast | Previous | Actual | fact_id |",
                  "|---|---|---|---|---|---|---|---|---|---:|"]
        for ev in nxt["red_events"]:
            lines.append(
                f"| {ev['event_date']} | {ev['weekday']} | {ev['clock_hcm'] or '—'} | {ev['currency']} "
                f"| {ev['focus']} | {ev['event']} | {ev['forecast'] or '—'} | {ev['previous'] or '—'} "
                f"| {ev['actual'] or '—'} | {ev['fact_id']} |"
            )
        lines += ["", "### Next week clashes", ""]
        if not nxt["clashes"]:
            lines.append("None.")
        for i, clash in enumerate(nxt["clashes"], 1):
            lines.append(
                f"- Clash {i}: {clash['weekday']} {clash['datetime_hcm']} "
                f"({clash['pair_hint']}, {clash['event_count']} events)"
            )
            for ev in clash["events"]:
                lines.append(
                    f"  - [{ev['impact']}/{ev['focus']}] {ev['clock_hcm']} {ev['currency']} {ev['event']} "
                    f"(F {ev['forecast'] or '—'} / P {ev['previous'] or '—'}; fact_id={ev['fact_id']})"
                )
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a weekly analyst fact pack from gold/mart.")
    parser.add_argument("--year", type=int, required=True)
    parser.add_argument("--week", type=int, required=True, help="ISO week number")
    parser.add_argument("--mart-dir", type=Path, default=GOLD_MART_DIR)
    parser.add_argument("--json-out", type=Path)
    parser.add_argument("--md-out", type=Path)
    args = parser.parse_args()

    pack = build_fact_pack(args.year, args.week, args.mart_dir)
    md = fact_pack_to_markdown(pack)
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(json.dumps(pack, indent=2, ensure_ascii=False) + "\n")
    if args.md_out:
        args.md_out.parent.mkdir(parents=True, exist_ok=True)
        args.md_out.write_text(md)
    if not args.json_out and not args.md_out:
        print(md)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
