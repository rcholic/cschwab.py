from datetime import datetime
import pytz
from typing import Optional

eastern_tz: pytz.BaseTzInfo = pytz.timezone("US/Eastern")
YMD_FMT = "%Y-%m-%d"


def now(tz: pytz.BaseTzInfo = eastern_tz) -> datetime:
    """Today datetime now, Returns datetime, default to US East timezone."""  # noqa: DAR201
    if tz is None:
        return datetime.now()
    return datetime.now().astimezone(tz)


def now_unix_ts() -> float:
    """Today now in unix timestamp, Returns timestamp."""  # noqa: DAR201
    return now().timestamp()


def ts_to_datetime(
    ts: Optional[float] = None, tz: pytz.BaseTzInfo = eastern_tz
) -> Optional[datetime]:
    if ts is None:
        return None
    while ts > 1e10:
        ts = ts / 1000
    return datetime.fromtimestamp(ts, tz)


def ts_to_date_string(
    ts: Optional[float] = None, tz: pytz.BaseTzInfo = eastern_tz
) -> Optional[str]:
    if ts is None:
        return None
    return ts_to_datetime(ts, tz).strftime(YMD_FMT)


def to_iso8601_str(dt: datetime) -> str:
    dt = dt.astimezone(eastern_tz)
    dt_str = dt.strftime("%Y-%m-%dT%H:%M:%S")
    return dt_str + ".000Z"


def today_str(tz: pytz.BaseTzInfo = eastern_tz) -> str:  # type: ignore
    """Today in string. Returns Y-m-d."""  # noqa: DAR201
    return now(tz=tz).strftime(YMD_FMT)
