from os.path import join, dirname, abspath
from unittest import TestCase

from pss.binimg import handle_file_not_existing

FILE_LOCATION = dirname(abspath(__file__))


class BinTestCase(TestCase):
    def test_raise_error_when_path_is_invalid(self):
        invalid_path = join(FILE_LOCATION, "..", "resources", "invalid.png")
        self.assertRaises(FileNotFoundError, handle_file_not_existing, invalid_path)
