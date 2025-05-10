"""
HTTP client utilities for PyHatchery.

This module provides functions to interact with external HTTP services,
primarily for checking package name availability on PyPI.
"""

from typing import Optional, Tuple

import requests

PYPI_JSON_URL_TEMPLATE = "https://pypi.org/pypi/{package_name}/json"


def check_pypi_availability(package_name: str) -> Tuple[Optional[bool], Optional[str]]:
    """
    Checks if a package name is potentially taken on PyPI.

    Args:
        package_name: The name of the package to check (e.g., "my-package-name").

    Returns:
        A tuple (is_taken, error_message).
        - is_taken (Optional[bool]):
            - True if the name is likely taken (HTTP 200).
            - False if the name is likely available (HTTP 404).
            - None if the check could not be completed (network error, etc).
        - error_message (Optional[str]):
            - A string describing the error if the check failed or an issue occurred.
            - None if the check was successful (200 or 404).
    """
    url = PYPI_JSON_URL_TEMPLATE.format(package_name=package_name)
    try:
        response = requests.get(url, timeout=10)  # 10-second timeout

        if response.status_code == 200:
            return True, None  # Name is taken
        if response.status_code == 404:
            return False, None  # Name is available

        response_content = response.text[:200] if response.text else "No content"
        error_msg = (
            f"PyPI check failed for '{package_name}'. "
            f"Unexpected status code: {response.status_code}. "
            f"Response content (truncated): {response_content}"
        )
        return None, error_msg

    except requests.exceptions.Timeout:
        error_msg = (
            f"PyPI check for '{package_name}' timed out. "
            "Please check your network connection."
        )
        return None, error_msg
    except requests.exceptions.ConnectionError:
        error_msg = (
            f"PyPI check for '{package_name}' failed due to a connection error. "
            "Please check your network connection."
        )
        return None, error_msg
    except requests.exceptions.RequestException as e:
        error_msg = (
            f"An unexpected error occurred during PyPI check for '{package_name}': {e}"
        )
        return None, error_msg


if __name__ == "__main__":
    # Example usage for quick testing
    names_to_test = [
        "requests",
        "this_package_does_not_exist_and_hopefully_never_will",
        "pip",
    ]
    for name in names_to_test:
        taken, err = check_pypi_availability(name)
        if err:
            print(f"Error checking '{name}': {err}")
        elif taken is None:
            print(f"Could not determine availability for '{name}'.")
        elif taken:
            print(f"'{name}' is likely TAKEN on PyPI.")
        else:
            print(f"'{name}' is likely AVAILABLE on PyPI.")
