#!/usr/bin/env python3
"""ABCD weekly pipeline: fetch this week → gold mart → Fact Pack → outlook.

A  ``fetch_weekly.py`` — nfs.faireconomy.media this-week export (no WARP, no HTML).
B  landing → silver ``YYYY_Www.csv`` → Kimball mart (weekly wins on overlap).
C  Fact Pack from gold/mart.
D  LLM outlook + lint. Fail-stop: A or B fail ⇒ do not call the LLM.

Fetch settings match ``docs/scrape_strategy.md``: strategy=http, firefox135,
human_delay, CSV first, ~2 requests / 5 minutes. Do not fetch historical months.
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.analyst.language import DEFAULT_LANG
from scripts.analyst.llm_client import load_dotenv
from scripts.analyst.run_weekly_report import current_iso_week, run_outlook
from scripts.extract.config import GOLD_MART_DIR
from scripts.extract.fetch_weekly import fetch_this_week
from scripts.transform.to_google_calendar import DEFAULT_SOURCE_TZ
from scripts.transform.weekly_ingest import WEEKLY_BRONZE_DEFAULT, ingest_weekly_bronze

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


def run_abcd(
    *,
    fmt: str = "csv",
    skip_fetch: bool = False,
    fallback: bool = False,
    source_timezone: str = DEFAULT_SOURCE_TZ,
    export_clock_tz: str = "UTC",
    write_gcal: bool = True,
    year: int | None = None,
    week: int | None = None,
    dry_run: bool = False,
    skip_report: bool = False,
    skip_lint: bool = False,
    provider: str | None = None,
    model: str | None = None,
    timeout: int = 180,
    suffix: str | None = None,
    reports_dir: Path | None = None,
    mart_dir: Path = GOLD_MART_DIR,
    lang: str = DEFAULT_LANG,
) -> dict:
    summary: dict = {"ok": False, "stopped_at": None}

    if skip_fetch:
        bronze = WEEKLY_BRONZE_DEFAULT
        if not bronze.exists():
            raise FileNotFoundError(
                f"--skip-fetch but missing {bronze}. Run without --skip-fetch first."
            )
        summary["A"] = {"skipped": True, "csv": str(bronze)}
        logger.info("A skipped — using existing %s", bronze)
    else:
        logger.info("A — fetch this-week export (%s), no WARP, fallback=%s", fmt, fallback)
        summary["A"] = fetch_this_week(fmt=fmt, fallback=fallback)
        logger.info(
            "A ok — %s rows via %s",
            summary["A"]["rows"],
            summary["A"]["method"],
        )

    logger.info("B — bronze weekly → silver → mart")
    summary["B"] = ingest_weekly_bronze(
        summary["A"].get("csv") or str(WEEKLY_BRONZE_DEFAULT),
        source_timezone=source_timezone,
        export_clock_tz=export_clock_tz,
        write_gcal=write_gcal,
        rebuild_mart=True,
        mart_dir=mart_dir,
    )
    logger.info(
        "B ok — %s (%s silver rows)",
        summary["B"]["week_label"],
        summary["B"]["rows"],
    )

    iso_year = year if year is not None else int(summary["B"]["iso_year"])
    iso_week = week if week is not None else int(summary["B"]["iso_week"])
    summary["week_label"] = f"{iso_year}-W{iso_week:02d}"

    if skip_report:
        summary["C"] = {"skipped": True}
        summary["D"] = {"skipped": True}
        summary["ok"] = True
        summary["stopped_at"] = "B"
        return summary

    logger.info("C+D — Fact Pack + outlook for %s", summary["week_label"])
    outlook = run_outlook(
        year=iso_year,
        week=iso_week,
        mart_dir=mart_dir,
        reports_dir=reports_dir or (REPO_ROOT / "reports" / "weekly"),
        provider=provider,
        model=model,
        dry_run=dry_run,
        timeout=timeout,
        suffix=suffix,
        skip_lint=skip_lint,
        lang=lang,
    )
    summary["C"] = {
        "fact_pack_json": outlook["fact_pack_json"],
        "fact_pack_md": outlook["fact_pack_md"],
    }
    summary["D"] = outlook
    summary["ok"] = outlook["exit_code"] == 0
    summary["stopped_at"] = "D"
    return summary


def main() -> int:
    load_dotenv()
    today_year, today_week = current_iso_week()
    parser = argparse.ArgumentParser(
        description="ABCD: fetch this week (no WARP) → mart → weekly outlook",
    )
    parser.add_argument("--fmt", choices=("csv", "xml", "json"), default="csv")
    parser.add_argument(
        "--skip-fetch",
        action="store_true",
        help="Reuse data/bronze/weekly/thisweek.csv (no network)",
    )
    parser.add_argument(
        "--fallback-formats",
        action="store_true",
        help="If CSV fails, try XML then JSON (burns the ~2/5 min quota)",
    )
    parser.add_argument("--source-tz", default=DEFAULT_SOURCE_TZ)
    parser.add_argument(
        "--export-clock-tz",
        default="UTC",
        help="Clock TZ of the faireconomy export (UTC). Converted to US Eastern for bronze.",
    )
    parser.add_argument("--no-gcal", action="store_true")
    parser.add_argument("--year", type=int, help="Override report ISO year (default: from fetch)")
    parser.add_argument("--week", type=int, help="Override report ISO week (default: from fetch)")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--skip-report", action="store_true", help="Stop after B (no LLM)")
    parser.add_argument("--skip-lint", action="store_true")
    parser.add_argument("--provider", choices=("openrouter", "google"))
    parser.add_argument("--model")
    parser.add_argument("--timeout", type=int, default=180)
    parser.add_argument("--suffix")
    parser.add_argument(
        "--lang",
        default=os.environ.get("REPORT_LANG", DEFAULT_LANG),
        help="Report language: vi, en, or any name (ja, es, …). Default: vi or REPORT_LANG",
    )
    parser.add_argument("--reports-dir", type=Path)
    parser.add_argument("--mart-dir", type=Path, default=GOLD_MART_DIR)
    args = parser.parse_args()

    try:
        summary = run_abcd(
            fmt=args.fmt,
            skip_fetch=args.skip_fetch,
            fallback=args.fallback_formats,
            source_timezone=args.source_tz,
            export_clock_tz=args.export_clock_tz,
            write_gcal=not args.no_gcal,
            year=args.year,
            week=args.week,
            dry_run=args.dry_run,
            skip_report=args.skip_report,
            skip_lint=args.skip_lint,
            provider=args.provider,
            model=args.model,
            timeout=args.timeout,
            suffix=args.suffix,
            lang=args.lang,
            reports_dir=args.reports_dir,
            mart_dir=args.mart_dir,
        )
    except Exception as exc:  # noqa: BLE001
        logger.error("ABCD stopped: %s", exc)
        print(json.dumps({"ok": False, "error": str(exc)}, indent=2))
        return 1

    print(json.dumps(summary, indent=2, default=str))
    if not summary.get("ok"):
        d_code = (summary.get("D") or {}).get("exit_code")
        return int(d_code) if d_code else 1
    logger.info(
        "ABCD done for %s (today is %s-W%02d)",
        summary.get("week_label"),
        today_year,
        today_week,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
