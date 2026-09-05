#!/usr/bin/env python3
"""Fetch Forex Factory *this week* via official-ish weekly export (no HTML scrape).

Prefer this path when you only need the current week — avoids Cloudflare on
www.forexfactory.com. Feed is rate-limited (~2 requests / 5 minutes).
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.extract.client import fetch_weekly_export
from scripts.extract.config import BRONZE_RAW_CALENDAR_DIR, BRONZE_WEEKLY_DIR
from scripts.extract.parser import rows_to_dataframe
from scripts.extract.weekly_export import parse_weekly_export

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


def fetch_this_week(
    *,
    fmt: str = "csv",
    out_raw: Path | None = None,
    out_csv: Path | None = None,
    fallback: bool = True,
) -> dict:
    """A — this-week export → bronze raw + bronze weekly CSV. No WARP."""
    body, method = fetch_weekly_export(fmt=fmt, fallback=fallback)
    used_fmt = method.rsplit(":", 1)[-1]

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    raw_dir = BRONZE_RAW_CALENDAR_DIR / "weekly"
    raw_dir.mkdir(parents=True, exist_ok=True)
    raw_path = out_raw or (raw_dir / f"thisweek_{stamp}.{used_fmt}")
    raw_path.write_text(body)
    logger.info("Raw dump → %s via %s (%s bytes)", raw_path, method, len(body))

    rows = parse_weekly_export(body, used_fmt)
    frame = rows_to_dataframe(rows)
    BRONZE_WEEKLY_DIR.mkdir(parents=True, exist_ok=True)
    csv_path = out_csv or (BRONZE_WEEKLY_DIR / "thisweek.csv")
    frame.to_csv(csv_path, index=False)

    return {
        "method": method,
        "raw": str(raw_path),
        "csv": str(csv_path),
        "rows": int(len(frame)),
        "impact_counts": frame["impact"].value_counts().to_dict() if len(frame) else {},
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Fetch FF this-week export → bronze")
    parser.add_argument("--fmt", choices=("csv", "xml", "json"), default="csv")
    parser.add_argument(
        "--out-raw",
        type=Path,
        default=None,
        help="Where to save the raw export dump",
    )
    parser.add_argument(
        "--out-csv",
        type=Path,
        default=None,
        help="Parsed bronze CSV (default: data/bronze/weekly/thisweek.csv)",
    )
    parser.add_argument(
        "--no-fallback",
        action="store_true",
        help="Do not try XML/JSON if CSV fails (saves the ~2/5 min quota)",
    )
    args = parser.parse_args()
    summary = fetch_this_week(
        fmt=args.fmt,
        out_raw=args.out_raw,
        out_csv=args.out_csv,
        fallback=not args.no_fallback,
    )
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
