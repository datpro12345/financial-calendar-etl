"""Parse Forex Factory calendar tables exported as markdown (print/WebFetch view)."""

from __future__ import annotations

import re
from typing import Iterable

from scripts.extract.config import ALLOWED_CURRENCIES, BRONZE_COLUMNS

DAY_HEADER = re.compile(
    r"^(Mon|Tue|Wed|Thu|Fri|Sat|Sun)\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+(\d{1,2})$",
    re.IGNORECASE,
)
TIME_LIKE = re.compile(
    r"^(\d{1,2}:\d{2}(am|pm)|All Day|Tentative|Day\s+\d+|\d{1,2}(st|nd|rd|th)-\d{1,2}(st|nd|rd|th)|\d{1,2}(st|nd|rd|th)-\d{1,2}(st|nd|rd|th)?)$",
    re.IGNORECASE,
)


def _cell(value: str | None) -> str:
    text = (value or "").strip()
    return text if text else "N/A"


def _split_row(line: str) -> list[str]:
    # Markdown table row: | a | b | c |
    parts = [p.strip() for p in line.strip().strip("|").split("|")]
    return parts


def parse_calendar_markdown(markdown: str, default_impact: str = "yellow") -> list[dict[str, str]]:
    """Parse FF calendar markdown table into bronze rows.

    Impact icons are lost in markdown conversion. Callers should pass
    default_impact='red' when the source URL filtered impacts=3 (high).
    """
    rows: list[dict[str, str]] = []
    current_date = ""
    current_time = ""

    for raw_line in markdown.splitlines():
        line = raw_line.strip()
        if not line.startswith("|"):
            continue
        if set(line.replace("|", "").replace("-", "").replace(" ", "")) == "":
            continue  # separator row

        cells = _split_row(line)
        if not cells:
            continue

        # Skip header-ish rows
        joined = " ".join(cells).lower()
        if "currency" in joined and "impact" in joined:
            continue
        if cells[0].lower() in {"date"} or "actual" == cells[0].lower():
            continue

        # Day breaker: "Tue Sep 1"
        first = cells[0]
        day_match = DAY_HEADER.match(first)
        if day_match:
            month = day_match.group(2).title()
            day = day_match.group(3)
            current_date = f"{month} {day}"
            # Same row may also contain first event after day label
            # Layout variants:
            # | Tue Sep 1 | | | | ... |  OR
            # | Tue Sep 1 | 12:15am | EUR | | Event | ... |
            if len(cells) >= 5 and cells[2].upper() in ALLOWED_CURRENCIES | {"ALL"}:
                pass  # fall through to event parse below with offset
            else:
                continue

        # Normalize columns. Observed layouts:
        # [date_or_empty, time, currency, impact, event, alerts?, detail?, actual, forecast, previous, graph?]
        # When date empty: [ '', time, currency, '', event, '', '', actual, forecast, previous, '']
        # When day+event:  [ 'Tue Sep 1', time, currency, '', event, '', '', actual, forecast, previous, '']

        # Find currency column index
        currency_idx = None
        for idx, cell in enumerate(cells):
            if cell.upper() in ALLOWED_CURRENCIES:
                currency_idx = idx
                break
        if currency_idx is None:
            continue

        currency = cells[currency_idx].upper()
        time_value = cells[currency_idx - 1] if currency_idx >= 1 else ""
        if time_value and TIME_LIKE.match(time_value):
            current_time = time_value
        elif not time_value:
            time_value = current_time
        else:
            # Unusual time token — keep as-is if non-empty, else carry forward
            time_value = time_value or current_time
            if time_value:
                current_time = time_value

        # Event is usually right after empty impact column
        event = ""
        for idx in range(currency_idx + 1, len(cells)):
            candidate = cells[idx].strip()
            if candidate and candidate.lower() not in {"actual", "forecast", "previous"}:
                event = candidate
                # Remaining numeric-ish columns after event+optional blanks
                rest = cells[idx + 1 :]
                break
        else:
            continue

        if not event or not current_date:
            continue

        # After event: optional empty alerts/detail then actual, forecast, previous
        # Strip leading empties then take up to 3 values
        nonempty_tail = []
        for item in rest:
            nonempty_tail.append(item.strip())
        # Prefer last 3 meaningful slots from the known positions:
        # Many rows: event, '', '', actual, forecast, previous, ''
        if len(rest) >= 5:
            actual, forecast, previous = rest[2], rest[3], rest[4]
        elif len(rest) >= 3:
            actual, forecast, previous = rest[0], rest[1], rest[2]
        else:
            actual = forecast = previous = ""

        rows.append(
            {
                "date": current_date,
                "time": time_value or current_time or "N/A",
                "currency": currency,
                "impact": default_impact,
                "event": event,
                "actual": _cell(actual),
                "forecast": _cell(forecast),
                "previous": _cell(previous),
            }
        )

    return rows


def merge_impact_layers(
    yellow_rows: Iterable[dict[str, str]] | None = None,
    orange_rows: Iterable[dict[str, str]] | None = None,
    red_rows: Iterable[dict[str, str]] | None = None,
    gray_rows: Iterable[dict[str, str]] | None = None,
) -> list[dict[str, str]]:
    """Merge impact-filtered extracts. Higher impact wins on duplicate keys."""
    merged: dict[tuple[str, str, str, str], dict[str, str]] = {}
    priority = {"gray": 0, "yellow": 1, "orange": 2, "red": 3}

    for impact, layer in (
        ("gray", gray_rows or []),
        ("yellow", yellow_rows or []),
        ("orange", orange_rows or []),
        ("red", red_rows or []),
    ):
        for row in layer:
            key = (row["date"], row["time"], row["currency"], row["event"])
            row = {**row, "impact": impact}
            existing = merged.get(key)
            if existing is None or priority[impact] >= priority[existing["impact"]]:
                merged[key] = row

    # Stable-ish order by date then time then currency
    return sorted(merged.values(), key=lambda r: (r["date"], r["time"], r["currency"], r["event"]))


def rows_to_dataframe(rows: Iterable[dict[str, str]]):
    import pandas as pd

    return pd.DataFrame(list(rows), columns=BRONZE_COLUMNS)
