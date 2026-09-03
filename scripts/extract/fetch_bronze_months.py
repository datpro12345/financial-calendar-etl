#!/usr/bin/env python3
"""Fetch bronze impact layers for one or more months (Cloudflare-paced)."""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.extract.client import fetch_month_impact_layers
from scripts.extract.config import IMPACT_FETCH_GAP_SECONDS
from scripts.extract.build_month_from_markdown import build_month

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


def main() -> int:
    parser = argparse.ArgumentParser(description="Fetch R/O/Y bronze layers then build Medallion month")
    parser.add_argument("--year", type=int, required=True)
    parser.add_argument(
        "--months",
        nargs="+",
        required=True,
        help="Month abbrs, e.g. jan feb mar",
    )
    parser.add_argument("--gap", type=int, default=IMPACT_FETCH_GAP_SECONDS)
    parser.add_argument(
        "--strategy",
        choices=("auto", "http", "browser", "stealth"),
        default="auto",
        help="http=curl_cffi then cloudscraper (use with WARP). See docs/scrape_strategy.md",
    )
    parser.add_argument("--fetch-only", action="store_true")
    parser.add_argument("--no-gold", action="store_true")
    args = parser.parse_args()

    results = []
    for month in args.months:
        logger.info("=== Month %s.%s ===", month, args.year)
        saved = fetch_month_impact_layers(
            month,
            args.year,
            gap_seconds=args.gap,
            strategy=args.strategy,
            stop_on_fail=True,
        )
        entry = {"month": month, "saved": {k: str(v) for k, v in saved.items()}}
        if not args.fetch_only and saved:
            built = build_month(
                year=args.year,
                month_abbr=month,
                red_md=saved.get("red"),
                orange_md=saved.get("orange"),
                yellow_md=saved.get("yellow"),
                write_gold_gcal=not args.no_gold,
            )
            entry["build"] = {
                "coverage": built.get("coverage"),
                "rows": built.get("rows"),
                "impact_counts": built.get("impact_counts"),
                "landing": built.get("bronze_landing"),
            }
        results.append(entry)
        if len(saved) < 3:
            logger.error("Incomplete layers for %s (%s/3). Stopping.", month, len(saved))
            print(json.dumps(results, indent=2))
            return 1

    print(json.dumps(results, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
