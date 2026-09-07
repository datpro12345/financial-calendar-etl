"""Silver coalesce upsert: `actual` arrives late and must never be erased."""

from pathlib import Path

import pandas as pd
import pytest

from scripts.extract.config import SILVER_COLUMNS
from scripts.extract.markdown_parser import parse_calendar_markdown
from scripts.extract.build_month_from_markdown import _holiday_rows
from scripts.transform.merge_silver import (
    event_uid,
    partition_of,
    read_partition,
    upsert_silver,
)
from scripts.transform.to_kimball import silver_to_kimball

FIXTURES = Path(__file__).parent / "fixtures"


def silver_row(**overrides) -> dict:
    row = {
        "event_date": "2026-09-01",
        "time_raw": "1:30pm",
        "event_datetime_utc": "2026-09-01T06:30:00+00:00",
        "event_datetime_hcm": "2026-09-01T13:30:00+07:00",
        "currency": "AUD",
        "impact": "yellow",
        "event": "Commodity Prices y/y",
        "actual": "",
        "forecast": "",
        "previous": "",
        "source_timezone": "Asia/Novosibirsk",
        "first_seen_at": "2026-09-03T07:55:34Z",
        "updated_at": "2026-09-03T07:55:34Z",
    }
    row.update(overrides)
    return row


def frame(*rows: dict) -> pd.DataFrame:
    return pd.DataFrame(list(rows), columns=[c for c in SILVER_COLUMNS if c != "event_uid"])


def upsert(rows, tmp_path, **kwargs):
    kwargs.setdefault("silver_dir", tmp_path / "silver")
    kwargs.setdefault("changes_dir", tmp_path / "changes")
    return upsert_silver(rows, **kwargs)


def test_empty_actual_never_overwrites_a_stored_one(tmp_path):
    """The exact regression measured in gold: 56 actuals blanked by a weekly run."""
    upsert(frame(silver_row(actual="15.5%", forecast="14.0%")), tmp_path)
    upsert(frame(silver_row(actual="", forecast="14.0%")), tmp_path)

    out = read_partition(tmp_path / "silver" / "2026_09.csv")
    assert len(out) == 1
    assert out.iloc[0]["actual"] == "15.5%"


def test_non_empty_revision_does_overwrite(tmp_path):
    """Coalesce means "empty never wins", not "old always wins"."""
    upsert(frame(silver_row(actual="15.5%")), tmp_path)
    upsert(frame(silver_row(actual="15.6%")), tmp_path)

    out = read_partition(tmp_path / "silver" / "2026_09.csv")
    assert out.iloc[0]["actual"] == "15.6%"


def test_new_event_from_weekly_is_inserted(tmp_path):
    upsert(frame(silver_row()), tmp_path)
    result = upsert(
        frame(
            silver_row(
                event="Non-Farm Employment Change",
                currency="USD",
                event_datetime_utc="2026-09-04T12:30:00+00:00",
                event_date="2026-09-04",
            )
        ),
        tmp_path,
    )

    assert result["inserted"] == 1
    assert len(read_partition(tmp_path / "silver" / "2026_09.csv")) == 2


def test_same_instant_from_two_timezones_is_one_row(tmp_path):
    """The this-week export publishes US Eastern, the monthly dump Novosibirsk.

    Identity is the absolute instant, so the two clocks describe one release.
    """
    monthly = silver_row(time_raw="1:30pm", source_timezone="Asia/Novosibirsk", actual="15.5%")
    weekly = silver_row(time_raw="2:30am", source_timezone="America/New_York", actual="")

    upsert(frame(monthly), tmp_path)
    result = upsert(frame(weekly), tmp_path)

    out = read_partition(tmp_path / "silver" / "2026_09.csv")
    assert result["inserted"] == 0
    assert len(out) == 1
    assert out.iloc[0]["actual"] == "15.5%"
    # Presentation stays with whichever source created the row, so time_raw and
    # source_timezone can never disagree.
    assert out.iloc[0]["time_raw"] == "1:30pm"
    assert out.iloc[0]["source_timezone"] == "Asia/Novosibirsk"


def test_equivalent_instant_formats_share_one_uid():
    assert event_uid(event_datetime_utc="2026-09-01T06:30:00+00:00", currency="AUD", event="X") == (
        event_uid(event_datetime_utc="2026-09-01T06:30:00Z", currency="AUD", event="X")
    )


def test_speeches_at_different_times_stay_separate(tmp_path):
    """12 Lagarde/FOMC speeches share (date, currency, event) but not the instant."""
    speeches = [
        silver_row(
            event="ECB President Lagarde Speaks",
            currency="EUR",
            time_raw=f"{hour}:00am",
            event_datetime_utc=f"2026-09-01T{hour:02d}:00:00+00:00",
        )
        for hour in range(1, 13)
    ]
    upsert(frame(*speeches), tmp_path)

    out = read_partition(tmp_path / "silver" / "2026_09.csv")
    assert len(out) == 12
    assert out["event_uid"].is_unique


