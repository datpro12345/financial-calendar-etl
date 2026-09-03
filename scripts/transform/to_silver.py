"""Build Silver calendar_events (SSOT) from Bronze landing."""

from __future__ import annotations

import argparse
import json
import logging
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.extract.config import (
    BRONZE_LANDING_DIR,
    SILVER_COLUMNS,
    SILVER_EVENTS_DIR,
)
from scripts.transform.timeutils import to_hcm

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

HCM_TZ = ZoneInfo("Asia/Ho_Chi_Minh")
NULL_TOKENS = {"", "n/a", "na", "null", "none", "nan"}


def _clean_value(value: object) -> str:
    text = "" if value is None or (isinstance(value, float) and pd.isna(value)) else str(value).strip()
    if text.lower() in NULL_TOKENS:
        return ""
    return text


def _parse_event_date(date_str: str, year: int) -> datetime | None:
    text = _clean_value(date_str)
    for fmt in ("%b %d %Y", "%B %d %Y"):
        try:
            return datetime.strptime(f"{text} {year}", fmt)
        except ValueError:
            continue
    return None


def _parse_clock(time_str: str) -> datetime | None:
    text = _clean_value(time_str)
    match = re.match(r"^(\d{1,2}:\d{2})(am|pm)$", text, re.IGNORECASE)
    if not match:
        return None
    return datetime.strptime(f"{match.group(1)}{match.group(2).lower()}", "%I:%M%p")


def landing_to_silver(
    landing_path: Path | str,
    *,
    year: int,
    source_timezone: str,
    output: Path | str | None = None,
) -> Path:
    landing_path = Path(landing_path)
    df = pd.read_csv(landing_path, dtype=str)
    updated_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    records: list[dict[str, str]] = []
    for _, row in df.iterrows():
        event_date = _parse_event_date(row.get("date", ""), year)
        if event_date is None:
            continue

        time_raw = _clean_value(row.get("time", ""))
        clock = _parse_clock(time_raw)
        dt_utc = ""
        dt_hcm = ""
        if clock is not None:
            start_hcm, _ = to_hcm(event_date, clock, source_timezone)
            dt_hcm = start_hcm.isoformat()
            dt_utc = start_hcm.astimezone(timezone.utc).isoformat()

        records.append(
            {
                "event_date": event_date.strftime("%Y-%m-%d"),
                "time_raw": time_raw,
                "event_datetime_utc": dt_utc,
                "event_datetime_hcm": dt_hcm,
                "currency": _clean_value(row.get("currency", "")).upper(),
                "impact": _clean_value(row.get("impact", "")).lower(),
                "event": _clean_value(row.get("event", "")),
                "actual": _clean_value(row.get("actual", "")),
                "forecast": _clean_value(row.get("forecast", "")),
                "previous": _clean_value(row.get("previous", "")),
                "source_timezone": source_timezone,
                "updated_at": updated_at,
            }
        )

    out = pd.DataFrame(records, columns=SILVER_COLUMNS)
    # Dedupe: keep last occurrence
    out = out.drop_duplicates(
        subset=["event_date", "time_raw", "currency", "event"],
        keep="last",
    ).sort_values(["event_date", "time_raw", "currency", "event"])

    if output:
        output_path = Path(output)
    else:
        SILVER_EVENTS_DIR.mkdir(parents=True, exist_ok=True)
        output_path = SILVER_EVENTS_DIR / landing_path.name

    output_path.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(output_path, index=False)
    logger.info("Silver SSOT saved %s rows → %s", len(out), output_path)
    return output_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Bronze landing → Silver calendar_events")
    parser.add_argument("--input", required=True, help="Bronze landing CSV")
    parser.add_argument("--year", type=int, required=True)
    parser.add_argument("--source-tz", required=True, help="IANA timezone of bronze times")
    parser.add_argument("--output", help="Optional silver CSV path")
    args = parser.parse_args()

    try:
        path = landing_to_silver(
            args.input,
            year=args.year,
            source_timezone=args.source_tz,
            output=args.output,
        )
    except Exception as exc:  # noqa: BLE001
        logger.error("Silver build failed: %s", exc)
        return 1
    print(f"OK {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
