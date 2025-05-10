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
    1. **Valid identifier**: letters/digits/underscores, not starting with a digit
    2. **All lowercase**: no capital letters
    3. **No punctuation**: hyphens, dots, spaces, etc. are disallowed
    4. **Short**: 32 chars max (PEP8 says “short”; this is a practical upper bound)
    5. **Underscores discouraged**: allowed, but a leading “_” (used only for C
       extension helpers) or multiple underscores fail the test
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
