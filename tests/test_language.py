from pathlib import Path

from scripts.analyst.language import apply_language, report_suffix, resolve_language
from scripts.analyst.run_weekly_report import attach_model_credit


def test_resolve_vi_and_en():
    vi = resolve_language("vi")
    en = resolve_language("EN")
    assert vi.code == "vi"
    assert "Vietnamese" in vi.write_instruction or "tiếng Việt" in vi.user_preamble
    assert en.code == "en"
    assert "English" in en.write_instruction


def test_resolve_custom_language():
    ja = resolve_language("ja")
    assert ja.code == "ja"
    assert "ja" in ja.write_instruction.lower() or "ja" in ja.user_preamble.lower()


def test_apply_language_replaces_tokens():
    contract = Path("docs/analyst/prompts/weekly_soros_prompt.md").read_text()
    assert "{{REPORT_LANGUAGE_RULE}}" in contract
    out = apply_language(contract, resolve_language("en"))
    assert "{{" not in out
    assert "English" in out
    assert "End of report" in out


def test_report_suffix_includes_lang_and_extra():
    assert report_suffix("en") == "en"
    assert report_suffix("vi", "ling-fin") == "vi.ling-fin"


def test_attach_model_credit_english_closing():
    raw = "VIII. x\n\nEnd of report. No extra sections, no daily checklist, no trade signals. Entire report in English.\n"
    out = attach_model_credit(raw, model="inclusionai/ling-3.0-flash-fin:free", language="en")
    assert out.strip().endswith(
        "Entire report in English. model: `inclusionai/ling-3.0-flash-fin:free`"
    )
