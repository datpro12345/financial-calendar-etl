"""Silver calendar_events → simple Kimball star (Gold mart)."""

from __future__ import annotations

import argparse
import logging
import re
import sys
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.extract.config import GOLD_MART_DIR, SILVER_EVENTS_DIR

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

IMPACT_RANK = {"gray": 0, "yellow": 1, "orange": 2, "red": 3}


WEEKLY_SILVER_NAME = re.compile(r"^\d{4}_W\d{2}\.csv$")


def _load_silver(silver_dir: Path, pattern: str = "*.csv") -> pd.DataFrame:
    files = sorted(silver_dir.glob(pattern))
    if not files:
        raise FileNotFoundError(f"No silver files in {silver_dir}")
    weekly = [path for path in files if WEEKLY_SILVER_NAME.match(path.name)]
    monthly = [path for path in files if path not in weekly]
    frames = [pd.read_csv(path, dtype=str).fillna("") for path in monthly]
    if weekly:
        weekly_df = pd.concat(
            [pd.read_csv(path, dtype=str).fillna("") for path in weekly],
            ignore_index=True,
        )
        owned_dates = set(weekly_df["event_date"].astype(str))
        if frames:
            monthly_df = pd.concat(frames, ignore_index=True)
            monthly_df = monthly_df[~monthly_df["event_date"].astype(str).isin(owned_dates)]
            df = pd.concat([monthly_df, weekly_df], ignore_index=True)
        else:
            df = weekly_df
        logger.info(
            "Weekly silver owns %s dates (%s rows); monthly remainder %s rows",
            len(owned_dates),
            len(weekly_df),
            len(df) - len(weekly_df),
        )
    else:
        df = pd.concat(frames, ignore_index=True)
    return df.drop_duplicates(
        subset=["event_date", "time_raw", "currency", "event"],
        keep="last",
    )


def _build_dim_date(event_dates: pd.Series) -> pd.DataFrame:
    dates = (
        pd.to_datetime(event_dates, errors="coerce")
        .dropna()
        .drop_duplicates()
        .sort_values()
    )
    rows = []
    for ts in dates:
        rows.append(
            {
                "date_key": int(ts.strftime("%Y%m%d")),
                "event_date": ts.strftime("%Y-%m-%d"),
                "year": ts.year,
                "quarter": ts.quarter,
                "month": ts.month,
                "month_name": ts.strftime("%B"),
                "day": ts.day,
                "iso_week": int(ts.strftime("%V")),
                "weekday": ts.weekday(),  # Mon=0
                "weekday_name": ts.strftime("%A"),
                "is_weekend": int(ts.weekday() >= 5),
            }
        )
    return pd.DataFrame(rows)


def _build_dim_currency(codes: pd.Series) -> pd.DataFrame:
    uniq = sorted({c.strip().upper() for c in codes if str(c).strip()})
    return pd.DataFrame(
        {
            "currency_key": range(1, len(uniq) + 1),
            "currency_code": uniq,
        }
    )


def _build_dim_impact(codes: pd.Series) -> pd.DataFrame:
    uniq = sorted({c.strip().lower() for c in codes if str(c).strip()})
    # stable preferred order
    preferred = ["gray", "yellow", "orange", "red"]
    ordered = [c for c in preferred if c in uniq] + [c for c in uniq if c not in preferred]
    return pd.DataFrame(
        {
            "impact_key": range(1, len(ordered) + 1),
            "impact_code": ordered,
            "impact_rank": [IMPACT_RANK.get(c, -1) for c in ordered],
        }
    )


def _build_dim_event(names: pd.Series) -> pd.DataFrame:
    uniq = sorted({n.strip() for n in names if str(n).strip()})
    return pd.DataFrame(
        {
            "event_key": range(1, len(uniq) + 1),
            "event_name": uniq,
        }
    )


def silver_to_kimball(
    silver_dir: Path | str = SILVER_EVENTS_DIR,
    out_dir: Path | str = GOLD_MART_DIR,
    pattern: str = "*.csv",
) -> dict[str, Path]:
    silver_dir = Path(silver_dir)
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    silver = _load_silver(silver_dir, pattern=pattern)
    logger.info("Loaded %s silver rows from %s", len(silver), silver_dir)

    dim_date = _build_dim_date(silver["event_date"])
    dim_currency = _build_dim_currency(silver["currency"])
    dim_impact = _build_dim_impact(silver["impact"])
    dim_event = _build_dim_event(silver["event"])

    fact = silver.copy()
    fact["date_key"] = pd.to_datetime(fact["event_date"], errors="coerce").dt.strftime("%Y%m%d")
    fact["date_key"] = pd.to_numeric(fact["date_key"], errors="coerce").astype("Int64")
    fact["currency"] = fact["currency"].str.strip().str.upper()
    fact["impact"] = fact["impact"].str.strip().str.lower()
    fact["event"] = fact["event"].str.strip()

    fact = fact.merge(dim_currency, left_on="currency", right_on="currency_code", how="left")
    fact = fact.merge(dim_impact, left_on="impact", right_on="impact_code", how="left")
    fact = fact.merge(dim_event, left_on="event", right_on="event_name", how="left")

    fact_out = pd.DataFrame(
        {
            "fact_id": range(1, len(fact) + 1),
            "date_key": fact["date_key"],
            "currency_key": fact["currency_key"],
            "impact_key": fact["impact_key"],
            "event_key": fact["event_key"],
            "time_raw": fact["time_raw"],
            "event_datetime_utc": fact["event_datetime_utc"],
            "event_datetime_hcm": fact["event_datetime_hcm"],
            "actual_txt": fact["actual"],
            "forecast_txt": fact["forecast"],
            "previous_txt": fact["previous"],
            "source_timezone": fact["source_timezone"],
            "updated_at": fact["updated_at"],
        }
    )

    paths = {
        "dim_date": out_dir / "dim_date.csv",
        "dim_currency": out_dir / "dim_currency.csv",
        "dim_impact": out_dir / "dim_impact.csv",
        "dim_event": out_dir / "dim_event.csv",
        "fact_calendar_release": out_dir / "fact_calendar_release.csv",
    }
    dim_date.to_csv(paths["dim_date"], index=False)
    dim_currency.to_csv(paths["dim_currency"], index=False)
    dim_impact.to_csv(paths["dim_impact"], index=False)
    dim_event.to_csv(paths["dim_event"], index=False)
    fact_out.to_csv(paths["fact_calendar_release"], index=False)

    for name, path in paths.items():
        logger.info("Wrote %s (%s rows)", path.name, sum(1 for _ in open(path)) - 1)

    return paths


def main() -> int:
    parser = argparse.ArgumentParser(description="Build simple Kimball mart from silver")
    parser.add_argument("--silver-dir", default=str(SILVER_EVENTS_DIR))
    parser.add_argument("--out-dir", default=str(GOLD_MART_DIR))
    parser.add_argument("--pattern", default="*.csv")
    args = parser.parse_args()

    try:
        paths = silver_to_kimball(args.silver_dir, args.out_dir, args.pattern)
    except Exception as exc:  # noqa: BLE001
        logger.error("Kimball build failed: %s", exc)
        return 1

    print("OK")
    for name, path in paths.items():
        print(f"  {name}: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
