"""Cloudflare-aware Forex Factory fetch. Canonical: docs/scrape_strategy.md.

Egress (must work before any library helps):
- Historical HTML: Cloudflare WARP Traffic+DNS UDP, or FF_HTTP_PROXY (residential).
- VN home IP typically TLS-resets www.forexfactory.com — stealth browsers will not fix that.

What to fetch:
- This week: nfs.faireconomy.media weekly export (CSV/XML/JSON). No HTML, no WARP.
- Months: calendar HTML with impacts=3|2|1|0 (red|orange|yellow|gray/holiday), paced gap+jitter.

HTTP stack (strategy=auto / http):
1. curl_cffi + Firefox TLS impersonation + rotated headers (this is what YTD used).
2. cloudscraper — only if TLS still connects (JS challenge).
3. Playwright, then optional undetected-chromedriver (strategy=browser|stealth|auto).

Dated ff_calendar_MMDDYYYY.xml archives do not exist on the public CDN (404).
"""

from __future__ import annotations

import logging
import os
import random
import time
from pathlib import Path
from typing import Literal
from urllib.parse import urlparse

from scripts.extract.config import (
    BRONZE_RAW_CALENDAR_DIR,
    DEFAULT_IMPERSONATE,
    FETCH_JITTER_SECONDS,
    FF_BASE_URL,
    FF_CALENDAR_URL,
    FF_WEEKLY_EXPORT_BASE,
    FF_WEEKLY_EXPORT_FORMATS,
    IMPACT_FETCH_GAP_SECONDS,
    IMPACT_LAYERS,
    MAX_FETCH_RETRIES,
    PROXY_ENV_KEYS,
    RETRY_BACKOFF_SECONDS,
    USER_AGENTS,
)

logger = logging.getLogger(__name__)

FetchStrategy = Literal["http", "browser", "stealth", "auto"]

MONTH_NUM = {
    "jan": "01",
    "feb": "02",
    "mar": "03",
    "apr": "04",
    "may": "05",
    "jun": "06",
    "jul": "07",
    "aug": "08",
    "sep": "09",
    "oct": "10",
    "nov": "11",
    "dec": "12",
}


def build_calendar_url(period: str) -> str:
    period = period.strip()
    if period.startswith("http"):
        return period
    if len(period) == 10 and period[4] == "-" and period[7] == "-":
        return f"{FF_CALENDAR_URL}?day={period}"
    return f"{FF_CALENDAR_URL}?month={period}"


def build_impact_url(month_abbr: str, year: int, impact_id: int) -> str:
    """Print/permalink view filtered to one impact id (3=red, 2=orange, 1=yellow, 0=gray/holiday)."""
    month = month_abbr.lower()
    return (
        f"{FF_CALENDAR_URL}?month={month}.{year}"
        f"&permalink=true&impacts={impact_id}"
    )


def build_weekly_export_url(fmt: str = "csv") -> str:
    fmt = fmt.lower().lstrip(".")
    if fmt not in FF_WEEKLY_EXPORT_FORMATS:
        raise ValueError(f"fmt must be one of {FF_WEEKLY_EXPORT_FORMATS}")
    return f"{FF_WEEKLY_EXPORT_BASE}.{fmt}"


def human_delay(low: float | None = None, high: float | None = None) -> float:
    """Sleep a random interval; returns seconds slept."""
    lo = FETCH_JITTER_SECONDS[0] if low is None else low
    hi = FETCH_JITTER_SECONDS[1] if high is None else high
    if hi < lo:
        lo, hi = hi, lo
    seconds = random.uniform(lo, hi)
    time.sleep(seconds)
    return seconds


def _pick_user_agent() -> str:
    return random.choice(USER_AGENTS)


def _proxy_url() -> str | None:
    for key in PROXY_ENV_KEYS:
        value = os.environ.get(key, "").strip()
        if value:
            return value
    return None


def _proxies_dict() -> dict[str, str] | None:
    proxy = _proxy_url()
    if not proxy:
        return None
    return {"http": proxy, "https": proxy}


def _browser_headers(*, referer: str | None = None) -> dict[str, str]:
    ua = _pick_user_agent()
    headers = {
        "User-Agent": ua,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none" if not referer else "cross-site",
        "Sec-Fetch-User": "?1",
        "Priority": "u=0, i",
    }
    if referer:
        headers["Referer"] = referer
    if "Chrome" in ua:
        headers["Sec-Ch-Ua"] = '"Chromium";v="131", "Not_A Brand";v="24"'
        headers["Sec-Ch-Ua-Mobile"] = "?0"
        headers["Sec-Ch-Ua-Platform"] = '"macOS"'
    return headers


def _looks_blocked(text: str, status: int) -> bool:
    if status == 429:
        return True
    if status != 200:
        return True
    low = text.lower()
    if "just a moment" in low or "security verification" in low:
        return True
    if "performing security verification" in low:
        return True
    if "rate limited" in low and len(text) < 8000:
        return True
    # Accept HTML calendar, markdown print table, or weekly export payloads
    if "calendar__table" in text or "| Currency |" in text or "Currency" in text:
        return False
    if text.lstrip().startswith("{") or text.lstrip().startswith("["):
        return False
    if "<weeklyevents" in low or text.lstrip().startswith("Title,Country"):
        return False
    return len(text) < 1500


