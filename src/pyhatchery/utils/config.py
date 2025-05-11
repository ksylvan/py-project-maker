"Helper functions for configuration management."

from typing import Optional

TRUTHY_STRINGS = ["true", "1", "yes"]
FALSY_STRINGS = ["false", "0", "no"]


def str_to_bool(value: Optional[str]) -> bool:
    """
    Convert a string to a boolean value based on its truthiness

    Args:
        value (str): The string to convert.

    Returns:
        bool: True if the string is 'true' (case insensitive), False otherwise.
    """
    if value is None:
        return False
    value = value.lower()
    if value in TRUTHY_STRINGS:
        return True
    if value in FALSY_STRINGS:
        return False
    raise ValueError(
        f"Invalid boolean string: {value} - "
        f"must be one of {TRUTHY_STRINGS + FALSY_STRINGS}"
    )
