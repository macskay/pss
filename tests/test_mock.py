# -*- encoding: utf-8 -*-

from unittest import TestCase


class MockTestCase(TestCase):
    def test_working_environment(self):
        self.fail()
