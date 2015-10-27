# -*- encoding: utf-8 -*-

# Module under test
from unittest import TestCase
from os.path import join, dirname, abspath

from external.elka_svg import parse

FILE_LOCATION = dirname(abspath(__file__))


class ElkaSvgTestCase(TestCase):
    def test_parse(self):
        names, pathss = zip(*parse("", join(FILE_LOCATION, "..", "resources", "grouped_VAT_09671_Rs_SJakob.svg")))
        self.assertEqual(len(names), 12)
        self.assertEqual(len(names), 12)
