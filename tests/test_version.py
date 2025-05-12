"""Tests for the version of the package."""

import re

import pyhatchery

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
    assert hasattr(pyhatchery, "__version__"), (
        "The package should have a __version__ attribute."
    )

    version = pyhatchery.__version__

    assert isinstance(version, str), (
        f"The __version__ attribute must be a string, but found type {type(version)}."
    )

    assert re.fullmatch(SEMVER_REGEX, version), (
        f"Version '{version}' does not conform to SemVer (X.Y.Z[-pre+build]). "
        f"See https://semver.org for details."
    )
