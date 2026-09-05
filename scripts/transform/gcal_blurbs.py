"""Load short Vietnamese GCal blurbs from YAML. No LLM."""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_BLURBS = REPO_ROOT / "docs" / "analyst" / "semantics" / "gcal_red.yml"
DEFAULT_FALLBACK = "Tin red {currency}. Đứng ngoài lệnh mới quanh giờ này."


def load_blurbs(path: Path | None = None) -> tuple[str, list[tuple[str, str]]]:
    text = (path or DEFAULT_BLURBS).read_text()
    fallback = DEFAULT_FALLBACK
    items: list[tuple[str, str]] = []
    current_match: str | None = None
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("fallback:"):
            fallback = line.split(":", 1)[1].strip().strip('"').strip("'")
            continue
        if line.startswith("- match:"):
            current_match = line.split(":", 1)[1].strip().strip('"').strip("'")
            continue
        if current_match and line.startswith("text:"):
            blurb = line.split(":", 1)[1].strip().strip('"').strip("'")
            items.append((current_match, blurb))
            current_match = None
    items.sort(key=lambda pair: len(pair[0]), reverse=True)
    return fallback, items


def blurb_for(event: str, currency: str, path: Path | None = None) -> str:
    fallback, items = load_blurbs(path)
    name = (event or "").strip()
    low = name.lower()
    for match, text in items:
        if match.lower() in low:
            return text
    return fallback.format(currency=(currency or "?").upper(), event=name)


def format_gcal_description(
    *,
    event: str,
    currency: str,
    forecast: str = "",
    previous: str = "",
    actual: str = "",
    path: Path | None = None,
) -> str:
    def cell(value: str) -> str:
        text = (value or "").strip()
        if not text or text.upper() in {"N/A", "NA", "NONE", "NULL"}:
            return "—"
        return text

    blurb = blurb_for(event, currency, path)
    return (
        f"{blurb}\n"
        f"F {cell(forecast)} · P {cell(previous)} · A {cell(actual)}\n"
        "Đứng ngoài lệnh mới quanh cửa sổ red. Asia/Ho_Chi_Minh"
    )
