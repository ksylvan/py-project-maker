"""Project name validation functions."""


def validate_project_name(project_name: str) -> tuple[bool, str | None]:
    """Validate the project name according to PEP8.

    Currently, this function implements a basic subset of checks. It ensures
    the project name contains only alphanumeric characters, hyphens ('-'),
    or underscores ('_'). More comprehensive validation, fully aligning with
    specific interpretations of PEP 8 or other standards like PEP 426 for
    PyPI distribution names, may be implemented in the future.

    Note:
        PEP 8 package name rules: Python package names should be short,
        all-lowercase, and the use of underscores is generally discouraged.
        (For context: module names in PEP 8 are similar but allow underscores
        more freely for readability. PyPI distribution names, governed by
        standards like PEP 426, have distinct rules, e.g., allowing hyphens
        and periods, and must start/end with an alphanumeric character.)

    Args:
        project_name (str): The name of the project to validate.
    Returns:
        bool: True if the project name is valid, False otherwise.
        str: An error message if the project name is invalid, None otherwise.
    """
    # Further validation for project_name (AC3)
    # For now, just a placeholder for basic character validation.
    # A simple check: does it contain only alphanumeric, hyphen, underscore?
    # This is a very basic check. More robust validation
    # (e.g. not starting/ending with hyphen) later.
    if not all(c.isalnum() or c in ["-", "_"] for c in project_name):
        error_message = (
            f"Error: Project name '{project_name}' contains invalid characters."
        )
        return False, error_message
    return True, None
