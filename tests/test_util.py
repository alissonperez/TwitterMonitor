# -*- coding: UTF-8 -*-

import unittest
from twitter_monitor.util import slugfy


class SlugfyTestCase(unittest.TestCase):

    def test_conversion(self):
        tests = [
            (u"Alisson dos Reis Perez  ", "alisson-dos-reis-perez"),
            (u"  Verificação de  Fichas", "verificacao-de-fichas"),
            (u"  Test with	tabulation and -- multiple '-'",
                "test-with-tabulation-and-multiple-"),
        ]

        for original, expected in tests:
            self.assertEquals(expected, slugfy(original))
