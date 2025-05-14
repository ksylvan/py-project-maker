"""Unit tests for the name service component."""

import unittest

from pytest import raises

from pyhatchery.components.name_service import (
    derive_python_package_slug,
    is_valid_python_package_name,
    pep503_name_ok,
    pep503_normalize,
)


class TestNameService(unittest.TestCase):
    """Tests for the name service component."""

    def test_pep503_normalize(self):
        """Test PEP 503 normalization for various inputs."""
        test_cases = [
            ("my-project", "my-project"),
            ("My_Project", "my-project"),
            ("My.Project", "my-project"),
            ("My__Project..Name", "my-project-name"),
            ("my-project", "my-project"),
            ("My--Project__Name", "my-project-name"),
            ("PROJECT", "project"),
        ]

        for input_name, expected_output in test_cases:
            with self.subTest(input_name=input_name):
                result = pep503_normalize(input_name)
                self.assertEqual(
                    result,
                    expected_output,
                    f"Failed to normalize '{input_name}' correctly. "
                    f"Got '{result}', expected '{expected_output}'",
                )

    def test_derive_python_package_slug(self):
        """Test Python package slug derivation for various inputs."""
        test_cases = [
            ("my_package", "my_package"),
            ("My Package", "my_package"),
            ("My-Hyphenated-Package", "my_hyphenated_package"),
            ("package.name", "package_name"),
            ("my__package", "my_package"),
            ("_package_", "package"),
            ("package123", "package123"),
        ]

        for input_name, expected_output in test_cases:
            with self.subTest(input_name=input_name):
                result = derive_python_package_slug(input_name)
                self.assertEqual(
                    result,
                    expected_output,
                    "Failed to derive Python package slug "
                    f"from '{input_name}' correctly. "
                    f"Got '{result}', expected '{expected_output}'",
                )

    def test_is_valid_python_package_name(self):
        """Test validation of Python package names against PEP 8 conventions."""
        valid_names = [
            "package_name",
            "simple",
            "my_package_123",
            "package",
            "single_underscore",
        ]

        for name in valid_names:
            with self.subTest(name=name, valid=True):
                is_valid, message = is_valid_python_package_name(name)
                self.assertTrue(
                    is_valid,
                    f"'{name}' should be valid, but got message: {message}",
                )
                self.assertIsNone(message)

        invalid_names_with_reasons = [
            ("", "Python package slug cannot be empty."),
            ("123package", "not a valid Python identifier"),
            ("Package", "should be all lowercase"),
            ("my-package", "not a valid Python identifier"),
            ("my package", "not a valid Python identifier"),
        ]

        for name, reason_fragment in invalid_names_with_reasons:
            with self.subTest(name=name, valid=False):
                is_valid, message = is_valid_python_package_name(name)
                self.assertFalse(
                    is_valid,
                    f"'{name}' should be invalid, but was marked valid",
                )
                self.assertIsNotNone(message)
                self.assertIsNotNone(message)
                if message:
                    self.assertIn(
                        reason_fragment.lower(),
                        message.lower(),
                        f"Error message for '{name}' should "
                        f"contain '{reason_fragment}'",
                    )

    def test_pep503_name_ok(self):
        """Test PEP 503 project name validation."""
        valid_names = [
            "package-name",
            "Package_Name",
            "PACKAGE",
            "package",
            "package.name",
            "package-name123",
            "123package",
        ]

        for name in valid_names:
            with self.subTest(name=name, valid=True):
                is_valid, message = pep503_name_ok(name)
                self.assertTrue(
                    is_valid,
                    f"'{name}' should be valid, but got message: {message}",
                )
                self.assertIsNone(message)

        invalid_names_with_reasons = [
            ("-package", "violates PEP 503"),
            ("package-", "violates PEP 503"),
            ("pack***age", "violates PEP 503"),
            ("package_name_with_too_many_underscores", "too long"),
            ("with___too___many___underscores", "too many underscores"),
        ]

        for name, reason_fragment in invalid_names_with_reasons:
            with self.subTest(name=name, valid=False):
                is_valid, message = pep503_name_ok(name)
                self.assertFalse(
                    is_valid,
                    f"'{name}' should be invalid, but was marked valid",
                )
                self.assertIsNotNone(message)
                if message:
                    self.assertIn(
                        reason_fragment.lower(),
                        message.lower(),
                        f"Error message for '{name}' "
                        f"should contain '{reason_fragment}'",
                    )

    def test_derive_python_package_slug_throws_exception(self):
        """Test handling of invalid project names."""
        # Test with a name that normalizes to an empty string
        with raises(ValueError, match=".*is empty*"):
            derive_python_package_slug("___+++")

        # Test with a name that normalizes to a Python keyword
        for p in [
            "def",
            "class",
            "for",
            "pass",
            "return",
            "if",
            "else",
            "elif",
            "try",
            "except",
        ]:
            with raises(ValueError, match=".* is a reserved keyword.*"):
                derive_python_package_slug(p)

        # Test with a name that is not a valid identifier
        with raises(ValueError, match=".*starts with a digit.*"):
            derive_python_package_slug("123abc")

        # Test with edge cases that resolve to valid package names
        assert derive_python_package_slug("project!name") == "project_name"
        assert derive_python_package_slug("project name") == "project_name"

        # Verify that non-keywords work correctly
        assert derive_python_package_slug("normal_name") == "normal_name"
        assert derive_python_package_slug("project-name") == "project_name"