def fetch_with_curl_cffi(url: str) -> str:
    from curl_cffi import requests

    session = requests.Session()
    proxies = _proxies_dict()
    last_error: Exception | None = None

    for attempt in range(1, MAX_FETCH_RETRIES + 1):
        headers = _browser_headers(
            referer="https://www.google.com/" if attempt > 1 else None
        )
        try:
            if attempt == 1 and urlparse(url).netloc.endswith("forexfactory.com"):
                home = session.get(
                    FF_BASE_URL,
                    impersonate=DEFAULT_IMPERSONATE,
                    headers=headers,
                    proxies=proxies,
                    timeout=45,
                )
                if home.status_code != 200:
                    logger.warning("Homepage returned %s", home.status_code)
                human_delay()

            response = session.get(
                url,
                impersonate=DEFAULT_IMPERSONATE,
                headers=headers,
                proxies=proxies,
                timeout=60,
            )
            html = response.text
            if _looks_blocked(html, response.status_code):
                raise RuntimeError(
                    f"Blocked or empty response HTTP {response.status_code} for {url}"
                )
            return html
        except Exception as exc:  # noqa: BLE001
            last_error = exc
            logger.warning(
                "curl_cffi attempt %s/%s failed: %s",
                attempt,
                MAX_FETCH_RETRIES,
                exc,
            )
            if attempt < MAX_FETCH_RETRIES:
                time.sleep(RETRY_BACKOFF_SECONDS * attempt + random.uniform(0.5, 2.0))

    raise RuntimeError(
        f"curl_cffi fetch failed after {MAX_FETCH_RETRIES} attempts"
    ) from last_error


def fetch_with_cloudscraper(url: str) -> str:
    """Bypass Cloudflare JS challenges when TLS handshake still succeeds."""
    import cloudscraper

    scraper = cloudscraper.create_scraper(
        browser={"browser": "firefox", "platform": "darwin", "mobile": False}
    )
    proxies = _proxies_dict()
    last_error: Exception | None = None

    for attempt in range(1, MAX_FETCH_RETRIES + 1):
        headers = _browser_headers(referer="https://www.google.com/")
        try:
            response = scraper.get(
                url,
                headers=headers,
                proxies=proxies,
                timeout=60,
            )
            body = response.text
            if _looks_blocked(body, response.status_code):
                raise RuntimeError(
                    f"cloudscraper blocked HTTP {response.status_code} for {url}"
                )
            return body
        except Exception as exc:  # noqa: BLE001
            last_error = exc
            logger.warning(
                "cloudscraper attempt %s/%s failed: %s",
                attempt,
                MAX_FETCH_RETRIES,
                exc,
            )
            if attempt < MAX_FETCH_RETRIES:
                human_delay(RETRY_BACKOFF_SECONDS * attempt, RETRY_BACKOFF_SECONDS * attempt + 3)

    raise RuntimeError(
        f"cloudscraper fetch failed after {MAX_FETCH_RETRIES} attempts"
    ) from last_error


def fetch_with_playwright(url: str) -> str:
    from playwright.sync_api import sync_playwright

    launch_args = ["--disable-blink-features=AutomationControlled", "--no-sandbox"]
    user_agent = _pick_user_agent()
    proxy = _proxy_url()

    with sync_playwright() as playwright:
        browser = None
        for channel in ("chrome", None):
            try:
                launch_kwargs: dict = {"headless": True, "args": launch_args}
                if channel:
                    launch_kwargs["channel"] = channel
                if proxy:
                    launch_kwargs["proxy"] = {"server": proxy}
                browser = playwright.chromium.launch(**launch_kwargs)
                break
            except Exception as exc:  # noqa: BLE001
                logger.warning("Playwright launch channel=%s failed: %s", channel, exc)

        if browser is None:
            raise RuntimeError("Could not launch Playwright browser.")

        try:
            context = browser.new_context(user_agent=user_agent, locale="en-US")
            page = context.new_page()
            page.goto(url, wait_until="domcontentloaded", timeout=90000)
            page.wait_for_selector(".calendar__table", timeout=45000)
            human_delay(1.0, 2.5)
            html = page.content()
            if _looks_blocked(html, 200):
                raise RuntimeError("Playwright got challenge/empty calendar page.")
            return html
        finally:
            browser.close()


def fetch_with_undetected_chrome(url: str) -> str:
    """Last-resort headed/headless Chrome that strips common automation markers.

    Requires optional dependency ``undetected-chromedriver``.
    Useless if the current egress IP is already TLS-reset by Cloudflare —
    pair with a residential proxy (system proxy / Chrome flags) in that case.
    """
    try:
        import undetected_chromedriver as uc
    except ImportError as exc:
        raise RuntimeError(
            "undetected-chromedriver not installed; pip install undetected-chromedriver"
        ) from exc

    options = uc.ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    # Prefer headless-new when available; fall back gracefully
    options.add_argument("--headless=new")

    driver = uc.Chrome(options=options)
    try:
        driver.set_page_load_timeout(90)
        driver.get(url)
        human_delay(2.0, 4.0)
        html = driver.page_source
        if _looks_blocked(html, 200):
            raise RuntimeError("undetected-chromedriver got challenge/empty page.")
        return html
    finally:
        driver.quit()


