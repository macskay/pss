# -*- encoding: utf-8 -*-

from unittest import TestCase
from os.path import join, dirname, abspath

from wordspot.svg import SvgHandler

FILE_LOCATION = dirname(abspath(__file__))


class SvgHandlerTestCase(TestCase):
    def setUp(self):
        self.valid_path = join(FILE_LOCATION, "..", "resources", "grouped_VAT_09671_Rs_SJakob.svg")

    def test_can_create_with_correct_path(self):
        self.assertIsNotNone(SvgHandler(self.valid_path))

    def test_raise_exception_when_invalid_path_given(self):
        invalid_path = join("..", "resources", "invalid.svg")
        self.assertRaises(FileNotFoundError, SvgHandler, invalid_path)

    def test_when_valid_svg_given_names_and_pathss_should_not_be_empty(self):
        svg_handler = SvgHandler(self.valid_path)
        self.assertTrue(len(svg_handler.names) > 0)
        self.assertTrue(len(svg_handler.pathss) > 0)

