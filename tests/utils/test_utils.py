"""Unit tests for utility functions."""

import unittest

from pyhatchery.utils.config import str_to_bool


class TestUtils(unittest.TestCase):
    """Unit tests for utility functions."""

    def test_str_to_bool(self):
        """Test string to boolean conversion."""

        # Test truthy strings
        for truthy in ["true", "1", "yes"]:
            self.assertTrue(str_to_bool(truthy))

        # Test falsy strings
        for falsy in ["false", "0", "no"]:
            self.assertFalse(str_to_bool(falsy))

        # Test None
        self.assertFalse(str_to_bool(None))

        # Test invalid strings
        with self.assertRaises(ValueError):
            str_to_bool("invalid")
