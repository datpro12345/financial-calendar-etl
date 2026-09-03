#!/usr/bin/env python3
"""Extract Forex Factory calendar data into bronze CSV files."""

from __future__ import annotations

import argparse
import logging
import sys
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.extract.client import build_calendar_url, fetch_calendar_html
from scripts.extract.config import BRONZE_COLUMNS, BRONZE_MONTHLY_DIR, BRONZE_WEEKLY_DIR
from scripts.extract.parser import parse_calendar_html, rows_to_dataframe

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


def resolve_output_path(period: str, output: str | None, cadence: str) -> Path:
    if output:
        return Path(output)

    now = datetime.now()
    if cadence == "weekly":
        year, week, _ = now.isocalendar()
        BRONZE_WEEKLY_DIR.mkdir(parents=True, exist_ok=True)
        return BRONZE_WEEKLY_DIR / f"{year}_W{week:02d}_ff_data.csv"

    if period in {"this", "next"}:
        month_label = now.strftime("%Y_%m")
    elif "." in period:
        # e.g. mar.2026
        month_part, year_part = period.split(".", 1)
        month_map = {
            "jan": "01",
            "feb": "02",
            "mar": "03",
            "apr": "04",
            "may": "05",
            "jun": "06",
            "jul": "07",
            "aug": "08",
            "sep": "09",
            "oct": "10",
            "nov": "11",
            "dec": "12",
        }
        month_label = f"{year_part}_{month_map.get(month_part.lower(), '01')}"
    else:
        month_label = now.strftime("%Y_%m")

    BRONZE_MONTHLY_DIR.mkdir(parents=True, exist_ok=True)
    return BRONZE_MONTHLY_DIR / f"{month_label}_ff_data.csv"


def extract_bronze(
    period: str = "this",
    output: str | None = None,
    cadence: str = "monthly",
    strategy: str = "auto",
    from_markdown: str | None = None,
    markdown_impact: str = "yellow",
) -> Path:
    if from_markdown:
        from scripts.extract.markdown_parser import parse_calendar_markdown

        md_path = Path(from_markdown)
        logger.info("Parsing local markdown %s (impact=%s)", md_path, markdown_impact)
        rows = parse_calendar_markdown(md_path.read_text(), default_impact=markdown_impact)
        method = "markdown"
    else:
        url = build_calendar_url(period)
        logger.info("Fetching calendar from %s", url)
        html, method = fetch_calendar_html(url, strategy=strategy)  # type: ignore[arg-type]
        logger.info("Fetched HTML via %s (%s bytes)", method, len(html))
        rows = parse_calendar_html(html)

    if not rows:
        raise RuntimeError("No calendar rows parsed from source.")

    frame = rows_to_dataframe(rows)
    output_path = resolve_output_path(period, output, cadence)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(output_path, index=False, na_rep="N/A")

    logger.info("Saved %s bronze rows to %s via %s", len(frame), output_path, method)
    return output_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Extract Forex Factory data to bronze CSV.")
    parser.add_argument(
        "--period",
        default="this",
        help="Calendar period: this, next, mar.2026, or YYYY-MM-DD",
    )
    parser.add_argument("--output", help="Optional output CSV path")
    parser.add_argument(
        "--cadence",
        choices=("monthly", "weekly"),
        default="monthly",
        help="Output folder cadence (weekly for recurring forecast/actual snapshots).",
    )
    parser.add_argument(
        "--strategy",
        choices=("http", "browser"),
        default="http",
        help="http=curl_cffi, browser=Playwright fallback",
    )
    parser.add_argument(
        "--from-markdown",
        help="Parse a local markdown calendar dump instead of live fetch",
    )
    parser.add_argument(
        "--markdown-impact",
        default="yellow",
        choices=("yellow", "orange", "red", "gray"),
        help="Impact label when parsing markdown (icons are lost in markdown)",
    )
    args = parser.parse_args()

    try:
        output_path = extract_bronze(
            period=args.period,
            output=args.output,
            cadence=args.cadence,
            strategy=args.strategy,
            from_markdown=args.from_markdown,
            markdown_impact=args.markdown_impact,
        )
    except Exception as exc:  # noqa: BLE001
        logger.error("Bronze extract failed: %s", exc)
        return 1

    print(f"OK {output_path} columns={','.join(BRONZE_COLUMNS)} rows={sum(1 for _ in open(output_path)) - 1}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
