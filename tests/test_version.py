"""Tests for the version of the package."""

import re

import pyhatchery

# Semantic Versioning 2.0.0 regex from https://semver.org/
# This regex is used to validate version strings.
# Passes versions like "1.0.0", "0.2.1", "1.0.0-alpha", "2.1.0-beta.1+build.123"
# and respects rules like no leading zeros for numeric identifiers
# (e.g., "01.0.0" is invalid).
SEMVER_REGEX = (
    r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)"
    r"(?:-((?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)"
    r"(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?"
    r"(?:\+([0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$"
)


def test_version_attributes():
    """
    Tests that the __version__ attribute is set in the module and
    conforms to semantic versioning norms (SemVer 2.0.0).
    """
    # Check if the __version__ attribute exists
    assert hasattr(pyhatchery, "__version__"), (
        "The package should have a __version__ attribute."
    )

    version = pyhatchery.__version__

    # Check if __version__ is a string
    assert isinstance(version, str), (
        f"The __version__ attribute must be a string, but found type {type(version)}."
    )

    # Check if __version__ conforms to semantic versioning
    assert re.fullmatch(SEMVER_REGEX, version), (
        f"Version '{version}' does not conform to SemVer (X.Y.Z[-pre+build]). "
        f"See https://semver.org for details."
    )