def test_untimed_release_variants_stay_separate(tmp_path):
    """A "Sep Data" catch-up and a clocked print of the same event are two rows."""
    clocked = silver_row(
        event="Building Permits",
        currency="USD",
        time_raw="8:30pm",
        event_datetime_utc="2026-09-01T13:30:00+00:00",
    )
    catch_up = silver_row(
        event="Building Permits",
        currency="USD",
        time_raw="Sep Data",
        event_datetime_utc="",
        event_datetime_hcm="",
        actual="1.42M",
    )
    upsert(frame(clocked, catch_up), tmp_path)

    out = read_partition(tmp_path / "silver" / "2026_09.csv")
    assert len(out) == 2
    assert sorted(out["time_raw"]) == ["8:30pm", "Sep Data"]


def test_untimed_rows_are_distinguished_by_their_label(tmp_path):
    tentative = silver_row(
        event="Spanish 10-y Bond Auction",
        currency="EUR",
        time_raw="Tentative",
        event_datetime_utc="",
    )
    all_day = silver_row(
        event="Spanish 10-y Bond Auction",
        currency="EUR",
        time_raw="All Day",
        event_datetime_utc="",
    )
    upsert(frame(tentative, all_day), tmp_path)

    assert len(read_partition(tmp_path / "silver" / "2026_09.csv")) == 2


def test_second_upsert_of_the_same_input_is_byte_identical(tmp_path):
    rows = frame(silver_row(actual="15.5%"), silver_row(event="Other", currency="NZD"))
    upsert(rows, tmp_path)
    first = (tmp_path / "silver" / "2026_09.csv").read_bytes()

    result = upsert(rows, tmp_path)

    assert (tmp_path / "silver" / "2026_09.csv").read_bytes() == first
    assert result == {
        **result,
        "inserted": 0,
        "updated": 0,
        "deleted": 0,
        "unchanged": 2,
    }
    # Nothing changed, so the audit log must not grow either.
    assert result["changes"] == []


def test_partition_follows_the_event_month(tmp_path):
    august = silver_row(event_date="2026-08-31", event_datetime_utc="2026-08-31T06:30:00+00:00")
    upsert(frame(august, silver_row()), tmp_path)

    assert (tmp_path / "silver" / "2026_08.csv").exists()
    assert (tmp_path / "silver" / "2026_09.csv").exists()
    assert partition_of("2026-08-31") == "2026_08"


def test_refresh_keeps_a_gray_row_it_does_not_cover(tmp_path):
    """A red/orange/yellow dump must not delete the holiday layer."""
    holiday = silver_row(
        event="Bank Holiday",
        currency="USD",
        impact="gray",
        time_raw="All Day",
        event_datetime_utc="",
        event_datetime_hcm="",
    )
    upsert(frame(holiday, silver_row()), tmp_path)

    upsert(
        frame(silver_row()),
        tmp_path,
        mode="refresh",
        delete_missing=True,
        scope_impacts=["red", "orange", "yellow"],
    )

    out = read_partition(tmp_path / "silver" / "2026_09.csv")
    assert set(out["impact"]) == {"gray", "yellow"}


def test_refresh_prunes_a_cancelled_row_inside_its_scope(tmp_path):
    cancelled = silver_row(
        event="Cancelled Speech",
        event_datetime_utc="2026-09-02T06:30:00+00:00",
        event_date="2026-09-02",
    )
    upsert(frame(silver_row(), cancelled), tmp_path)

    result = upsert(
        frame(silver_row()),
        tmp_path,
        mode="refresh",
        delete_missing=True,
        scope_impacts=["yellow"],
    )

    out = read_partition(tmp_path / "silver" / "2026_09.csv")
    assert result["deleted"] == 1
    assert list(out["event"]) == ["Commodity Prices y/y"]


def test_refresh_does_not_prune_unless_asked(tmp_path):
    """An old dump replayed today must not delete rows a newer source added."""
    upsert(frame(silver_row(), silver_row(event="Added Later", currency="GBP")), tmp_path)

    result = upsert(frame(silver_row()), tmp_path, mode="refresh")

    assert result["deleted"] == 0
    assert len(read_partition(tmp_path / "silver" / "2026_09.csv")) == 2


def test_delete_missing_requires_refresh_mode(tmp_path):
    with pytest.raises(ValueError, match="delete_missing requires"):
        upsert(frame(silver_row()), tmp_path, mode="merge", delete_missing=True)


