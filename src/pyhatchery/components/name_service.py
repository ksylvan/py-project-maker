"""Project name validation functions."""

import re

_PEP503_VALID_RE = re.compile(
    r"^[a-z0-9](?:[a-z0-9._-]*[a-z0-9])?$",
    re.IGNORECASE | re.ASCII,  # keeps matching strictly ASCII
)
_MAX_LEN = 32  # “short”: pragmatic cap


def pep503_normalize(name: str) -> str:
    """Return the canonical PEP-503 form: lower-case, runs of . _ - become '-'.
    See https://peps.python.org/pep-0503 for more details.

    The name is normalized to lowercase, and runs of periods, underscores, and hyphens
    are replaced with a single hyphen, which are then normalized to lowercase

    Args:
        name (str): The name to canonicalize.
    Returns:
        str: The PEP503 normalized name.

    """
    return re.sub(r"[-_.]+", "-", name).lower()


def pep503_name_ok(project_name: str) -> tuple[bool, str | None]:
    """
    Args:
        project_name (str): The name of the project to validate.

    Returns:
        bool: True if the project name is valid, False otherwise.
        str: An error message if the project name is invalid, None otherwise.

    Implemented checks
    ------------------
    1. PEP503 compliance: Must start and end with a letter or digit, and may contain
       letters, digits, periods, underscores, or hyphens in between
    2. ASCII only: Only ASCII characters are allowed
    3. Short: 32 chars max (pragmatic upper bound)
    4. Limited underscores: No more than 2 underscores allowed
    """
    if not _PEP503_VALID_RE.match(project_name):
        return (
            False,
            f"Error: Project name '{project_name}' violates PEP 503 conventions.",
        )
    if len(project_name) > _MAX_LEN:
        return (
            False,
            f"Error: Project name '{project_name}' is too long (max {_MAX_LEN} chars).",
        )
    if project_name.count("_") > 2:  # keep names terse/readable
        return False, "Error: Project name cannot contain too many underscores."
    return True, None
