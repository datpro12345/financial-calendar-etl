#!/usr/bin/env python3
"""Warn when a silver partition is missing an impact layer.

Every month from 2026_01 to 2026_09 sat at ``coverage: "red+orange+yellow"`` for
months: the gray (``impacts=0``) layer was never fetched, so the mart had one
holiday in total and ``liquidity_holidays`` was effectively always empty. Nothing
failed and nothing warned. This check exists so that cannot repeat silently.
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.extract.config import (
    BRONZE_LANDING_DIR,
    IMPACT_LAYERS,
    SILVER_EVENTS_DIR,
)
from scripts.transform.merge_silver import read_partition

logger = logging.getLogger(__name__)

EXPECTED_LAYERS = tuple(label for label, _ in IMPACT_LAYERS)
MONTHLY_PARTITION_GLOB = "20[0-9][0-9]_[01][0-9].csv"


def check_impact_coverage(
    silver_dir: Path | str = SILVER_EVENTS_DIR,
    landing_dir: Path | str = BRONZE_LANDING_DIR,
    *,
    expected: tuple[str, ...] = EXPECTED_LAYERS,
) -> dict:
    silver_dir = Path(silver_dir)
    landing_dir = Path(landing_dir)

    partitions: list[dict] = []
    warnings: list[str] = []

    for path in sorted(silver_dir.glob(MONTHLY_PARTITION_GLOB)):
        part = path.stem
        frame = read_partition(path)
        present = {
            str(value).strip().lower()
            for value in frame["impact"].unique()
            if str(value).strip()
        }
        missing = [layer for layer in expected if layer not in present]

        meta_path = landing_dir / f"{part}.meta.json"
        declared = ""
        if meta_path.exists():
            declared = json.loads(meta_path.read_text()).get("coverage", "")

        partitions.append(
            {
                "partition": part,
                "rows": len(frame),
                "layers_present": sorted(present),
                "layers_missing": missing,
                "landing_coverage": declared,
            }
        )
        if missing:
            warnings.append(
                f"{part}: no {'/'.join(missing)} rows "
                f"(landing coverage {declared or 'unknown'}) — "
                f"refetch that impact layer with fetch_bronze_months.py"
            )

    for warning in warnings:
        logger.warning("Impact coverage — %s", warning)

    return {
        "ok": not warnings,
        "expected_layers": list(expected),
        "partitions": partitions,
        "warnings": warnings,
    }


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    parser = argparse.ArgumentParser(description="Check silver partitions for missing impact layers")
    parser.add_argument("--silver-dir", type=Path, default=SILVER_EVENTS_DIR)
    parser.add_argument("--landing-dir", type=Path, default=BRONZE_LANDING_DIR)
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit non-zero when a layer is missing (default: warn only)",
    )
    args = parser.parse_args()

    result = check_impact_coverage(args.silver_dir, args.landing_dir)
    print(json.dumps(result, indent=2))
    return 1 if args.strict and not result["ok"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
