"""Model-agnostic LLM client: OpenRouter and Google AI Studio."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"

# Weekly outlook: pick from the free shortlist (DeepSeek :free is gone).
PREFERRED_OPENROUTER_MODELS = (
    "inclusionai/ling-3.0-flash-fin:free",
    "minimax/minimax-m3:free",
)
DEFAULT_OPENROUTER_MODEL = PREFERRED_OPENROUTER_MODELS[0]  # used when .env has no model


class LLMError(RuntimeError):
    pass


def load_dotenv(path: Path | None = None) -> None:
    env_path = path or (REPO_ROOT / ".env")
    if not env_path.exists():
        return
    for raw in env_path.read_text().splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key, value = key.strip(), value.strip().strip("'").strip('"')
        if key and key not in os.environ:
            os.environ[key] = value


def _http_json(url: str, payload: dict, headers: dict, timeout: int) -> dict:
    body = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(url, data=body, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise LLMError(f"HTTP {exc.code} from {url}: {detail[:800]}") from exc
    except urllib.error.URLError as exc:
        raise LLMError(f"Network error calling {url}: {exc}") from exc


def complete_openrouter(
    system: str,
    user: str,
    model: str,
    api_key: str,
    timeout: int = 180,
) -> str:
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "temperature": 0.2,
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/datpro12345/ff-transform-data",
        "X-Title": "ff-transform-data weekly analyst",
    }
    data = _http_json(OPENROUTER_URL, payload, headers, timeout)
    try:
        return data["choices"][0]["message"]["content"].strip()
    except (KeyError, IndexError, TypeError) as exc:
        raise LLMError(f"Unexpected OpenRouter response: {data!r}"[:800]) from exc


def complete_google(
    system: str,
    user: str,
    model: str,
    api_key: str,
    timeout: int = 180,
) -> str:
    url = GEMINI_URL.format(model=model) + f"?key={api_key}"
    payload = {
        "systemInstruction": {"parts": [{"text": system}]},
        "contents": [{"role": "user", "parts": [{"text": user}]}],
        "generationConfig": {"temperature": 0.2},
    }
    headers = {"Content-Type": "application/json"}
    data = _http_json(url, payload, headers, timeout)
    try:
        return data["candidates"][0]["content"]["parts"][0]["text"].strip()
    except (KeyError, IndexError, TypeError) as exc:
        raise LLMError(f"Unexpected Gemini response: {data!r}"[:800]) from exc


def complete(
    system: str,
    user: str,
    provider: str | None = None,
    model: str | None = None,
    timeout: int = 180,
) -> tuple[str, str, str]:
    """Return (text, provider, model). Provider/model fall back to env."""
    load_dotenv()
    chosen = (provider or os.environ.get("LLM_PROVIDER") or "openrouter").strip().lower()
    if chosen == "openrouter":
        api_key = os.environ.get("OPENROUTER_API_KEY", "").strip()
        if not api_key or api_key.startswith("your_"):
            raise LLMError("OPENROUTER_API_KEY is missing in .env")
        env_model = (os.environ.get("OPENROUTER_MODEL") or "").strip()
        if model:
            candidates = [model]
        elif env_model:
            candidates = [env_model] + [m for m in PREFERRED_OPENROUTER_MODELS if m != env_model]
        else:
            candidates = list(PREFERRED_OPENROUTER_MODELS)
        last_error: LLMError | None = None
        for used_model in candidates:
            try:
                text = complete_openrouter(system, user, used_model, api_key, timeout)
                return text, chosen, used_model
            except LLMError as exc:
                last_error = exc
                if "404" not in str(exc) or used_model == candidates[-1]:
                    raise
        raise last_error or LLMError("OpenRouter complete failed")
    if chosen in {"google", "gemini"}:
        api_key = os.environ.get("GEMINI_API_KEY", "").strip()
        if not api_key or api_key.startswith("your_"):
            raise LLMError("GEMINI_API_KEY is missing in .env")
        used_model = model or os.environ.get("GEMINI_MODEL") or "gemini-2.5-flash"
        return complete_google(system, user, used_model, api_key, timeout), chosen, used_model
    raise LLMError(f"Unknown LLM_PROVIDER={chosen!r} (use openrouter or google)")
