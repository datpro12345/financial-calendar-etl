from scripts.transform.gcal_blurbs import blurb_for, format_gcal_description


def test_nfp_matches_vietnamese_blurb():
    text = blurb_for("Non-Farm Employment Change", "USD")
    assert "NFP" in text
    assert "USD" in text or "Mỹ" in text


def test_core_cpi_beats_cpi():
    core = blurb_for("Core CPI y/y", "USD")
    raw = blurb_for("CPI y/y", "USD")
    assert "lõi" in core
    assert core != raw


def test_unknown_uses_fallback():
    text = blurb_for("Totally Made Up Red Print", "GBP")
    assert "GBP" in text
    assert "red" in text.lower() or "Red" in text or "lệnh" in text


def test_description_has_fp_and_no_llm_tone():
    desc = format_gcal_description(
        event="Non-Farm Employment Change",
        currency="USD",
        forecast="55K",
        previous="-23K",
        actual="",
    )
    assert "F 55K" in desc
    assert "P -23K" in desc
    assert "A —" in desc
    assert "Asia/Ho_Chi_Minh" in desc
