"""Output language for the weekly outlook. Numbers stay in the Fact Pack."""

from __future__ import annotations

from dataclasses import dataclass

DEFAULT_LANG = "vi"


@dataclass(frozen=True)
class LanguageProfile:
    code: str
    english_name: str
    write_instruction: str
    closing_line: str
    closing_markers: tuple[str, ...]
    user_preamble: str


_BUILTIN: dict[str, LanguageProfile] = {
    "vi": LanguageProfile(
        code="vi",
        english_name="Vietnamese",
        write_instruction=(
            "Write the entire analysis and conclusions in Vietnamese. "
            "Keep event names, currency codes, and pair symbols in English."
        ),
        closing_line=(
            "Hết báo cáo. Không thêm mục, không checklist daily, không tín hiệu vào lệnh. "
            "Toàn bộ tiếng Việt."
        ),
        closing_markers=("Hết báo cáo", "End of report"),
        user_preamble=(
            "Viết toàn bộ báo cáo bằng tiếng Việt. "
            "Kết luận tách Chính (USD/EUR/GBP/JPY) và Phụ."
        ),
    ),
    "en": LanguageProfile(
        code="en",
        english_name="English",
        write_instruction=(
            "Write the entire analysis and conclusions in English. "
            "Keep event names, currency codes, and pair symbols in English. "
            "Translate section titles I–VIII into English."
        ),
        closing_line=(
            "End of report. No extra sections, no daily checklist, no trade signals. "
            "Entire report in English."
        ),
        closing_markers=("End of report", "Hết báo cáo"),
        user_preamble=(
            "Write the entire report in English. "
            "Split conclusions into Primary (USD/EUR/GBP/JPY) and Secondary."
        ),
    ),
}


def normalize_lang(code: str | None) -> str:
    raw = (code or DEFAULT_LANG).strip().lower().replace("_", "-")
    if not raw:
        return DEFAULT_LANG
    return raw.split("-", 1)[0]


def resolve_language(code: str | None) -> LanguageProfile:
    """Return a profile for vi/en, or a generic profile for any other language name."""
    key = normalize_lang(code)
    if key in _BUILTIN:
        return _BUILTIN[key]
    label = (code or key).strip()
    return LanguageProfile(
        code=key,
        english_name=label,
        write_instruction=(
            f"Write the entire analysis and conclusions in {label}. "
            "Keep event names, currency codes, and pair symbols in English. "
            f"Translate section titles I–VIII into {label}."
        ),
        closing_line=(
            f"End of report. No extra sections, no daily checklist, no trade signals. "
            f"Entire report in {label}."
        ),
        closing_markers=("End of report", "Hết báo cáo"),
        user_preamble=(
            f"Write the entire report in {label}. "
            "Split conclusions into Primary (USD/EUR/GBP/JPY) and Secondary."
        ),
    )


def apply_language(contract: str, profile: LanguageProfile) -> str:
    text = contract
    replacements = {
        "{{REPORT_LANGUAGE_RULE}}": profile.write_instruction,
        "{{CLOSING_LINE}}": profile.closing_line,
    }
    for token, value in replacements.items():
        text = text.replace(token, value)
    return text


def report_suffix(lang: str | None, extra: str | None = None) -> str | None:
    """Filename suffix: lang always, plus optional model tag."""
    code = normalize_lang(lang)
    parts = [code]
    if extra:
        parts.append(extra)
    return ".".join(parts)
