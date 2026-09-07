from datetime import date
from pathlib import Path

import pandas as pd

from scripts.extract.parser import rows_to_dataframe
from scripts.extract.weekly_export import parse_weekly_csv
from scripts.transform.weekly_ingest import (
    detect_iso_week,
    infer_year_for_bronze_date,
    ingest_weekly_bronze,
    utc_export_to_et_bronze,
)

FIXTURE = Path(__file__).parent / "fixtures" / "ff_calendar_thisweek_sample.csv"


def test_utc_export_nfp_is_et_830():
    date_et, time_et = utc_export_to_et_bronze("Sep 4", "12:30pm", 2026)
    assert date_et == "Sep 4"
    assert time_et == "8:30am"


def test_infer_year_near_reference():
    assert infer_year_for_bronze_date("Sep 4", date(2026, 9, 6)) == 2026
    assert infer_year_for_bronze_date("Dec 30", date(2027, 1, 3)) == 2026


def test_detect_iso_week_majority():
    year, week = detect_iso_week(["2026-08-31", "2026-09-04", "2026-09-06"])
    assert (year, week) == (2026, 36)


def test_ingest_weekly_fixture(tmp_path):
    bronze = tmp_path / "thisweek.csv"
    rows = parse_weekly_csv(FIXTURE.read_text())
    rows_to_dataframe(rows).to_csv(bronze, index=False)

    result = ingest_weekly_bronze(
        bronze,
        reference=date(2026, 9, 6),
        export_clock_tz="America/New_York",
        write_gcal=False,
        rebuild_mart=False,
        landing_dir=tmp_path / "landing",
        silver_dir=tmp_path / "silver",
        changes_dir=tmp_path / "changes",
        mart_dir=tmp_path / "mart",
    )
    assert result["week_label"] == "2026-W36"
    assert result["rows"] == 6

    # Landing keeps the weekly audit file; silver is partitioned by event month.
    assert Path(result["landing"]).name == "2026_W36.csv"
    assert sorted(result["silver_partitions"]) == ["2026_09"]

    silver = Path(result["silver_partitions"]["2026_09"])
    assert silver.name == "2026_09.csv"
    text = silver.read_text()
    assert "Non-Farm Employment Change" in text
    assert "2026-09-04" in text
    assert "19:30" in text  # 8:30am ET → 19:30 HCM


def test_weekly_upsert_never_blanks_a_stored_actual(tmp_path):
    """The this-week export has no Actual column; it must not erase one."""
    bronze = tmp_path / "thisweek.csv"
    rows = parse_weekly_csv(FIXTURE.read_text())
    rows_to_dataframe(rows).to_csv(bronze, index=False)

    silver_dir = tmp_path / "silver"
    kwargs = dict(
        reference=date(2026, 9, 6),
        export_clock_tz="America/New_York",
        write_gcal=False,
        rebuild_mart=False,
        landing_dir=tmp_path / "landing",
        silver_dir=silver_dir,
        changes_dir=tmp_path / "changes",
        mart_dir=tmp_path / "mart",
    )
    ingest_weekly_bronze(bronze, **kwargs)

    partition = silver_dir / "2026_09.csv"
    frame = pd.read_csv(partition, dtype=str).fillna("")
    target = frame["event"] == "Non-Farm Employment Change"
    assert target.any()
    frame.loc[target, "actual"] = "22K"
    frame.to_csv(partition, index=False)

    result = ingest_weekly_bronze(bronze, **kwargs)

    after = pd.read_csv(partition, dtype=str).fillna("")
    kept = after.loc[after["event"] == "Non-Farm Employment Change", "actual"]
    assert list(kept) == ["22K"]
    assert result["silver_upsert"]["inserted"] == 0
    assert result["silver_upsert"]["deleted"] == 0
