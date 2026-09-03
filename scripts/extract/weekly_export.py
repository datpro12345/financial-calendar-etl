"""Parse Faireconomy / Forex Factory weekly calendar exports (CSV / XML / JSON).

Official-ish feed (this week only, rate-limited ~2 req / 5 min):
  https://nfs.faireconomy.media/ff_calendar_thisweek.{csv,xml,json}
"""

from __future__ import annotations

import csv
import io
import json
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import Any

from scripts.extract.config import BRONZE_COLUMNS

IMPACT_EXPORT_MAP = {
    "high": "red",
    "medium": "orange",
    "low": "yellow",
    "holiday": "gray",
}


def _cell(value: Any) -> str:
    text = "" if value is None else str(value).strip()
    return text if text else "N/A"


def _map_impact(raw: str) -> str:
    return IMPACT_EXPORT_MAP.get(raw.strip().lower(), raw.strip().lower() or "N/A")


def _date_to_bronze(date_raw: str) -> str:
    """Convert MM-DD-YYYY (export) → 'Sep 4' bronze style."""
    text = date_raw.strip()
    for fmt in ("%m-%d-%Y", "%Y-%m-%d"):
        try:
            dt = datetime.strptime(text[:10], fmt)
            return f"{dt.strftime('%b')} {dt.day}"
        except ValueError:
            continue
    # ISO datetime e.g. 2026-08-30T11:15:00-04:00
    try:
        dt = datetime.fromisoformat(text.replace("Z", "+00:00"))
        return f"{dt.strftime('%b')} {dt.day}"
    except ValueError:
        return text or "N/A"


def _time_to_bronze(time_raw: str, date_raw: str = "") -> str:
    text = (time_raw or "").strip()
    if text:
        return text
    # JSON often embeds time in ISO date
    if "T" in date_raw:
        try:
            dt = datetime.fromisoformat(date_raw.replace("Z", "+00:00"))
            hour = dt.strftime("%I").lstrip("0") or "12"
            return f"{hour}:{dt.strftime('%M%p').lower()}"
        except ValueError:
            pass
    return "N/A"


def _row(
    *,
    date: str,
    time: str,
    currency: str,
    impact: str,
    event: str,
    actual: str = "N/A",
    forecast: str = "N/A",
    previous: str = "N/A",
) -> dict[str, str]:
    return {
        "date": date,
        "time": time,
        "currency": currency.upper() if currency else "N/A",
        "impact": impact,
        "event": event,
        "actual": actual,
        "forecast": forecast,
        "previous": previous,
    }


def parse_weekly_csv(text: str) -> list[dict[str, str]]:
    reader = csv.DictReader(io.StringIO(text))
    rows: list[dict[str, str]] = []
    for item in reader:
        # Title,Country,Date,Time,Impact,Forecast,Previous,URL
        country = _cell(item.get("Country"))
        if country.upper() == "ALL":
            country = "ALL"
        rows.append(
            _row(
                date=_date_to_bronze(_cell(item.get("Date"))),
                time=_cell(item.get("Time")),
                currency=country,
                impact=_map_impact(_cell(item.get("Impact"))),
                event=_cell(item.get("Title")),
                forecast=_cell(item.get("Forecast")),
                previous=_cell(item.get("Previous")),
            )
        )
    return rows


def parse_weekly_xml(text: str) -> list[dict[str, str]]:
    root = ET.fromstring(text)
    rows: list[dict[str, str]] = []
    for event in root.findall("event"):
        def _text(tag: str) -> str:
            node = event.find(tag)
            if node is None or node.text is None:
                return "N/A"
            return node.text.strip() or "N/A"

        country = _text("country")
        rows.append(
            _row(
                date=_date_to_bronze(_text("date")),
                time=_text("time"),
                currency=country,
                impact=_map_impact(_text("impact")),
                event=_text("title"),
                forecast=_text("forecast"),
                previous=_text("previous"),
            )
        )
    return rows


def parse_weekly_json(text: str) -> list[dict[str, str]]:
    payload = json.loads(text)
    if not isinstance(payload, list):
        raise ValueError("Weekly JSON export must be a list of events")
    rows: list[dict[str, str]] = []
    for item in payload:
        date_raw = _cell(item.get("date"))
        rows.append(
            _row(
                date=_date_to_bronze(date_raw),
                time=_time_to_bronze(_cell(item.get("time")) if "time" in item else "", date_raw),
                currency=_cell(item.get("country")),
                impact=_map_impact(_cell(item.get("impact"))),
                event=_cell(item.get("title")),
                forecast=_cell(item.get("forecast")),
                previous=_cell(item.get("previous")),
            )
        )
    return rows


def parse_weekly_export(text: str, fmt: str) -> list[dict[str, str]]:
    fmt = fmt.lower().lstrip(".")
    if fmt == "csv":
        return parse_weekly_csv(text)
    if fmt == "xml":
        return parse_weekly_xml(text)
    if fmt == "json":
        return parse_weekly_json(text)
    raise ValueError(f"Unsupported weekly format: {fmt}")


def assert_bronze_schema(rows: list[dict[str, str]]) -> None:
    for row in rows:
        missing = set(BRONZE_COLUMNS) - set(row)
        if missing:
            raise ValueError(f"Row missing columns: {sorted(missing)}")
