"""
HTTP client utilities for PyHatchery.

This module provides functions to interact with external HTTP services,
primarily for checking package name availability on PyPI.
"""

from http import HTTPStatus

import requests

PYPI_JSON_URL_TEMPLATE = "https://pypi.org/pypi/{package_name}/json"
RESPONSE_CUT_OFF = 200


def check_pypi_availability(package_name: str) -> tuple[bool | None, str | None]:
    """
    Checks if a package name is potentially taken on PyPI.

    Args:
        package_name: The name of the package to check (e.g., "my-package-name").

    Returns:
        A tuple (is_taken, error_message).
        - is_taken (bool | None):
            - True if the name is likely taken (HTTP 200).
            - False if the name is likely available (HTTP 404).
            - None if the check could not be completed (network error, etc).
        - error_message (str | None):
            - A string describing the error if the check failed or an issue occurred.
            - None if the check was successful (200 or 404).
    """

    url = PYPI_JSON_URL_TEMPLATE.format(package_name=package_name)
    try:
        response = requests.get(url, timeout=10)

        if response.status_code == HTTPStatus.OK:
            return True, None
        if response.status_code == HTTPStatus.NOT_FOUND:
            return False, None

        response_content = (
            response.text[:RESPONSE_CUT_OFF] if response.text else "No content"
        )
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
