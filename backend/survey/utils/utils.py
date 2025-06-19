import logging
import pytz
from dateutil import parser
from datetime import timezone

logger = None


def get_logger():
    global logger
    if logger is not None:
        return logger
    logger = logging.getLogger("survey")
    logger.addHandler(logging.StreamHandler())
    logger.setLevel(logging.INFO)
    return logger


def convert_to_utc(datetime_str: str, tz_name: str = "UTC"):
    """
    Convert a datetime string in a given local timezone to a UTC-aware datetime.

    Args:
        datetime_str (str): The datetime string, e.g. "2025-06-19T12:06:00"
        tz_name (str): The timezone name, e.g. "America/New_York". Defaults to "UTC".

    Returns:
        datetime.datetime: Timezone-aware datetime in UTC.
    """
    dt = parser.parse(datetime_str)

    # Get the timezone object (default UTC if not found)
    try:
        local_tz = pytz.timezone(tz_name)
    except pytz.UnknownTimeZoneError:
        local_tz = pytz.UTC

    if dt.tzinfo is None:
        dt = local_tz.localize(dt)
    else:
        dt = dt.astimezone(local_tz)

    # Convert to UTC
    dt_utc = dt.astimezone(timezone.utc)

    return dt_utc
