from pathlib import Path

from scripts.analyst.fact_pack import build_fact_pack, iso_week_bounds, next_iso_week
from scripts.analyst.run_weekly_report import load_control_lane

MART = Path("data/gold/mart")


def test_iso_week_bounds_monday_sunday():
    start, end = iso_week_bounds(2026, 36)
    assert start.isoformat() == "2026-08-31"
    assert end.isoformat() == "2026-09-06"


def test_week_36_counts_and_nfp_cad_clash():
    pack = build_fact_pack(2026, 36, MART)
    assert pack["coverage"]["by_impact"]["red"] >= 12
    usd = next(r for r in pack["currency_exposure"] if r["currency"] == "USD")
    cad = next(r for r in pack["currency_exposure"] if r["currency"] == "CAD")
    nzd = next(r for r in pack["currency_exposure"] if r["currency"] == "NZD")
    assert usd["red"] >= 3
    assert cad["red"] >= 2
    assert nzd["red"] >= 3

    nfp_clash = next(
        c
        for c in pack["clashes"]
        if any(e["event"] == "Non-Farm Employment Change" for e in c["events"])
    )
    names = {e["event"] for e in nfp_clash["events"]}
    currencies = set(nfp_clash["currencies"])
    assert "Employment Change" in names
    assert "USD" in currencies and "CAD" in currencies
    assert nfp_clash["event_count"] >= 5

    nfp = next(e for e in pack["red_events"] if e["event"] == "Non-Farm Employment Change")
    assert nfp["forecast"] == "55K"
    assert nfp["previous"] == "-23K"
    assert nfp["expectation_shifted"] is True
    assert nfp["session"] == "us"
    assert nfp["focus"] == "primary"
    assert pack["focus"]["primary_red"] >= 3
    assert pack["focus"]["secondary_red"] >= 9
    assert next_iso_week(2026, 36) == (2026, 37)
    nxt = pack["next_week"]
    assert nxt["available"] is True
    assert nxt["week_label"] == "2026-W37"
    assert nxt["focus"]["primary_red"] >= 1
    assert any(e["currency"] == "EUR" for e in nxt["red_events"])


def test_control_lane_files_load():
    text = load_control_lane()
    assert "nfp" in text
    assert "impossible_trinity" in text
    assert "Dual mandate" in text or "dual mandate" in text.lower()
