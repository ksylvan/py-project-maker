"""Project name validation functions."""

import keyword
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
    # Strip leading/trailing whitespace and replace internal spaces with hyphens
    name = name.strip()
    name = re.sub(r"\s+", "-", name)
    # Replace runs of separators with a single hyphen
    return re.sub(r"[-_.]+", "-", name).lower()


def derive_python_package_slug(name: str) -> str:
    """
    Derives a Python package slug from a project name.
    Converts to lowercase, replaces separators with underscores,
    and ensures it's a valid Python identifier.

    Args:
        name: The project name.

    Returns:
        A string suitable for use as a Python package name.
    """
    # Replace non-alphanumeric characters (except underscores) with underscores
    slug = re.sub(r"[^a-zA-Z0-9_]", "_", name)
    # Convert to lowercase
    slug = slug.lower()
    # Consolidate multiple underscores
    slug = re.sub(r"_+", "_", slug)
    # Remove leading/trailing underscores
    slug = slug.strip("_")

    # Ensure it's a valid Python identifier
    if not slug:  # Handle empty string case
        return "default_package_name"

    # Check if it's a Python keyword

    if keyword.iskeyword(slug):
        return "default_package_name"

    if not slug.isidentifier():
        # If it's not a valid identifier (e.g., starts with a digit)
        if slug[0].isdigit():
            slug = f"p_{slug}"
        # If still not an identifier, provide a default
        if not slug.isidentifier():
            return "default_package_name"

    return slug


def is_valid_python_package_name(slug: str) -> tuple[bool, str | None]:
    """
    Checks if the given slug is a valid PEP 8 Python package name.
    - Must be a valid Python identifier.
    - Must be all lowercase.
    - Should only contain lowercase letters, numbers (not starting), and underscores.

    Args:
        slug: The Python package slug to validate.

    Returns:
        A tuple (is_valid, message). Message is None if valid.
    """
    if not slug:
        return False, "Python package slug cannot be empty."
    if not slug.isidentifier():
        return (
            False,
            f"Derived Python package slug '{slug}' is not a valid Python identifier "
            "(e.g., cannot start with a digit or contain hyphens/spaces).",
        )
    if not slug.islower():  # isidentifier allows uppercase, but PEP 8 wants lowercase
        # This check might be redundant if derive_python_package_slug
        # always produces lowercase
        return (
            False,
            f"Derived Python package slug '{slug}' should be all lowercase.",
        )
    # Further check for characters, though isidentifier should cover most.
    # PEP 8: "modules should have short, all-lowercase names. Underscores can be
    # used in the module name if it improves readability."
    # isidentifier() handles a-z, 0-9, _ expectations.
    return True, None


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