def fetch_calendar_html(url: str, strategy: FetchStrategy = "auto") -> tuple[str, str]:
    """Fetch calendar HTML/markdown body. Returns (body, method_used)."""
    errors: list[str] = []

    def _try(name: str, fn) -> tuple[str, str] | None:
        try:
            return fn(url), name
        except Exception as exc:  # noqa: BLE001
            msg = f"{name}: {exc}"
            errors.append(msg)
            logger.warning("%s", msg)
            return None

    if strategy == "http":
        for name, fn in (
            ("curl_cffi", fetch_with_curl_cffi),
            ("cloudscraper", fetch_with_cloudscraper),
        ):
            got = _try(name, fn)
            if got:
                return got
        raise RuntimeError("HTTP strategies failed: " + " | ".join(errors))

    if strategy == "browser":
        got = _try("playwright", fetch_with_playwright)
        if got:
            return got
        raise RuntimeError("browser strategy failed: " + " | ".join(errors))

    if strategy == "stealth":
        got = _try("undetected_chrome", fetch_with_undetected_chrome)
        if got:
            return got
        raise RuntimeError("stealth strategy failed: " + " | ".join(errors))

    # auto: try all layers in order
    for name, fn in (
        ("curl_cffi", fetch_with_curl_cffi),
        ("cloudscraper", fetch_with_cloudscraper),
        ("playwright", fetch_with_playwright),
        ("undetected_chrome", fetch_with_undetected_chrome),
    ):
        got = _try(name, fn)
        if got:
            return got

    raise RuntimeError(
        "All fetch strategies failed (TLS block / CF challenge / missing deps). "
        "Use FF_HTTP_PROXY (residential) or save dumps manually, then "
        "build_month_from_markdown.py. Details: "
        + " | ".join(errors)
    )


def fetch_weekly_export(fmt: str = "csv", *, fallback: bool = True) -> tuple[str, str]:
    """Fetch this-week export. Prefer CSV (stable); optionally fall back across formats."""
    preferred = [fmt.lower()]
    if fallback:
        preferred += [f for f in FF_WEEKLY_EXPORT_FORMATS if f != fmt.lower()]
    last_error: Exception | None = None
    for candidate in preferred:
        url = build_weekly_export_url(candidate)
        try:
            # Soft pacing — feed is rate-limited (~2 / 5 min)
            human_delay(1.0, 2.0)
            body, method = fetch_calendar_html(url, strategy="http")
            return body, f"{method}:{candidate}"
        except Exception as exc:  # noqa: BLE001
            last_error = exc
            logger.warning("Weekly export %s failed: %s", candidate, exc)
    raise RuntimeError("Weekly export fetch failed") from last_error


def fetch_month_impact_layers(
    month_abbr: str,
    year: int,
    *,
    out_dir: Path | None = None,
    gap_seconds: int = IMPACT_FETCH_GAP_SECONDS,
    strategy: FetchStrategy = "auto",
    stop_on_fail: bool = True,
) -> dict[str, Path]:
    """Fetch red/orange/yellow/gray (holiday) dumps for one month with pacing.

    Returns map impact_label → saved raw file path.
    """
    month_abbr = month_abbr.lower()
    month_num = MONTH_NUM[month_abbr]
    out_dir = out_dir or (BRONZE_RAW_CALENDAR_DIR / str(year))
    out_dir.mkdir(parents=True, exist_ok=True)

    saved: dict[str, Path] = {}
    for idx, (label, impact_id) in enumerate(IMPACT_LAYERS):
        if idx > 0 and gap_seconds > 0:
            jitter = human_delay(0.0, FETCH_JITTER_SECONDS[1])
            logger.info(
                "Cloudflare pacing: sleep %ss (+%.1fs jitter) before %s",
                gap_seconds,
                jitter,
                label,
            )
            time.sleep(gap_seconds)

        url = build_impact_url(month_abbr, year, impact_id)
        logger.info("Fetching %s", url)
        try:
            body, method = fetch_calendar_html(url, strategy=strategy)
            ext = (
                ".html"
                if body.lstrip().lower().startswith("<!doctype")
                or body.lstrip().lower().startswith("<html")
                or "calendar__table" in body
                else ".md"
            )
            dest = out_dir / f"{month_num}_{label}{ext}"
            # Drop stale sibling extension if re-fetching
            for stale in out_dir.glob(f"{month_num}_{label}.*"):
                if stale != dest:
                    stale.unlink(missing_ok=True)
            dest.write_text(body)
            saved[label] = dest
            logger.info("Saved %s via %s (%s bytes)", dest.name, method, len(body))
        except Exception as exc:  # noqa: BLE001
            logger.error("Failed %s/%s: %s", month_abbr, label, exc)
            if stop_on_fail:
                break

    return saved
