import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.extract.client import build_calendar_url, build_weekly_export_url
from scripts.extract.config import BRONZE_COLUMNS
from scripts.extract.parser import parse_calendar_html, rows_to_dataframe
from scripts.extract.weekly_export import parse_weekly_csv, parse_weekly_export

FIXTURE_HTML = (Path(__file__).parent / "fixtures" / "calendar_sample.html").read_text()
FIXTURE_WEEKLY_CSV = (
    Path(__file__).parent / "fixtures" / "ff_calendar_thisweek_sample.csv"
).read_text()


def test_build_calendar_url_month_and_day():
    assert build_calendar_url("this") == "https://www.forexfactory.com/calendar?month=this"
    assert build_calendar_url("mar.2026") == "https://www.forexfactory.com/calendar?month=mar.2026"
    assert build_calendar_url("2026-03-02") == "https://www.forexfactory.com/calendar?day=2026-03-02"


def test_build_weekly_export_url():
    assert (
        build_weekly_export_url("csv")
        == "https://nfs.faireconomy.media/ff_calendar_thisweek.csv"
    )


def test_parse_weekly_csv_maps_impact_and_date():
    rows = parse_weekly_csv(FIXTURE_WEEKLY_CSV)
    assert len(rows) == 6
    nfp = next(r for r in rows if r["event"] == "Non-Farm Employment Change")
    assert nfp["currency"] == "USD"
    assert nfp["impact"] == "red"
    assert nfp["date"] == "Sep 4"
    assert nfp["forecast"] == "180K"
    assert next(r for r in rows if r["impact"] == "orange")["currency"] == "EUR"
    assert next(r for r in rows if r["event"] == "G20 Meetings")["impact"] == "gray"
    assert set(rows[0].keys()) == set(BRONZE_COLUMNS)
    assert parse_weekly_export(FIXTURE_WEEKLY_CSV, "csv") == rows


def test_parse_calendar_html_matches_bronze_schema():
    rows = parse_calendar_html(FIXTURE_HTML)

    assert len(rows) == 4
    assert set(rows[0].keys()) == set(BRONZE_COLUMNS)

    usd_row = next(row for row in rows if row["currency"] == "USD")
    assert usd_row["impact"] == "red"
    assert usd_row["event"] == "Non-Farm Employment Change"
    assert usd_row["forecast"] == "180K"
    assert usd_row["actual"] == "N/A"

    jpy_row = next(row for row in rows if row["currency"] == "JPY")
    assert jpy_row["impact"] == "gray"
    assert jpy_row["actual"] == "N/A"
    assert jpy_row["forecast"] == "N/A"


def test_rows_to_dataframe_column_order():
    rows = parse_calendar_html(FIXTURE_HTML)
    frame = rows_to_dataframe(rows)
    assert list(frame.columns) == BRONZE_COLUMNS


def test_parse_sep2026_red_markdown():
    from scripts.extract.markdown_parser import parse_calendar_markdown

    md = (Path(__file__).parent / "fixtures" / "calendar_sep2026_red.md").read_text()
    rows = parse_calendar_markdown(md, default_impact="red")
    assert len(rows) >= 20
    nfp = next(r for r in rows if r["event"] == "Non-Farm Employment Change")
    assert nfp["currency"] == "USD"
    assert nfp["impact"] == "red"
    assert nfp["forecast"] == "55K"


def test_bronze_extract_end_to_end_with_fixture(tmp_path, monkeypatch):
    from scripts.extract import extract_bronze as extract_module

    def fake_fetch(url: str, strategy: str = "http"):
        return FIXTURE_HTML, "fixture"

    monkeypatch.setattr(extract_module, "fetch_calendar_html", fake_fetch)

    output = tmp_path / "2026_03_ff_data.csv"
    result = extract_module.extract_bronze(period="mar.2026", output=str(output))
    assert result == output

    import pandas as pd

    frame = pd.read_csv(result)
    assert list(frame.columns) == BRONZE_COLUMNS
    assert len(frame) == 4


@pytest.mark.integration
def test_live_bronze_extract(tmp_path):
    pytest.importorskip("curl_cffi")

    from scripts.extract.extract_bronze import extract_bronze

    output = tmp_path / "live_bronze.csv"
    try:
        result = extract_bronze(period="this", output=str(output), strategy="http")
    except Exception as exc:
        pytest.skip(f"Live Forex Factory fetch unavailable in this environment: {exc}")

    assert result.exists()
    frame = rows_to_dataframe([])
    import pandas as pd

    live = pd.read_csv(result)
    assert list(live.columns) == BRONZE_COLUMNS
    assert len(live) > 0
    assert set(live["currency"].unique()).issubset({"AUD", "CAD", "CHF", "CNY", "EUR", "GBP", "JPY", "NZD", "USD"})
