# -*- encoding: utf-8 -*-

# Module under test
from unittest import TestCase, skip
import lib.elka_svg
from os.path import join


@skip("Still working on this, test not working yet")
class ElkaSvgTestCase(TestCase):
    def test_parse(self):
        names, pathss = lib.elka_svg.parse(" ", join("..", "resources", "grouped_VAT_09671_Rs_SJakob.svg"))
        self.assertEqual(len(names), 5)
