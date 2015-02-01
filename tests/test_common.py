# -*- coding: UTF-8 -*-

from twitter_monitor.common import Tc
import unittest


class TcTestCase(unittest.TestCase):

    def test_warning(self):
        self.assertEquals(
            '\033[93mTest message\033[0m', Tc('Test message').warning)
