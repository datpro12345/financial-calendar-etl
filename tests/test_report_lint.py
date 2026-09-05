import json
from pathlib import Path

from scripts.analyst.fact_pack import build_fact_pack
from scripts.analyst.report_lint import lint_files, lint_report
from scripts.analyst.run_weekly_report import attach_model_credit

MART = Path("data/gold/mart")
PACK_JSON = Path("reports/weekly/2026-W36-fact-pack.json")


def _pack() -> dict:
    if PACK_JSON.exists():
        return json.loads(PACK_JSON.read_text())
    return build_fact_pack(2026, 36, MART)


def test_lint_flags_invented_nfp_threshold():
    pack = _pack()
    fake = (
        "NFP fact_id=2890 in ≤ ~30K và AHE <99.9%. "
        "Long EUR/USD. target 1.36."
    )
    issues = lint_report(fake, pack)
    joined = " ".join(issues)
    assert "30K" in joined or "30k" in joined.lower()
    assert "99.9%" in joined
    assert any("entry-style" in i or "1.36" in i for i in issues)


def test_lint_allows_pack_labor_numbers():
    pack = _pack()
    nfp = next(e for e in pack["red_events"] if e["event"] == "Non-Farm Employment Change")
    ahe = next(e for e in pack["red_events"] if "Average Hourly Earnings" in e["event"])
    cad = next(
        e
        for e in pack["red_events"]
        if e["event"] == "Employment Change" and e["currency"] == "CAD"
    )
    clean = (
        f"USD NFP fact_id={nfp['fact_id']} F {nfp['forecast']} vs P {nfp['previous']}. "
        f"AHE fact_id={ahe['fact_id']} F {ahe['forecast']} / P {ahe['previous']}. "
        f"CAD Employment fact_id={cad['fact_id']} F {cad['forecast']} / P {cad['previous']} lúc 19:30."
    )
    assert lint_report(clean, pack) == []


def test_lint_existing_ling_fin_if_present():
    report = Path("reports/weekly/2026-W36-macro-outlook.ling-fin.md")
    if not report.exists() or not PACK_JSON.exists():
        return
    issues = lint_files(PACK_JSON, report)
    invented = [i for i in issues if "30K" in i or "0.2%" in i or "1.36" in i]
    assert invented == []


def test_attach_model_credit_same_closing_line():
    raw = (
        "VIII. x\n\n"
        "*Hết báo cáo. Không thêm mục, không checklist daily, "
        "không tín hiệu vào lệnh. Toàn bộ tiếng Việt.*\n\n"
        "---\n\n### Model đã viết báo cáo\n\n- **Model:** `old`\n"
    )
    out = attach_model_credit(raw, model="inclusionai/ling-3.0-flash-fin:free")
    assert "### Model đã viết báo cáo" not in out
    assert out.strip().endswith(
        "Toàn bộ tiếng Việt. model: `inclusionai/ling-3.0-flash-fin:free`"
    )
