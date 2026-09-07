"""Coalesce upsert of calendar events into monthly Silver partitions.

`actual` is a late-arriving measure: an event is published with an empty actual
and only gets a value after the release. A write must therefore never let an
empty value overwrite a stored one, and partitions are keyed by ``event_date``
(business time) rather than by the run that produced them.
"""

from __future__ import annotations

import hashlib
import logging
import os
import sys
from collections.abc import Iterable
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.extract.config import (
    SILVER_CHANGES_COLUMNS,
    SILVER_CHANGES_DIR,
    SILVER_COLUMNS,
    SILVER_EVENTS_DIR,
)

logger = logging.getLogger(__name__)

# Row identity is the absolute release instant, not the published clock: the
# this-week export publishes US Eastern while the monthly HTML dump publishes the
# scraping account's timezone (Asia/Novosibirsk in this repo). Keying on
# ``time_raw`` matches 0 rows across the two sources; keying on the instant
# matches 91 of 92. ``time_raw`` only identifies untimed rows ("All Day",
# "Tentative", "Sep Data"), which carry no instant at all.
IDENTITY_FIELDS = ("event_datetime_utc", "currency", "event")
UNTIMED_IDENTITY_FIELDS = ("event_date", "time_raw", "currency", "event")

# Deterministic file ordering; not an identity.
BUSINESS_KEY = ("event_date", "time_raw", "currency", "event")

# Measures and classification a later scrape may fill in or revise.
# ``time_raw``/``source_timezone``/``event_datetime_hcm`` are deliberately NOT
# mutable: time_raw is only meaningful together with its source_timezone, so
# letting one source overwrite it would make the row internally inconsistent.
MUTABLE_FIELDS = ("impact", "actual", "forecast", "previous")

MODES = ("merge", "refresh")


def utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _utc_minute(value: object) -> str:
    """Normalise an ISO instant to ``YYYY-MM-DDTHH:MMZ`` so formats cannot drift."""
    text = _norm(value)
    if not text:
        return ""
    parsed = pd.to_datetime(text, errors="coerce", utc=True)
    if pd.isna(parsed):
        return ""
    return parsed.strftime("%Y-%m-%dT%H:%MZ")


def event_uid(
    *,
    event_date: object = "",
    event_datetime_utc: object = "",
    currency: object = "",
    event: object = "",
    time_raw: object = "",
) -> str:
    """Stable id for one release occurrence.

    Hex digits never contain ``%``, ``K``, ``M`` or ``bp``, so these ids stay
    inert to the numeric checks in ``report_lint``.
    """
    instant = _utc_minute(event_datetime_utc)
    if instant:
        parts = ("i", instant, _norm(currency).upper(), _norm(event))
    else:
        parts = (
            "u",
            _norm(event_date),
            _norm(time_raw).lower(),
            _norm(currency).upper(),
            _norm(event),
        )
    digest = hashlib.sha1("|".join(parts).encode()).hexdigest()  # noqa: S324 - id, not crypto
    return digest[:16]


def add_event_uid(frame: pd.DataFrame) -> pd.DataFrame:
    """(Re)derive ``event_uid`` so it can never drift from the row's identity."""
    out = frame.copy()
    out["event_uid"] = [
        event_uid(
            event_date=row["event_date"],
            event_datetime_utc=row["event_datetime_utc"],
            currency=row["currency"],
            event=row["event"],
            time_raw=row["time_raw"],
        )
        for _, row in out.iterrows()
    ]
    return out


def partition_of(event_date: object) -> str:
    """``2026-09-04`` → ``2026_09``."""
    return str(event_date)[:7].replace("-", "_")


def _norm(value: object) -> str:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return ""
    return str(value).strip()


def read_partition(path: Path) -> pd.DataFrame:
    """Read a silver partition, tolerating partitions written before uid/first_seen_at."""
    if not Path(path).exists():
        return pd.DataFrame(columns=SILVER_COLUMNS)
    frame = pd.read_csv(path, dtype=str).fillna("")
    for column in SILVER_COLUMNS:
        if column not in frame.columns:
            frame[column] = ""
    blank_seen = frame["first_seen_at"].map(_norm) == ""
    frame.loc[blank_seen, "first_seen_at"] = frame.loc[blank_seen, "updated_at"]
    frame = add_event_uid(frame)
    return frame[list(SILVER_COLUMNS)]


