"""Input validation and KQL escaping helpers for caller supplied values."""

import re
from . import consts

MAX_TARGET_LENGTH = 2048
_CONTROL_CHARS = re.compile(r"[\x00-\x1f\x7f]")


def validate_type_and_target(type_of_data, target):
    """Validate the IOC type and target received from the HTTP request.

    Args:
        type_of_data (str): IOC type, must be one of the keys of consts.SOURCES.
        target (str): IOC value.

    Returns:
        bool: True if both values are acceptable, False otherwise.
    """
    if not isinstance(type_of_data, str) or type_of_data not in consts.SOURCES:
        return False
    if not isinstance(target, str) or not target or len(target) > MAX_TARGET_LENGTH:
        return False
    return not _CONTROL_CHARS.search(target)


def escape_kql_string(value):
    """Escape a value so it is always treated as literal data inside a double quoted KQL string.

    Args:
        value (str): Raw value.

    Returns:
        str: Escaped value, safe to place between double quotes in a KQL query.
    """
    value = _CONTROL_CHARS.sub("", str(value))
    return value.replace("\\", "\\\\").replace('"', '\\"')
