"""B — bronze this-week CSV → landing → silver monthly partitions → Kimball mart.

The this-week export carries no ``Actual``, so it is upserted with
``mode="merge"``: it inserts newly scheduled events and refreshes forecasts, but
an empty incoming value never overwrites an actual already stored in the monthly
partition. Landing keeps a ``YYYY_Www.csv`` file as the audit trail of the fetch.
"""

from __future__ import annotations

import json
import logging
from collections import Counter
from datetime import date, datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

import pandas as pd

from scripts.extract.config import (
    BRONZE_LANDING_COLUMNS,
    BRONZE_LANDING_DIR,
    BRONZE_WEEKLY_DIR,
    GOLD_MART_DIR,
    SILVER_CHANGES_DIR,
    SILVER_EVENTS_DIR,
)
from scripts.transform.merge_silver import upsert_silver
from scripts.transform.to_google_calendar import DEFAULT_SOURCE_TZ, rebuild_monthly_gcals
from scripts.transform.to_kimball import silver_to_kimball
from scripts.transform.to_silver import (
    _parse_clock,
    _parse_event_date,
    landing_to_silver_frame,
)

logger = logging.getLogger(__name__)

WEEKLY_BRONZE_DEFAULT = BRONZE_WEEKLY_DIR / "thisweek.csv"


def utc_export_to_et_bronze(date_text: str, time_text: str, year: int) -> tuple[str, str]:
    """Faireconomy this-week clocks are UTC; bronze/HTML convention is US Eastern."""
    event_date = _parse_event_date(date_text, year)
    clock = _parse_clock(time_text)
    if event_date is None or clock is None:
        return date_text, time_text
    utc = datetime(
        event_date.year,
        event_date.month,
        event_date.day,
        clock.hour,
        clock.minute,
        tzinfo=ZoneInfo("UTC"),
    )
    eastern = utc.astimezone(ZoneInfo("America/New_York"))
    hour = eastern.strftime("%I").lstrip("0") or "12"
    return f"{eastern.strftime('%b')} {eastern.day}", f"{hour}:{eastern.strftime('%M%p').lower()}"


def infer_year_for_bronze_date(date_text: str, reference: date) -> int:
    """Pick calendar year for bronze ``Sep 4`` given a reference day (usually today)."""
    text = (date_text or "").strip()
    for year in (reference.year, reference.year - 1, reference.year + 1):
        for fmt in ("%b %d %Y", "%B %d %Y"):
            try:
                parsed = datetime.strptime(f"{text} {year}", fmt).date()
            except ValueError:
                continue
            if abs((parsed - reference).days) <= 10:
                return year
    return reference.year


def detect_iso_week(event_dates: list[str]) -> tuple[int, int]:
    """Majority ISO week from ``YYYY-MM-DD`` values."""
    weeks: list[tuple[int, int]] = []
    for raw in event_dates:
        try:
            parsed = date.fromisoformat(str(raw)[:10])
        except ValueError:
            continue
        iso = parsed.isocalendar()
        weeks.append((iso.year, iso.week))
    if not weeks:
        raise ValueError("No parseable event_date values to detect ISO week")
    year, week = Counter(weeks).most_common(1)[0][0]
    return year, week


def bronze_weekly_to_landing(
    bronze_csv: Path | str,
    *,
    reference: date | None = None,
    source_file: str | None = None,
    output: Path | None = None,
    export_clock_tz: str = "UTC",
) -> tuple[Path, dict]:
    bronze_csv = Path(bronze_csv)
    if not bronze_csv.exists():
        raise FileNotFoundError(f"Weekly bronze CSV missing: {bronze_csv}")

    frame = pd.read_csv(bronze_csv, dtype=str).fillna("")
    if frame.empty:
        raise ValueError(f"Weekly bronze CSV is empty: {bronze_csv}")

    today = reference or date.today()
    ingested_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H%M%SZ")
    src = source_file or bronze_csv.name

    landing_rows: list[dict[str, str]] = []
    years: list[int] = []
    for _, row in frame.iterrows():
        year = infer_year_for_bronze_date(str(row.get("date", "")), today)
        years.append(year)
        date_raw = str(row.get("date", "")).strip()
        time_raw = str(row.get("time", "")).strip()
        if export_clock_tz.upper() in {"UTC", "GMT"}:
            date_raw, time_raw = utc_export_to_et_bronze(date_raw, time_raw, year)
        landing_rows.append(
            {
                "date": f"{date_raw} {year}" if date_raw else date_raw,
                "time": time_raw,
                "currency": str(row.get("currency", "")).strip(),
                "impact": str(row.get("impact", "")).strip(),
                "event": str(row.get("event", "")).strip(),
                "actual": str(row.get("actual", "")).strip(),
                "forecast": str(row.get("forecast", "")).strip(),
                "previous": str(row.get("previous", "")).strip(),
                "source_file": src,
                "ingested_at": ingested_at,
            }
        )

    year = Counter(years).most_common(1)[0][0]
    landing_df = pd.DataFrame(landing_rows, columns=BRONZE_LANDING_COLUMNS)
    dest_dir = output.parent if output else BRONZE_LANDING_DIR
    dest_dir.mkdir(parents=True, exist_ok=True)
    landing_path = output or (dest_dir / f"weekly_ingest_{ingested_at}.csv")
    landing_df.to_csv(landing_path, index=False, na_rep="N/A")

    meta = {
        "layer": "bronze_landing",
        "source": "weekly_export",
        "source_file": src,
        "rows": int(len(landing_df)),
        "inferred_year": year,
        "impact_counts": landing_df["impact"].value_counts().to_dict(),
        "ingested_at": ingested_at,
    }
    landing_path.with_suffix(".meta.json").write_text(json.dumps(meta, indent=2) + "\n")
    logger.info("Weekly landing %s rows → %s", len(landing_df), landing_path)
    return landing_path, meta


