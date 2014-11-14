# -*- coding: UTF-8 -*-

from twitter_monitor.core import Notifier, Routine
from mock import MagicMock, Mock
import unittest


def create_twitter_api_mock():
    """
    Create a mocked twitter api to use with tests
    """
    class Follower:
        def __init__(self, screen_name, id):
            self.screen_name = screen_name
            self.id = id

    api = MagicMock(name="TwitterApi")

    api.followers.return_value = [Follower("alissonperez", 42)]

    return api


class NotifierTestCase(unittest.TestCase):

    def setUp(self):
        self.api = create_twitter_api_mock()
        self.notifier = Notifier(self.api)

    def test_send(self):
        message = "Test message"
        self.notifier.send(message)

        followers = self.api.followers()
        follower_id = followers[0].id

        self.api.send_direct_message.assert_called_once_with(
            user_id=follower_id, text=message)

    def test_send_with_empty_message(self):
        self.api.send_direct_message = Mock(
            side_effect=Exception("Method should not be called"))

        message = ""
        self.notifier.send(message)


def create_notifier_mock():
    """
    Create a mocked nofifier object to use with tests
    """

    notifier = MagicMock(name="Notifier")

    return notifier


class RoutineTest(Routine):

    name = "Routine Test"
    short_name = "Rout. Test"

    def _execute(self):
        self.notify("Test message")
        return True


class RoutineTestCase(unittest.TestCase):

    def setUp(self):
        self.notifier = create_notifier_mock()
        self.routine = RoutineTest(self.notifier)

    def test_run(self):
        self.assertTrue(self.routine.run(), "Run method should return true")

        message = "{}: {}".format(self.routine.short_name, "Test message")

        self.notifier.send.assert_called_once_with(message)
