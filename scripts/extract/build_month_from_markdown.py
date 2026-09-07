"""Build Medallion hops from FF markdown dumps: raw → landing → silver → gold."""

from __future__ import annotations

import argparse
import json
import logging
import shutil
import sys
from collections.abc import Iterable
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.extract.config import (
    BRONZE_LANDING_COLUMNS,
    BRONZE_LANDING_DIR,
    BRONZE_RAW_CALENDAR_DIR,
)
from scripts.extract.markdown_parser import (
    is_holiday_event,
    merge_impact_layers,
    parse_calendar_markdown,
)
from scripts.extract.parser import parse_calendar_html
from scripts.transform.merge_silver import upsert_silver
from scripts.transform.to_google_calendar import (
    parse_timezone_from_html,
    parse_timezone_from_markdown,
    silver_to_google_calendar,
)
from scripts.transform.to_silver import landing_to_silver_frame

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

MONTH_MAP = {
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


def _looks_like_html(text: str) -> bool:
    head = text.lstrip()[:200].lower()
    return head.startswith("<!doctype") or head.startswith("<html") or "calendar__table" in text


def _copy_raw(src: Path, year: int, month_num: str, kind: str) -> Path:
    dest_dir = BRONZE_RAW_CALENDAR_DIR / str(year)
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / f"{month_num}_{kind}{src.suffix or '.md'}"
    if src.resolve() == dest.resolve():
        return dest
    shutil.copy2(src, dest)
    return dest


def _parse_dump(text: str, default_impact: str) -> tuple[list[dict[str, str]], str | None]:
    """Parse HTML or markdown calendar dump; return rows + optional timezone."""
    if _looks_like_html(text):
        return parse_calendar_html(text), parse_timezone_from_html(text)
    return parse_calendar_markdown(text, default_impact=default_impact), parse_timezone_from_markdown(text)


def _load_layer(path: Path | None, impact: str, year: int, month_num: str) -> tuple[list[dict], str | None, list[str]]:
    if path is None or not path.exists():
        return [], None, []
    raw = _copy_raw(path, year, month_num, impact)
    text = path.read_text()
    rows, tz = _parse_dump(text, default_impact=impact)
    return rows, tz, [str(raw)]


def _holiday_rows(rows: Iterable[dict[str, str]]) -> list[dict[str, str]]:
    return [{**row, "impact": "gray"} for row in rows if is_holiday_event(row.get("event", ""))]


def build_month(
    *,
    year: int,
    month_abbr: str,
    all_md: Path | None = None,
    red_md: Path | None = None,
    orange_md: Path | None = None,
    yellow_md: Path | None = None,
    gray_md: Path | None = None,
    write_gold_gcal: bool = True,
    prune_missing: bool = False,
) -> dict:
    month_num = MONTH_MAP[month_abbr.lower()]
    if not any([all_md, red_md, orange_md, yellow_md, gray_md]):
        raise ValueError(
            "Provide at least one of --all-md / --red-md / --orange-md / --yellow-md / --gray-md"
        )

    source_tz = "America/New_York"
    raw_paths: list[str] = []
    source_files: list[str] = []

    yellow_rows: list[dict[str, str]] = []
    orange_rows: list[dict[str, str]] = []
    red_rows: list[dict[str, str]] = []
    gray_rows: list[dict[str, str]] = []

    # Unfiltered dump: yellow fallback + holiday names when dedicated gray is missing.
    # Name heuristic only catches "*Holiday*" (e.g. Bank Holiday), not New Year's Day.
    if all_md and all_md.exists():
        raw_all = _copy_raw(all_md, year, month_num, "all")
        raw_paths.append(str(raw_all))
        source_files.append(str(raw_all))
        all_text = all_md.read_text()
        all_rows, all_tz = _parse_dump(all_text, default_impact="yellow")
        if all_tz:
            source_tz = all_tz
        gray_rows = _holiday_rows(all_rows)
        if yellow_md is None:
            yellow_rows = [row for row in all_rows if not is_holiday_event(row.get("event", ""))]

    for impact, path in (
        ("red", red_md),
        ("orange", orange_md),
        ("yellow", yellow_md),
        ("gray", gray_md),
    ):
        rows, tz, paths = _load_layer(path, impact, year, month_num)
        if tz:
            source_tz = tz
        raw_paths.extend(paths)
        source_files.extend(paths)
        if impact == "red":
            red_rows = rows
        elif impact == "orange":
            orange_rows = rows
        elif impact == "yellow":
            yellow_rows = rows
        else:
            gray_rows = rows or gray_rows

    merged = merge_impact_layers(
        yellow_rows=yellow_rows,
        orange_rows=orange_rows,
        red_rows=red_rows,
        gray_rows=gray_rows,
    )
    layers_present = [
        name
        for name, rows in (
            ("red", red_rows),
            ("orange", orange_rows),
            ("yellow", yellow_rows),
            ("gray", gray_rows),
        )
        if rows
    ]
    coverage = "+".join(layers_present) if layers_present else "empty"

    ingested_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    source_file = "|".join(source_files) if source_files else ""
    landing_rows = [
        {**row, "source_file": source_file, "ingested_at": ingested_at}
        for row in merged
    ]
    landing_df = pd.DataFrame(landing_rows, columns=BRONZE_LANDING_COLUMNS)

    BRONZE_LANDING_DIR.mkdir(parents=True, exist_ok=True)
    landing_path = BRONZE_LANDING_DIR / f"{year}_{month_num}.csv"
    landing_df.to_csv(landing_path, index=False, na_rep="N/A")

    meta = {
        "year": year,
        "month": month_num,
        "layer": "bronze_landing",
        "source_timezone": source_tz,
        "coverage": coverage,
        "rows": len(landing_df),
        "impact_counts": landing_df["impact"].value_counts().to_dict() if len(landing_df) else {},
        "raw_files": raw_paths,
        "ingested_at": ingested_at,
    }
    meta_path = landing_path.with_suffix(".meta.json")
    meta_path.write_text(json.dumps(meta, indent=2))
    logger.info(
        "Bronze landing %s rows=%s coverage=%s tz=%s",
        landing_path.name,
        meta["rows"],
        coverage,
        source_tz,
    )

    silver_frame = landing_to_silver_frame(
        landing_path,
        year=year,
        source_timezone=source_tz,
    )
    # The dump is authoritative only for its own month; never let a stray
    # adjacent-month row trigger a refresh (and deletions) in another partition.
    target_part = f"{year}_{month_num}"
    in_month = silver_frame["event_date"].str.startswith(f"{year}-{month_num}")
    if not bool(in_month.all()):
        logger.warning(
            "Dropping %s silver row(s) outside %s", int((~in_month).sum()), target_part
        )
    upsert = upsert_silver(
        silver_frame[in_month],
        mode="refresh",
        source=f"monthly_html:{target_part}",
        delete_missing=prune_missing,
        scope_impacts=layers_present,
    )
    silver_path = Path(upsert["partitions"][target_part])

    gold_path = None
    if write_gold_gcal:
        try:
            gold_path = silver_to_google_calendar(silver_path, year=year)
        except Exception as exc:  # noqa: BLE001
            logger.warning("Gold Google Calendar skipped: %s", exc)

    return {
        "bronze_landing": str(landing_path),
        "bronze_meta": str(meta_path),
        "bronze_raw": raw_paths,
        "silver": str(silver_path),
        "silver_upsert": {
            key: upsert[key] for key in ("inserted", "updated", "deleted", "unchanged")
        },
        "silver_changes": upsert["changes"],
        "gold_google_calendar": str(gold_path) if gold_path else None,
        **meta,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build Medallion layers from FF markdown.")
    parser.add_argument("--year", type=int, required=True)
    parser.add_argument("--month", required=True, help="Month abbr, e.g. jan")
    parser.add_argument("--all-md", type=Path)
    parser.add_argument("--red-md", type=Path)
    parser.add_argument("--orange-md", type=Path)
    parser.add_argument("--yellow-md", type=Path)
    parser.add_argument("--gray-md", type=Path)
    parser.add_argument("--no-gold", action="store_true")
    parser.add_argument(
        "--prune",
        action="store_true",
        help="Delete silver rows this dump no longer lists (only for layers it carried)",
    )
    args = parser.parse_args()

    result = build_month(
        year=args.year,
        month_abbr=args.month,
        all_md=args.all_md,
        red_md=args.red_md,
        orange_md=args.orange_md,
        yellow_md=args.yellow_md,
        gray_md=args.gray_md,
        write_gold_gcal=not args.no_gold,
        prune_missing=args.prune,
    )
    print(json.dumps(result, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
