# -*- encoding: utf-8 -*-

# Module under test
from unittest import TestCase, skipIf
from os.path import join, dirname, abspath, isfile

from external.elka_svg import parse

FILE_LOCATION = dirname(abspath(__file__))


@skipIf(not isfile(join(FILE_LOCATION, "..", "resources", "grouped_VAT_09671_Rs_SJakob.svg")), "Travis-CI has no SVGs")
class ElkaSvgTestCase(TestCase):
    def test_parse_svg_file_to_names_and_symbol_groups(self):
        names, symbol_groups = zip(*parse("", join(FILE_LOCATION, "..", "resources", "grouped_VAT_09671_Rs_SJakob.svg")))
        self.assertEqual(len(names), 12)
        self.assertEqual(len(symbol_groups), 12)
