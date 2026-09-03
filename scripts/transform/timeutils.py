"""Timezone helpers shared by silver/gold transforms."""

from __future__ import annotations

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

HCM_TZ = ZoneInfo("Asia/Ho_Chi_Minh")


def to_hcm(
    event_date: datetime,
    clock: datetime,
    source_tz_name: str,
) -> tuple[datetime, datetime]:
    """Convert FF local wall time → HCM start/end (1h duration)."""
    source_tz = ZoneInfo(source_tz_name)
    local_dt = datetime(
        event_date.year,
        event_date.month,
        event_date.day,
        clock.hour,
        clock.minute,
        tzinfo=source_tz,
    )
    start_hcm = local_dt.astimezone(HCM_TZ)
    end_hcm = start_hcm + timedelta(hours=1)
    return start_hcm, end_hcm
