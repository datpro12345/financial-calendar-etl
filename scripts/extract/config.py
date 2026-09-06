from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

# Medallion paths (see docs/architecture.md)
BRONZE_RAW_CALENDAR_DIR = REPO_ROOT / "data" / "bronze" / "raw" / "calendar"
BRONZE_LANDING_DIR = REPO_ROOT / "data" / "bronze" / "landing" / "calendar_events"
SILVER_EVENTS_DIR = REPO_ROOT / "data" / "silver" / "calendar_events"
GOLD_GCAL_DIR = REPO_ROOT / "data" / "gold" / "google_calendar"
GOLD_MART_DIR = REPO_ROOT / "data" / "gold" / "mart"

# Legacy paths (pre-medallion; do not write new files here)
LEGACY_BRONZE_MONTHLY_DIR = REPO_ROOT / "data" / "bronze" / "monthly"
LEGACY_SILVER_MONTHLY_DIR = REPO_ROOT / "data" / "silver" / "monthly"

# Back-compat aliases used by older scripts
BRONZE_MONTHLY_DIR = LEGACY_BRONZE_MONTHLY_DIR
BRONZE_WEEKLY_DIR = REPO_ROOT / "data" / "bronze" / "weekly"

BRONZE_LANDING_COLUMNS = [
    "date",
    "time",
    "currency",
    "impact",
    "event",
    "actual",
    "forecast",
    "previous",
    "source_file",
    "ingested_at",
]

# Legacy 8-col bronze (parsed only)
BRONZE_COLUMNS = [
    "date",
    "time",
    "currency",
    "impact",
    "event",
    "actual",
    "forecast",
    "previous",
]

SILVER_COLUMNS = [
    "event_date",
    "time_raw",
    "event_datetime_utc",
    "event_datetime_hcm",
    "currency",
    "impact",
    "event",
    "actual",
    "forecast",
    "previous",
    "source_timezone",
    "updated_at",
]

ALLOWED_CURRENCIES = frozenset(
    {"AUD", "CAD", "CHF", "CNY", "EUR", "GBP", "JPY", "NZD", "USD"}
)

IMPACT_CLASS_MAP = {
    "icon icon--ff-impact-yel": "yellow",
    "icon icon--ff-impact-ora": "orange",
    "icon icon--ff-impact-red": "red",
    "icon icon--ff-impact-gra": "gray",
}

FF_BASE_URL = "https://www.forexfactory.com"
FF_CALENDAR_URL = f"{FF_BASE_URL}/calendar"

# Official-ish weekly feed (this week only; rate-limited ~2 req / 5 min).
# Prefer this over HTML scrape for the current week.
FF_WEEKLY_EXPORT_BASE = "https://nfs.faireconomy.media/ff_calendar_thisweek"
FF_WEEKLY_EXPORT_FORMATS = ("csv", "xml", "json")

DEFAULT_IMPERSONATE = "firefox135"
MAX_FETCH_RETRIES = 5
RETRY_BACKOFF_SECONDS = 3

# Cloudflare-safe pacing between impact-layer fetches
IMPACT_FETCH_GAP_SECONDS = 45
# Random human-like delay range (seconds) applied around paced gaps
FETCH_JITTER_SECONDS = (2.0, 5.0)

# Optional egress when WARP is off: residential proxy URL.
# WARP Traffic+DNS (UDP) is the proven path for historical HTML (see docs/scrape_strategy.md).
PROXY_ENV_KEYS = ("FF_HTTP_PROXY", "HTTPS_PROXY", "HTTP_PROXY")

# Rotating browser-like User-Agents (used by cloudscraper / header builds)
USER_AGENTS = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:135.0) Gecko/20100101 Firefox/135.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:134.0) Gecko/20100101 Firefox/134.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36",
)

# FF impact filter IDs → bronze impact label
# https://www.forexfactory.com/calendar?...&impacts=3,2,1,0
# 0 = holiday / non-economic (bank holidays, session closures). Required for
# liquidity: a closed cash session thins FX even when no red print is scheduled.
IMPACT_LAYERS = (
    ("red", 3),
    ("orange", 2),
    ("yellow", 1),
    ("gray", 0),
)