def test_delta_log_records_the_arriving_actual(tmp_path):
    upsert(frame(silver_row()), tmp_path, source="weekly_export:2026-W36")
    upsert(frame(silver_row(actual="15.5%")), tmp_path, source="monthly_html:2026_09")

    log = pd.read_csv(tmp_path / "changes" / "2026_09.csv", dtype=str).fillna("")
    assert list(log["change_type"]) == ["insert", "update"]
    arrival = log[log["change_type"] == "update"].iloc[0]
    assert arrival["field"] == "actual"
    assert arrival["old_value"] == ""
    assert arrival["new_value"] == "15.5%"
    assert arrival["source"] == "monthly_html:2026_09"
    assert arrival["event"] == "Commodity Prices y/y"


def test_updated_at_only_moves_on_a_real_change(tmp_path):
    upsert(frame(silver_row()), tmp_path, now="2026-09-01T00:00:00Z")
    upsert(frame(silver_row()), tmp_path, now="2026-09-02T00:00:00Z")

    out = read_partition(tmp_path / "silver" / "2026_09.csv")
    assert out.iloc[0]["updated_at"] == "2026-09-03T07:55:34Z"

    upsert(frame(silver_row(actual="15.5%")), tmp_path, now="2026-09-04T00:00:00Z")
    out = read_partition(tmp_path / "silver" / "2026_09.csv")
    assert out.iloc[0]["updated_at"] == "2026-09-04T00:00:00Z"
    assert out.iloc[0]["first_seen_at"] == "2026-09-03T07:55:34Z"


def test_fact_id_survives_adding_a_new_event(tmp_path):
    """`macro_textbook.md` compares actual vs forecast on the same fact_id."""
    silver_dir = tmp_path / "silver"
    upsert(frame(silver_row(), silver_row(event="Zulu Late Event", currency="NZD")), tmp_path)
    silver_to_kimball(silver_dir=silver_dir, out_dir=tmp_path / "mart1")
    before = pd.read_csv(tmp_path / "mart1" / "fact_calendar_release.csv", dtype=str)

    # An event sorting before the others would have renumbered a sequential id.
    upsert(
        frame(
            silver_row(
                event="AAA Brand New Event",
                currency="AUD",
                event_datetime_utc="2026-09-01T05:00:00+00:00",
            )
        ),
        tmp_path,
    )
    silver_to_kimball(silver_dir=silver_dir, out_dir=tmp_path / "mart2")
    after = pd.read_csv(tmp_path / "mart2" / "fact_calendar_release.csv", dtype=str)

    assert len(after) == len(before) + 1
    kept = after[after["fact_id"].isin(before["fact_id"])]
    assert len(kept) == len(before)
    assert set(before["event_key"]) <= set(after["event_key"])


def test_weekly_gray_row_reaches_the_mart(tmp_path):
    holiday = silver_row(
        event="Bank Holiday",
        currency="USD",
        impact="gray",
        time_raw="All Day",
        event_datetime_utc="",
        event_datetime_hcm="",
    )
    upsert(frame(holiday, silver_row()), tmp_path)
    silver_to_kimball(silver_dir=tmp_path / "silver", out_dir=tmp_path / "mart")

    fact = pd.read_csv(tmp_path / "mart" / "fact_calendar_release.csv", dtype=str)
    impacts = pd.read_csv(tmp_path / "mart" / "dim_impact.csv", dtype=str)
    codes = dict(zip(impacts["impact_key"], impacts["impact_code"]))
    assert "gray" in {codes[key] for key in fact["impact_key"]}


def test_stale_weekly_partition_is_ignored_by_the_mart(tmp_path):
    """A leftover YYYY_Www.csv must not double-count rows after the migration."""
    silver_dir = tmp_path / "silver"
    upsert(frame(silver_row(actual="15.5%")), tmp_path)
    stale = read_partition(silver_dir / "2026_09.csv")
    stale.to_csv(silver_dir / "2026_W36.csv", index=False)

    silver_to_kimball(silver_dir=silver_dir, out_dir=tmp_path / "mart")

    fact = pd.read_csv(tmp_path / "mart" / "fact_calendar_release.csv", dtype=str)
    assert len(fact) == 1
    assert fact.iloc[0]["actual_txt"] == "15.5%"


def test_all_dump_yields_the_gray_holiday_layer():
    """`impacts=0` was never fetched; the `all` dump is the offline fallback."""
    text = (FIXTURES / "calendar_sep2026_all.md").read_text()
    rows = parse_calendar_markdown(text, default_impact="yellow")

    holidays = _holiday_rows(rows)

    assert len(holidays) == 8
    assert {row["impact"] for row in holidays} == {"gray"}
    # Bronze keeps the published date form; ISO conversion happens in silver.
    assert ("Sep 7", "USD") in {(row["date"], row["currency"]) for row in holidays}