def ingest_weekly_bronze(
    bronze_csv: Path | str = WEEKLY_BRONZE_DEFAULT,
    *,
    source_timezone: str = DEFAULT_SOURCE_TZ,
    export_clock_tz: str = "UTC",
    reference: date | None = None,
    write_gcal: bool = True,
    rebuild_mart: bool = True,
    landing_dir: Path | None = None,
    silver_dir: Path | None = None,
    changes_dir: Path | None = None,
    mart_dir: Path | None = None,
) -> dict:
    """Landing → coalesce upsert into silver ``YYYY_MM.csv`` → GCal → Kimball rebuild."""
    landing_dest_dir = Path(landing_dir) if landing_dir else BRONZE_LANDING_DIR
    silver_dest_dir = Path(silver_dir) if silver_dir else SILVER_EVENTS_DIR
    changes_dest_dir = Path(changes_dir) if changes_dir else SILVER_CHANGES_DIR
    landing_dest_dir.mkdir(parents=True, exist_ok=True)
    silver_dest_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    landing_path, landing_meta = bronze_weekly_to_landing(
        bronze_csv,
        reference=reference,
        source_file=Path(bronze_csv).name,
        output=landing_dest_dir / f"weekly_ingest_{stamp}.csv",
        export_clock_tz=export_clock_tz,
    )
    year = int(landing_meta["inferred_year"])

    silver_df = landing_to_silver_frame(
        landing_path,
        year=year,
        source_timezone=source_timezone,
    )
    if silver_df.empty:
        raise ValueError("Silver weekly convert produced 0 rows — check bronze dates")

    iso_year, iso_week = detect_iso_week(silver_df["event_date"].tolist())
    week_label = f"{iso_year}-W{iso_week:02d}"
    dest_name = f"{iso_year}_W{iso_week:02d}.csv"

    landing_final = landing_dest_dir / dest_name
    Path(landing_path).replace(landing_final)
    meta_tmp = Path(landing_path).with_suffix(".meta.json")
    if meta_tmp.exists():
        meta_tmp.replace(landing_final.with_suffix(".meta.json"))

    upsert = upsert_silver(
        silver_df,
        mode="merge",
        source=f"weekly_export:{week_label}",
        silver_dir=silver_dest_dir,
        changes_dir=changes_dest_dir,
    )

    landing_meta["week_label"] = week_label
    landing_meta["source_timezone"] = source_timezone
    landing_final.with_suffix(".meta.json").write_text(
        json.dumps(landing_meta, indent=2) + "\n"
    )
    logger.info(
        "Weekly silver %s rows → partitions %s",
        len(silver_df),
        sorted(upsert["partitions"]),
    )

    gcal_paths: list[str] = []
    if write_gcal:
        months = sorted(
            {str(day)[:7] for day in silver_df["event_date"] if str(day).strip()}
        )
        gcal_paths = [
            str(path)
            for path in rebuild_monthly_gcals(silver_dest_dir, months=months)
        ]

    mart_paths: dict[str, str] = {}
    if rebuild_mart:
        built = silver_to_kimball(
            silver_dir=silver_dest_dir,
            out_dir=mart_dir or GOLD_MART_DIR,
        )
        mart_paths = {name: str(path) for name, path in built.items()}

    return {
        "week_label": week_label,
        "iso_year": iso_year,
        "iso_week": iso_week,
        "rows": int(len(silver_df)),
        "landing": str(landing_final),
        "silver_partitions": upsert["partitions"],
        "silver_upsert": {
            key: upsert[key] for key in ("inserted", "updated", "deleted", "unchanged")
        },
        "silver_changes": upsert["changes"],
        "gold_gcal": gcal_paths,
        "mart": mart_paths,
        "impact_counts": silver_df["impact"].value_counts().to_dict(),
        "source_timezone": source_timezone,
    }
