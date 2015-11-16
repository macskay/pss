# -*- encoding: utf-8 -*-

from os.path import join, dirname, abspath
from unittest import TestCase

from pss.svg import SvgHandler, SymbolGroupImage

FILE_LOCATION = dirname(abspath(__file__))


class SvgHandlerTestCase(TestCase):
    def setUp(self):
        self.valid_path = join(FILE_LOCATION, "..", "resources", "test_query.svg")

    def test_can_create_with_correct_path(self):
        self.assertIsNotNone(SvgHandler(self.valid_path))

    def test_raise_exception_when_invalid_path_given(self):
        invalid_path = join("..", "resources", "invalid.svg")
        self.assertRaises(FileNotFoundError, SvgHandler, invalid_path)

    def test_when_valid_svg_given_names_and_symbol_group_should_not_be_empty(self):
        svg_handler = SvgHandler(self.valid_path, "Query")
        symbol_group = svg_handler.symbol_groups[0]

        self.assertEqual(svg_handler.names[0], "Query")
        self.assertEqual(svg_handler.get_symbol_group_size(symbol_group), 16)


class SymbolGroupImageTestCase(TestCase):
    def setUp(self):
        valid_path = join(FILE_LOCATION, "..", "resources", "test_query.svg")
        self.svg_handler = SvgHandler(valid_path)
        self.sgi = SymbolGroupImage(self.svg_handler.symbol_groups[0], "Name")

    def test_when_creating_symbol_group_image_bounding_box_is_not_none(self):
        self.assertIsNotNone(self.sgi.bounding_box)

    def test_get_width_returns_width_of_image(self):
        self.assertEqual(self.sgi.get_width(), self.sgi.bounding_box.width()*5)

    def test_get_height_returns_height_of_image(self):
        self.assertEqual(self.sgi.get_height(), self.sgi.bounding_box.height()*5)
