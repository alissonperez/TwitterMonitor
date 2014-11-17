#!/usr/bin/python
# -*- coding: UTF-8 -*-

import os
import argparse
import sys
import logging
from unittest import TestLoader
from unittest import TextTestRunner


class TMTestRunner(object):

    def __init__(self):
        self._parser = argparse.ArgumentParser(
            description='TwitterMonitor - Tests')

        self._parser.add_argument(
            "-f", "--filter",
            dest="filter",
            help="Run a specific test (modules inside 'tests' dir)")

    def execute(self, args=None):
        if args is None:
            args = sys.argv[1:]

        self.options = self._parser.parse_args(args)

        return self._run_tests()

    def _run_tests(self):
        if not TextTestRunner().run(self._get_suite()).wasSuccessful():
            raise SystemExit(1)
        else:
            return 0

    def _get_suite(self):
        # Using filter from command line
        if self.options.filter is not None:
            name = "tests." + self.options.filter
            return TestLoader().loadTestsFromName(name)

        project_dir = os.path.dirname(os.path.realpath(__file__)) + "/tests/"
        return TestLoader().discover(project_dir)


logging.getLogger('').addHandler(logging.NullHandler())
TMTestRunner().execute()
