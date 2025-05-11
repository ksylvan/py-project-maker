"""Unit tests for the HTTP client component."""

import unittest
from unittest.mock import MagicMock, patch

import requests

from pyhatchery.components.http_client import check_pypi_availability


class TestHttpClient(unittest.TestCase):
    """Tests for the HTTP client component."""

    @patch("pyhatchery.components.http_client.requests.get")
    def test_pypi_name_taken(self, mock_get: MagicMock):
        """Test that a 200 OK response indicates a package name is taken."""
        # Setup
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        # Execute
        is_taken, error_msg = check_pypi_availability("existing-package")

        # Assert
        self.assertTrue(is_taken)
        self.assertIsNone(error_msg)
        mock_get.assert_called_once_with(
            "https://pypi.org/pypi/existing-package/json", timeout=10
        )

    @patch("pyhatchery.components.http_client.requests.get")
    def test_pypi_name_available(self, mock_get: MagicMock):
        """Test that a 404 Not Found response indicates a package name is available."""
        # Setup
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        # Execute
        is_taken, error_msg = check_pypi_availability("new-package-name")

        # Assert
        self.assertFalse(is_taken)
        self.assertIsNone(error_msg)
        mock_get.assert_called_once_with(
            "https://pypi.org/pypi/new-package-name/json", timeout=10
        )

    @patch("pyhatchery.components.http_client.requests.get")
    def test_pypi_api_error(self, mock_get: MagicMock):
        """Test handling of an unexpected status code from PyPI API."""
        # Setup
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Internal server error"
        mock_get.return_value = mock_response

        # Execute
        is_taken, error_msg = check_pypi_availability("package-name")

        # Assert
        self.assertIsNone(is_taken)
        self.assertIsNotNone(error_msg)
        self.assertIn("Unexpected status code: 500", str(error_msg))
        self.assertIn("Internal server error", str(error_msg))
        mock_get.assert_called_once_with(
            "https://pypi.org/pypi/package-name/json", timeout=10
        )

    @patch("pyhatchery.components.http_client.requests.get")
    def test_network_timeout(self, mock_get: MagicMock):
        """Test handling of a network timeout."""
        # Setup
        mock_get.side_effect = requests.exceptions.Timeout("Connection timed out")

        # Execute
        is_taken, error_msg = check_pypi_availability("package-name")

        # Assert
        self.assertIsNone(is_taken)
        self.assertIsNotNone(error_msg)
        self.assertIn("timed out", str(error_msg))
        mock_get.assert_called_once_with(
            "https://pypi.org/pypi/package-name/json", timeout=10
        )

    @patch("pyhatchery.components.http_client.requests.get")
    def test_connection_error(self, mock_get: MagicMock):
        """Test handling of a connection error."""
        # Setup
        mock_get.side_effect = requests.exceptions.ConnectionError(
            "Could not connect to PyPI"
        )

        # Execute
        is_taken, error_msg = check_pypi_availability("package-name")

        # Assert
        self.assertIsNone(is_taken)
        self.assertIsNotNone(error_msg)
        self.assertIn("connection error", str(error_msg))
        mock_get.assert_called_once_with(
            "https://pypi.org/pypi/package-name/json", timeout=10
        )

    @patch("pyhatchery.components.http_client.requests.get")
    def test_general_request_exception(self, mock_get: MagicMock):
        """Test handling of a general request exception."""
        # Setup
        mock_get.side_effect = requests.exceptions.RequestException(
            "Some other request error"
        )

        # Execute
        is_taken, error_msg = check_pypi_availability("package-name")

        # Assert
        self.assertIsNone(is_taken)
        self.assertIsNotNone(error_msg)
        self.assertIn("unexpected error", str(error_msg))
        self.assertIn("Some other request error", str(error_msg))
        mock_get.assert_called_once_with(
            "https://pypi.org/pypi/package-name/json", timeout=10
        )
