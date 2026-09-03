"""Parse Forex Factory calendar HTML into bronze-layer rows."""

from __future__ import annotations

import re
from typing import Iterable

from bs4 import BeautifulSoup, Tag

from scripts.extract.config import ALLOWED_CURRENCIES, BRONZE_COLUMNS, IMPACT_CLASS_MAP

DAY_OR_MONTH_PATTERN = re.compile(
    r"\b(Mon|Tue|Wed|Thu|Fri|Sat|Sun|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\b",
    re.IGNORECASE,
)


def _normalize_cell_text(value: str | None) -> str:
    if value is None:
        return "N/A"
    cleaned = value.strip()
    return cleaned if cleaned else "N/A"


def _parse_impact(cell: Tag) -> str | None:
    for span in cell.find_all("span"):
        impact_class = span.get("class")
        if not impact_class:
            continue
        class_name = " ".join(impact_class)
        if class_name in IMPACT_CLASS_MAP:
            return IMPACT_CLASS_MAP[class_name]
        title = span.get("title", "").strip().lower()
        if title in {"low", "medium", "high", "holiday", "non-economic"}:
            mapping = {
                "low": "yellow",
                "medium": "orange",
                "high": "red",
                "holiday": "gray",
                "non-economic": "gray",
            }
            return mapping.get(title)
    return None


def _parse_currency(cell: Tag) -> str | None:
    span = cell.find("span")
    if span and span.get("title"):
        return span["title"].strip().upper()
    text = cell.get_text(strip=True).upper()
    return text if text in ALLOWED_CURRENCIES else None


def _strip_day_prefix(date_text: str) -> str:
    match = DAY_OR_MONTH_PATTERN.search(date_text)
    if not match:
        return date_text.strip()
    return date_text.replace(match.group(0), "").strip()


def _cell_class_name(cell: Tag) -> str:
    classes = cell.get("class") or []
    return " ".join(classes)


def parse_calendar_html(html: str) -> list[dict[str, str]]:
    """Return bronze-schema rows from a Forex Factory calendar page."""
    soup = BeautifulSoup(html, "lxml")
    table = soup.find("table", class_="calendar__table")
    if table is None:
        raise ValueError("Could not find calendar table in HTML.")

    rows: list[dict[str, str]] = []
    current_date = ""
    current_time = ""

    for row in table.find_all("tr", class_=lambda value: value and "calendar__row" in value):
        cells = row.find_all("td")
        if not cells:
            continue

        class_names = [_cell_class_name(cell) for cell in cells]

        if any("calendar__date" in name for name in class_names):
            date_cell = next(cell for cell in cells if "calendar__date" in _cell_class_name(cell))
            current_date = _strip_day_prefix(date_cell.get_text("\n", strip=True))
            continue

        event = None
        currency = None
        impact = None
        actual = "N/A"
        forecast = "N/A"
        previous = "N/A"
        time_value = current_time

        for cell, class_name in zip(cells, class_names):
            if "calendar__time" in class_name:
                time_value = cell.get_text(strip=True) or current_time
                current_time = time_value
            elif "calendar__currency" in class_name:
                currency = _parse_currency(cell)
            elif "calendar__impact" in class_name:
                impact = _parse_impact(cell)
            elif "calendar__event" in class_name:
                event = cell.get_text(strip=True)
            elif "calendar__actual" in class_name:
                actual = _normalize_cell_text(cell.get_text(strip=True))
            elif "calendar__forecast" in class_name:
                forecast = _normalize_cell_text(cell.get_text(strip=True))
            elif "calendar__previous" in class_name:
                previous = _normalize_cell_text(cell.get_text(strip=True))

        if not currency or currency not in ALLOWED_CURRENCIES:
            continue
        if not impact or not event:
            continue

        rows.append(
            {
                "date": current_date,
                "time": _normalize_cell_text(time_value),
                "currency": currency,
                "impact": impact,
                "event": event,
                "actual": actual,
                "forecast": forecast,
                "previous": previous,
            }
        )

    return rows


def rows_to_dataframe(rows: Iterable[dict[str, str]]):
    import pandas as pd

    frame = pd.DataFrame(list(rows), columns=BRONZE_COLUMNS)
    return frame
