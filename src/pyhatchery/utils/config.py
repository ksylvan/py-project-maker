"Helper functions for configuration management."

TRUTHY_STRINGS = ["true", "1", "yes"]
FALSY_STRINGS = ["false", "0", "no"]


def str_to_bool(value: str | None) -> bool:
    """
    Convert a string to a boolean value based on its truthiness

    Args:
        value (str or None): to be converted.

    Returns:
        bool: False if None, and True if the string is truthy, False otherwise.
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
