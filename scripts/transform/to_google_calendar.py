"""Gold export: Silver calendar_events → Google Calendar CSV (HCM)."""

from __future__ import annotations

import argparse
import json
import logging
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.extract.config import GOLD_GCAL_DIR, SILVER_EVENTS_DIR

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

TARGET_CURRENCIES = ("USD", "GBP", "EUR")
DEFAULT_SOURCE_TZ = "America/New_York"
GOOGLE_CALENDAR_COLUMNS = [
    "Subject",
    "Start Date",
    "Start Time",
    "End Date",
    "End Time",
    "Description",
    "Location",
]

TZ_ALIASES = {
    "America/Los Angeles": "America/Los_Angeles",
    "America/New York": "America/New_York",
    "America/Chicago": "America/Chicago",
}


def parse_timezone_from_markdown(markdown: str) -> str:
    match = re.search(
        r"Calendar Time Zone:\s*([A-Za-z]+/[A-Za-z_ ]+?)(?:\s*\(|$)",
        markdown,
    )
    if match:
        raw = match.group(1).strip()
        return TZ_ALIASES.get(raw, raw.replace(" ", "_"))
    return DEFAULT_SOURCE_TZ


def parse_timezone_from_html(html: str) -> str | None:
    """Read FF page timezone (window.FF.timezone_name)."""
    match = re.search(r"timezone_name:\s*'([^']+)'", html)
    if not match:
        return None
    raw = match.group(1).strip()
    return TZ_ALIASES.get(raw, raw.replace(" ", "_"))


def silver_to_google_calendar(
    silver_path: Path | str,
    *,
    year: int | None = None,
    currencies: tuple[str, ...] = TARGET_CURRENCIES,
    impact: str = "red",
    output: Path | str | None = None,
) -> Path:
    """Build Gold Google Calendar CSV from Silver SSOT."""
    silver_path = Path(silver_path)
    df = pd.read_csv(silver_path, dtype=str).fillna("")

    filtered = df[
        (df["currency"].isin(currencies))
        & (df["impact"].str.lower() == impact.lower())
        & (df["event_datetime_hcm"].astype(str).str.len() > 0)
    ].copy()

    if filtered.empty:
        raise RuntimeError(
            f"No gold rows after filter currency={currencies} impact={impact} from {silver_path}"
        )

    records = []
    for _, row in filtered.iterrows():
        start_hcm = datetime.fromisoformat(row["event_datetime_hcm"])
        end_hcm = start_hcm + timedelta(hours=1)
        description = (
            f"Forecast: {row['forecast'] or 'N/A'} | Actual: {row['actual'] or 'N/A'} | "
            f"Previous: {row['previous'] or 'N/A'} | TZ: Asia/Ho_Chi_Minh"
        )
        records.append(
            {
                "Subject": row["event"],
                "Start Date": start_hcm.strftime("%m/%d/%Y"),
                "Start Time": start_hcm.strftime("%H:%M"),
                "End Date": end_hcm.strftime("%m/%d/%Y"),
                "End Time": end_hcm.strftime("%H:%M"),
                "Description": description,
                "Location": row["currency"],
            }
        )

    out_df = pd.DataFrame(records, columns=GOOGLE_CALENDAR_COLUMNS)
    if output:
        output_path = Path(output)
    else:
        year_month = filtered["event_date"].astype(str).str.slice(0, 7).iloc[0]
        GOLD_GCAL_DIR.mkdir(parents=True, exist_ok=True)
        output_path = GOLD_GCAL_DIR / f"{year_month}-news.csv"

    output_path.parent.mkdir(parents=True, exist_ok=True)
    out_df.to_csv(output_path, index=False)
    logger.info("Gold Google Calendar saved %s rows → %s", len(out_df), output_path)
    return output_path


# Back-compat wrappers used by older call sites / tests
def load_source_timezone(path: Path, explicit: str | None = None) -> str:
    if explicit:
        return explicit
    meta_path = Path(path).with_suffix(".meta.json")
    if meta_path.exists():
        meta = json.loads(meta_path.read_text())
        if meta.get("source_timezone"):
            return meta["source_timezone"]
    return DEFAULT_SOURCE_TZ


def bronze_to_google_calendar(
    bronze_path: Path | str,
    *,
    year: int | None = None,
    currencies: tuple[str, ...] = TARGET_CURRENCIES,
    impact: str = "red",
    upcoming_only: bool = False,
    output: Path | str | None = None,
    source_timezone: str | None = None,
) -> Path:
    """Legacy entry: bronze/landing-like CSV → gold GCal (prefer silver_to_google_calendar)."""
    from scripts.transform.to_silver import landing_to_silver

    bronze_path = Path(bronze_path)
    year = year or datetime.now().year
    source_tz = load_source_timezone(bronze_path, source_timezone)

    # If already silver schema, export directly
    cols = set(pd.read_csv(bronze_path, nrows=0).columns)
    if "event_datetime_hcm" in cols:
        return silver_to_google_calendar(bronze_path, year=year, currencies=currencies, impact=impact, output=output)

    silver = landing_to_silver(bronze_path, year=year, source_timezone=source_tz)
    return silver_to_google_calendar(silver, year=year, currencies=currencies, impact=impact, output=output)


def main() -> int:
    parser = argparse.ArgumentParser(description="Silver → Gold Google Calendar CSV (HCM)")
    parser.add_argument(
        "--input",
        default=str(SILVER_EVENTS_DIR / f"{datetime.now():%Y_%m}.csv"),
        help="Silver calendar_events CSV",
    )
    parser.add_argument("--output", help="Optional gold CSV path")
    parser.add_argument("--year", type=int, default=datetime.now().year)
    args = parser.parse_args()

    try:
        path = silver_to_google_calendar(args.input, year=args.year, output=args.output)
    except Exception as exc:  # noqa: BLE001
        logger.error("Gold Google Calendar export failed: %s", exc)
        return 1
    print(f"OK {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