def _atomic_write(frame: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    frame.to_csv(tmp, index=False)
    os.replace(tmp, path)


def _change(
    *,
    changed_at: str,
    source: str,
    change_type: str,
    row: dict,
    field: str = "",
    old_value: str = "",
    new_value: str = "",
) -> dict:
    return {
        "changed_at": changed_at,
        "source": source,
        "change_type": change_type,
        "event_uid": row["event_uid"],
        "event_date": row["event_date"],
        "currency": row["currency"],
        "event": row["event"],
        "field": field,
        "old_value": old_value,
        "new_value": new_value,
    }


def _coalesce(old: dict, new: dict) -> tuple[dict, list[tuple[str, str, str]]]:
    """Merge `new` onto `old`. An empty incoming value never wins."""
    merged = dict(old)
    deltas: list[tuple[str, str, str]] = []
    for field in MUTABLE_FIELDS:
        incoming = _norm(new.get(field))
        stored = _norm(old.get(field))
        if not incoming or incoming == stored:
            continue
        merged[field] = incoming
        deltas.append((field, stored, incoming))
    return merged, deltas


def _append_changes(changes_dir: Path, part: str, rows: list[dict]) -> Path | None:
    if not rows:
        return None
    changes_dir.mkdir(parents=True, exist_ok=True)
    path = changes_dir / f"{part}.csv"
    frame = pd.DataFrame(rows, columns=SILVER_CHANGES_COLUMNS)
    frame.to_csv(path, mode="a", header=not path.exists(), index=False)
    return path


def _prepare(new_rows: pd.DataFrame) -> pd.DataFrame:
    frame = new_rows.copy()
    for column in SILVER_COLUMNS:
        if column not in frame.columns:
            frame[column] = ""
    frame = frame[list(SILVER_COLUMNS)].astype(str)
    for column in SILVER_COLUMNS:
        frame[column] = frame[column].map(_norm)
    frame = frame[frame["event_date"] != ""]
    return add_event_uid(frame)


def upsert_silver(
    new_rows: pd.DataFrame,
    *,
    mode: str = "merge",
    source: str = "unknown",
    delete_missing: bool = False,
    scope_impacts: Iterable[str] | None = None,
    silver_dir: Path | str = SILVER_EVENTS_DIR,
    changes_dir: Path | str = SILVER_CHANGES_DIR,
    now: str | None = None,
) -> dict:
    """Upsert silver rows into ``YYYY_MM.csv`` partitions, coalescing measures.

    ``mode="merge"`` (weekly feed) covers one week of a wider partition, so it
    only inserts and coalesces. ``mode="refresh"`` (monthly HTML dump) covers a
    whole month and may additionally prune.

    Pruning is opt-in via ``delete_missing`` because a dump is only authoritative
    as of the moment it was captured: an older dump replayed today would
    otherwise delete rows a newer source has since added. When pruning is on it
    is limited to ``scope_impacts`` — the impact layers the dump actually carried
    — so a gray holiday row survives a red/orange/yellow refresh.
    """
    if mode not in MODES:
        raise ValueError(f"mode must be one of {MODES}, got {mode!r}")
    if delete_missing and mode != "refresh":
        raise ValueError("delete_missing requires mode='refresh'")

    silver_dir = Path(silver_dir)
    changes_dir = Path(changes_dir)
    stamp = now or utc_stamp()
    incoming = _prepare(new_rows)

    if scope_impacts is None:
        scope = {_norm(v).lower() for v in incoming["impact"].unique() if _norm(v)}
    else:
        scope = {_norm(v).lower() for v in scope_impacts if _norm(v)}

    partitions: dict[str, str] = {}
    totals = {"inserted": 0, "updated": 0, "deleted": 0, "unchanged": 0}
    change_paths: list[str] = []

    for part, month_rows in incoming.groupby(incoming["event_date"].map(partition_of), sort=True):
        path = silver_dir / f"{part}.csv"
        existing = read_partition(path)

        old_by_uid = {row["event_uid"]: row for row in existing.to_dict("records")}
        new_by_uid = {
            row["event_uid"]: row
            for row in month_rows.drop_duplicates(subset=["event_uid"], keep="last").to_dict("records")
        }

        kept: list[dict] = []
        changes: list[dict] = []

        for uid, old in old_by_uid.items():
            new = new_by_uid.get(uid)
            if new is None:
                if delete_missing and _norm(old.get("impact")).lower() in scope:
                    totals["deleted"] += 1
                    changes.append(
                        _change(
                            changed_at=stamp,
                            source=source,
                            change_type="delete",
                            row=old,
                        )
                    )
                    continue
                kept.append(old)
                continue

            merged, deltas = _coalesce(old, new)
            if deltas:
                merged["updated_at"] = stamp
                totals["updated"] += 1
                for field, old_value, new_value in deltas:
                    changes.append(
                        _change(
                            changed_at=stamp,
                            source=source,
                            change_type="update",
                            row=merged,
                            field=field,
                            old_value=old_value,
                            new_value=new_value,
                        )
                    )
            else:
                totals["unchanged"] += 1
            kept.append(merged)

        for uid, new in new_by_uid.items():
            if uid in old_by_uid:
                continue
            row = dict(new)
            row["first_seen_at"] = row.get("first_seen_at") or stamp
            row["updated_at"] = row.get("updated_at") or stamp
            totals["inserted"] += 1
            changes.append(
                _change(
                    changed_at=stamp,
                    source=source,
                    change_type="insert",
                    row=row,
                )
            )
            kept.append(row)

        out = pd.DataFrame(kept, columns=SILVER_COLUMNS).sort_values(list(BUSINESS_KEY))
        _atomic_write(out, path)
        partitions[part] = str(path)

        change_path = _append_changes(changes_dir, part, changes)
        if change_path:
            change_paths.append(str(change_path))

        logger.info(
            "Silver upsert %s (%s): %s rows, +%s ~%s -%s",
            path.name,
            mode,
            len(out),
            sum(1 for c in changes if c["change_type"] == "insert"),
            sum(1 for c in changes if c["change_type"] == "update"),
            sum(1 for c in changes if c["change_type"] == "delete"),
        )

    return {
        "mode": mode,
        "source": source,
        "delete_missing": delete_missing,
        "partitions": partitions,
        "changes": change_paths,
        **totals,
    }
