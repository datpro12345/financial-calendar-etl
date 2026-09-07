#!/usr/bin/env python3
"""A2 — re-scrape the current month's HTML so printed `actual` values reach silver.

The this-week export (step A) carries no ``Actual`` column, so the monthly HTML
dump is the only source of printed values. Each month costs four Cloudflare-paced
requests because all four impact layers are fetched, including gray/holiday
(``impacts=0``) — dropping gray is what silently left the mart with no holidays.

Results are upserted with ``mode="refresh"``, which coalesces: an empty incoming
value never overwrites a stored one, and nothing is pruned unless asked.
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from datetime import date, timedelta
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.extract.build_month_from_markdown import MONTH_MAP, build_month
from scripts.extract.client import fetch_month_impact_layers
from scripts.extract.config import (
    BRONZE_RAW_CALENDAR_DIR,
    IMPACT_FETCH_GAP_SECONDS,
    IMPACT_LAYERS,
)

logger = logging.getLogger(__name__)

NUM_TO_ABBR = {num: abbr for abbr, num in MONTH_MAP.items()}
LAYER_KEYS = tuple(label for label, _ in IMPACT_LAYERS)

# Days into a new month during which the previous month is still worth a refresh.
EDGE_DAYS = 5


def months_to_backfill(
    reference: date | None = None,
    *,
    edge_days: int = EDGE_DAYS,
) -> list[tuple[int, str]]:
    """Current month, plus the previous one early in a new month.

    A release printed on the 31st only gets an actual on a later run, which by
    then may already sit in the next month.
    """
    today = reference or date.today()
    months: list[tuple[int, str]] = []
    if today.day <= edge_days:
        previous = today.replace(day=1) - timedelta(days=1)
        months.append((previous.year, NUM_TO_ABBR[f"{previous.month:02d}"]))
    months.append((today.year, NUM_TO_ABBR[f"{today.month:02d}"]))
    return months


def existing_layers(year: int, month_abbr: str) -> dict[str, Path]:
    """Raw dumps already on disk, so a partial fetch still rebuilds a full month."""
    raw_dir = BRONZE_RAW_CALENDAR_DIR / str(year)
    month_num = MONTH_MAP[month_abbr.lower()]
    found: dict[str, Path] = {}
    for label in (*LAYER_KEYS, "all"):
        for suffix in (".html", ".md"):
            candidate = raw_dir / f"{month_num}_{label}{suffix}"
            if candidate.exists():
                found[label] = candidate
                break
    return found


def backfill_actuals(
    *,
    reference: date | None = None,
    months: list[tuple[int, str]] | None = None,
    fetch: bool = True,
    gap_seconds: int = IMPACT_FETCH_GAP_SECONDS,
    strategy: str = "http",
    write_gold_gcal: bool = True,
    prune_missing: bool = False,
) -> dict:
    targets = months or months_to_backfill(reference)
    results: list[dict] = []

    for year, abbr in targets:
        logger.info("A2 — actual backfill %s.%s (all %s impact layers)", abbr, year, len(IMPACT_LAYERS))
        layers = existing_layers(year, abbr)
        if fetch:
            saved = fetch_month_impact_layers(
                abbr,
                year,
                gap_seconds=gap_seconds,
                strategy=strategy,
                stop_on_fail=False,
            )
            layers.update(saved)
            missing = [label for label in LAYER_KEYS if label not in saved]
            if missing:
                logger.warning("Incomplete fetch for %s.%s — missing %s", abbr, year, missing)

        if not layers:
            logger.warning("No raw dumps for %s.%s — skipping", abbr, year)
            results.append({"year": year, "month": abbr, "skipped": "no raw dumps"})
            continue

        built = build_month(
            year=year,
            month_abbr=abbr,
            all_md=layers.get("all"),
            red_md=layers.get("red"),
            orange_md=layers.get("orange"),
            yellow_md=layers.get("yellow"),
            gray_md=layers.get("gray"),
            write_gold_gcal=write_gold_gcal,
            prune_missing=prune_missing,
        )
        results.append(
            {
                "year": year,
                "month": abbr,
                "coverage": built.get("coverage"),
                "rows": built.get("rows"),
                "impact_counts": built.get("impact_counts"),
                "silver": built.get("silver"),
                "silver_upsert": built.get("silver_upsert"),
            }
        )

    return {"ok": True, "months": results}


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    parser = argparse.ArgumentParser(description="Backfill printed actuals from monthly HTML")
    parser.add_argument("--year", type=int, help="Only with --months")
    parser.add_argument("--months", nargs="+", help="Month abbrs, e.g. aug sep")
    parser.add_argument("--gap", type=int, default=IMPACT_FETCH_GAP_SECONDS)
    parser.add_argument(
        "--strategy",
        choices=("auto", "http", "browser", "stealth"),
        default="http",
    )
    parser.add_argument("--skip-fetch", action="store_true", help="Rebuild from raw dumps on disk")
    parser.add_argument("--no-gcal", action="store_true")
    parser.add_argument(
        "--prune",
        action="store_true",
        help="Delete silver rows the dumps no longer list (only for layers they carried)",
    )
    args = parser.parse_args()

    months = None
    if args.months:
        if args.year is None:
            parser.error("--months requires --year")
        months = [(args.year, abbr) for abbr in args.months]

    summary = backfill_actuals(
        months=months,
        fetch=not args.skip_fetch,
        gap_seconds=args.gap,
        strategy=args.strategy,
        write_gold_gcal=not args.no_gcal,
        prune_missing=args.prune,
    )
    print(json.dumps(summary, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
