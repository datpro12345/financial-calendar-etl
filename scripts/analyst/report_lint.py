"""Deterministic lint: report numbers and fact_ids must exist in the Fact Pack."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

PRIMARY_PAIRS = (
    "EUR/USD",
    "GBP/USD",
    "USD/JPY",
    "EUR/GBP",
    "EUR/JPY",
    "GBP/JPY",
)

STRUCTURAL_TIMES = frozenset(
    {"06:00", "12:00", "13:00", "18:00", "18:30", "23:00", "23:59", "00:00"}
)
STRUCTURAL_INTS = frozenset(range(0, 24)) | {30, 36, 37, 2026}

UNIT_RE = re.compile(
    r"(?<![\w.])(-?\d+(?:[.,]\d+)?)\s*(%|[Bb][Pp]\b|[KkMm](?![A-Za-zÀ-ỹ]))"
)
TIME_RE = re.compile(r"\b(\d{1,2}:\d{2})\b")
FACT_RE = re.compile(r"fact_id\s*=\s*(\d+)", re.I)
PRICE_RE = re.compile(r"\b(1\.\d{2,5})\b")
BARE_DEC_RE = re.compile(r"(?<![\w.:])(-?\d+[.,]\d{1,2})(?!\d)")

BANNED_ENTRY = (
    re.compile(r"\bLong\s+(EUR|USD|GBP|JPY|EUR/USD|GBP/USD|USD/JPY)", re.I),
    re.compile(r"\bShort\s+(EUR|USD|GBP|JPY|EUR/USD|GBP/USD|USD/JPY)", re.I),
    re.compile(r"target\s+\d", re.I),
    re.compile(r"\bentry\b", re.I),
    re.compile(r"USD売り"),
)


def _norm_num(raw: str) -> str:
    return raw.replace(",", ".").strip()


def _walk_strings(obj: Any) -> list[str]:
    out: list[str] = []
    if obj is None:
        return out
    if isinstance(obj, dict):
        for v in obj.values():
            out.extend(_walk_strings(v))
    elif isinstance(obj, list):
        for v in obj:
            out.extend(_walk_strings(v))
    elif isinstance(obj, bool):
        return out
    elif isinstance(obj, (int, float)):
        out.append(str(obj))
    else:
        text = str(obj).strip()
        if text:
            out.append(text)
    return out


def allowed_from_pack(pack: dict[str, Any]) -> dict[str, set[str]]:
    blobs = _walk_strings(pack)
    units: set[str] = set()
    times: set[str] = set(STRUCTURAL_TIMES)
    facts: set[str] = set()
    prices: set[str] = set()
    decimals: set[str] = set()

    for blob in blobs:
        for match in UNIT_RE.finditer(blob):
            units.add(_norm_num(match.group(1)) + match.group(2).upper())
        for match in TIME_RE.finditer(blob):
            h, m = match.group(1).split(":")
            times.add(f"{int(h):02d}:{m}")
        for match in FACT_RE.finditer(blob):
            facts.add(match.group(1))
        for match in PRICE_RE.finditer(blob):
            prices.add(match.group(1))
        for match in BARE_DEC_RE.finditer(blob):
            decimals.add(_norm_num(match.group(1)))
        if re.fullmatch(r"\d+", blob):
            facts.add(blob)

    for ev in pack.get("red_events", []) + pack.get("orange_events", []) + pack.get("tier1_events", []):
        facts.add(str(ev.get("fact_id", "")))
        for key in ("forecast", "previous", "actual", "clock_hcm"):
            val = ev.get(key) or ""
            for match in UNIT_RE.finditer(val):
                units.add(_norm_num(match.group(1)) + match.group(2).upper())
            if re.fullmatch(r"\d{1,2}:\d{2}", str(val)):
                h, m = str(val).split(":")
                times.add(f"{int(h):02d}:{m}")
    nxt = pack.get("next_week") or {}
    for ev in nxt.get("red_events", []) + nxt.get("orange_events", []):
        facts.add(str(ev.get("fact_id", "")))
        for key in ("forecast", "previous", "actual"):
            val = ev.get(key) or ""
            for match in UNIT_RE.finditer(val):
                units.add(_norm_num(match.group(1)) + match.group(2).upper())

    for row in pack.get("currency_exposure", []):
        share = row.get("red_share_pct")
        if share is not None and share != "":
            units.add(_norm_num(str(share)) + "%")
            units.add(str(int(float(_norm_num(str(share))))) + "%")
    for block in (pack, pack.get("next_week") or {}):
        focus = block.get("focus") or {}
        by_impact = (block.get("coverage") or {}).get("by_impact") or {}
        total_red = int(by_impact.get("red") or 0)
        primary_red = int(focus.get("primary_red") or 0)
        if total_red:
            pct = round(primary_red / total_red * 100, 1)
            units.add(f"{pct}%")
            units.add(f"{int(pct)}%")
        if primary_red:
            # USD share of next-week primary red, etc.
            pass
        nxt_exp = block.get("currency_exposure_primary") or block.get("currency_exposure") or []
        prim_total = sum(int(r.get("red") or 0) for r in (block.get("currency_exposure_primary") or []))
        if prim_total:
            for row in nxt_exp:
                red = int(row.get("red") or 0)
                pct = round(red / prim_total * 100, 1)
                units.add(f"{pct}%")
                units.add(f"{int(pct)}%")

    return {
        "units": units,
        "times": times,
        "facts": {f for f in facts if f},
        "prices": prices,
        "decimals": decimals,
    }


def _unit_key(num: str, suffix: str) -> str:
    return _norm_num(num) + suffix.upper()


def _unit_allowed(key: str, allowed_units: set[str]) -> bool:
    if key in allowed_units:
        return True
    match = re.fullmatch(r"(-?\d+(?:\.\d+)?)(%|[KM]|BP)", key)
    if not match:
        return False
    num, suf = float(match.group(1)), match.group(2)
    for item in allowed_units:
        other = re.fullmatch(r"(-?\d+(?:\.\d+)?)(%|[KM]|BP)", item)
        if other and other.group(2) == suf and abs(float(other.group(1)) - num) < 0.05:
            return True
    return False


def _minutes(clock: str) -> int:
    h, m = clock.split(":")
    return int(h) * 60 + int(m)


def _time_allowed(clock: str, allowed_times: set[str]) -> bool:
    if clock in allowed_times:
        return True
    stamp = _minutes(clock)
    return any(abs(stamp - _minutes(t)) <= 30 for t in allowed_times)


def lint_report(report: str, pack: dict[str, Any]) -> list[str]:
    report = re.sub(r"<!--.*?-->", " ", report, flags=re.S)
    report = re.sub(r"model:\s*`[^`]+`", " ", report, flags=re.I)
    report = re.sub(r"`[^`]+`", " ", report)
    allowed = allowed_from_pack(pack)
    issues: list[str] = []

    for match in UNIT_RE.finditer(report):
        key = _unit_key(match.group(1), match.group(2))
        if not _unit_allowed(key, allowed["units"]):
            issues.append(f"number not in fact pack: {match.group(0).strip()}")

    for match in TIME_RE.finditer(report):
        h, m = match.group(1).split(":")
        clock = f"{int(h):02d}:{m}"
        if not _time_allowed(clock, allowed["times"]):
            issues.append(f"time not in fact pack: {clock}")

    for match in FACT_RE.finditer(report):
        fid = match.group(1)
        if fid not in allowed["facts"]:
            issues.append(f"unknown fact_id={fid}")

    for match in PRICE_RE.finditer(report):
        if match.group(1) not in allowed["prices"]:
            issues.append(f"price level not in fact pack: {match.group(1)}")

    for match in BARE_DEC_RE.finditer(report):
        dec = _norm_num(match.group(1))
        after = report[match.end() : match.end() + 1]
        if after in {"%", "K", "k", "M", "m"}:
            continue
        if dec in allowed["decimals"]:
            continue
        if any(u.startswith(dec) for u in allowed["units"]):
            continue
        if PRICE_RE.fullmatch(match.group(1)):
            continue
        issues.append(f"decimal not in fact pack: {match.group(0)}")

    for pat in BANNED_ENTRY:
        found = pat.search(report)
        if found:
            issues.append(f"entry-style language: {found.group(0)}")

    return issues


def lint_files(pack_path: Path, report_path: Path) -> list[str]:
    pack = json.loads(pack_path.read_text())
    report = report_path.read_text()
    return lint_report(report, pack)


def main() -> int:
    parser = argparse.ArgumentParser(description="Lint a weekly report against its fact pack.")
    parser.add_argument("--pack", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    issues = lint_files(args.pack, args.report)
    if not issues:
        print(f"PASS {args.report.name}")
        return 0
    print(f"FAIL {args.report.name} ({len(issues)} issue(s))")
    for item in issues:
        print(f"  - {item}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
