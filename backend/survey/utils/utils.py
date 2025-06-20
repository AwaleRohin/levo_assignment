import logging
import pytz
from dateutil import parser
from datetime import timezone
from typing import Optional

_logger: Optional[logging.Logger] = None

def get_logger() -> logging.Logger:
    global _logger
    if _logger is not None:
        return _logger

    _logger = logging.getLogger("survey")
    if not _logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "[%(asctime)s] [%(levelname)s] %(name)s - %(message)s"
        )
        handler.setFormatter(formatter)
        _logger.addHandler(handler)

    _logger.setLevel(logging.INFO)
    return _logger


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
