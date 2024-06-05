from datetime import datetime
import pytz

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


def ts_to_datetime(ts: float, tz: pytz.BaseTzInfo = eastern_tz) -> datetime:
    while ts > 1e10:
        ts = ts / 1000
    return datetime.fromtimestamp(ts, tz)


def today_str(tz: pytz.BaseTzInfo = eastern_tz) -> str:  # type: ignore
    """Today in string. Returns Y-m-d."""  # noqa: DAR201
    return now(tz=tz).strftime(YMD_FMT)
