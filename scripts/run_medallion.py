#!/usr/bin/env python3
"""Run bronze raw dumps → landing → silver → gold GCal → Kimball mart.

Does not fetch the network. Reuses files under data/bronze/raw/calendar/.
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.extract.build_month_from_markdown import MONTH_MAP, build_month
from scripts.extract.config import BRONZE_RAW_CALENDAR_DIR
from scripts.transform.to_kimball import silver_to_kimball

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

NUM_TO_ABBR = {num: abbr for abbr, num in MONTH_MAP.items()}
LAYER_FILES = ("red", "orange", "yellow", "gray", "all")


def _find_layer(raw_dir: Path, month_num: str, layer: str) -> Path | None:
    for ext in (".html", ".md"):
        path = raw_dir / f"{month_num}_{layer}{ext}"
        if path.exists():
            return path
    return None


def discover_months(year: int) -> list[str]:
    raw_dir = BRONZE_RAW_CALENDAR_DIR / str(year)
    found: list[str] = []
    for month_num, abbr in sorted(NUM_TO_ABBR.items()):
        if any(_find_layer(raw_dir, month_num, layer) for layer in LAYER_FILES):
            found.append(abbr)
    return found


def run_year(
    year: int,
    *,
    write_gold_gcal: bool = True,
    prune_missing: bool = False,
    months: list[str] | None = None,
) -> dict:
    raw_dir = BRONZE_RAW_CALENDAR_DIR / str(year)
    months = months or discover_months(year)
    if not months:
        raise FileNotFoundError(f"No bronze raw dumps in {raw_dir}")

    results = []
    for abbr in months:
        month_num = MONTH_MAP[abbr]
        logger.info("=== bronze→gold %s.%s ===", abbr, year)
        built = build_month(
            year=year,
            month_abbr=abbr,
            all_md=_find_layer(raw_dir, month_num, "all"),
            red_md=_find_layer(raw_dir, month_num, "red"),
            orange_md=_find_layer(raw_dir, month_num, "orange"),
            yellow_md=_find_layer(raw_dir, month_num, "yellow"),
            gray_md=_find_layer(raw_dir, month_num, "gray"),
            write_gold_gcal=write_gold_gcal,
            prune_missing=prune_missing,
        )
        results.append(
            {
                "month": abbr,
                "rows": built.get("rows"),
                "coverage": built.get("coverage"),
                "impact_counts": built.get("impact_counts"),
                "landing": built.get("bronze_landing"),
                "silver": built.get("silver"),
                "silver_upsert": built.get("silver_upsert"),
                "gold_gcal": built.get("gold_google_calendar"),
            }
        )

    mart = silver_to_kimball()
    return {
        "year": year,
        "months": results,
        "mart": {name: str(path) for name, path in mart.items()},
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Rebuild Medallion gold from bronze raw")
    parser.add_argument("--year", type=int, default=2026)
    parser.add_argument("--no-gcal", action="store_true")
    parser.add_argument(
        "--months",
        nargs="+",
        help="Month abbrs to rebuild, e.g. --months sep. Default: every month with a raw dump",
    )
    parser.add_argument(
        "--prune",
        action="store_true",
        help="Delete silver rows the dumps no longer list (only for layers they carried)",
    )
    args = parser.parse_args()
    summary = run_year(
        args.year,
        write_gold_gcal=not args.no_gcal,
        prune_missing=args.prune,
        months=args.months,
    )
    print(json.dumps(summary, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
