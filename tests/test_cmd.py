# -*- coding: UTF-8 -*-

from twitter_monitor.cmd import Executor
from twitter_monitor.core import Routine
from mock import MagicMock, Mock
import unittest


class RoutineTest(Routine):

    name = u"Routine Test"
    short_name = u"Rout. Test"

    def _execute(self):
        self.notify("Test message")
        return True


class ExecutorTestCase(unittest.TestCase):

    def test_run(self):
        notifier = Mock(name="NotifierTest")
        e = Executor(notifier, [RoutineTest])

        self.assertTrue(e.run())

        notifier.send.assert_called_once_with('Rout. Test: Test message')