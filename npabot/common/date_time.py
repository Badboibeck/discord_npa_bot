import datetime

import pytz

ZERO_TIMES = {"hour": 0, "minute": 0, "second": 0, "microsecond": 0}
MAX_TIMES = {"hour": 23, "minute": 59, "second": 59, "microsecond": 999999}


def utc_now() -> datetime.datetime:
    return datetime.datetime.now(tz=datetime.timezone.utc)


def utc_now_naive() -> datetime.datetime:
    now = utc_now()
    return datetime.datetime(
        year=now.year,
        month=now.month,
        day=now.day,
        hour=now.hour,
        minute=now.minute,
        second=now.second,
        microsecond=now.microsecond,
    )


def us_est_now() -> datetime.datetime:
    return datetime.datetime.now(tz=pytz.timezone("America/New_York"))


def convert_to_naive(value: datetime.datetime) -> datetime.datetime:
    return datetime.datetime(
        year=value.year,
        month=value.month,
        day=value.day,
        hour=value.hour,
        minute=value.minute,
        second=value.second,
        microsecond=value.microsecond,
    )


def date_as_utc(year: int, month: int, day: int = 1) -> datetime.datetime:
    return datetime.datetime(
        year=year, month=month, day=day, tzinfo=datetime.timezone.utc
    )
