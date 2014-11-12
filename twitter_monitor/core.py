# -*- coding: UTF-8 -*-

from abc import ABCMeta
from abc import abstractmethod
import logging


class loggable(object):
    """
    Include logger property in objects to show log messages
    """

    _logger = None

    @property
    def logger(self):
        if self._logger is None:
            self._logger = logging.getLogger(__name__)
            self._logger.addHandler(logging.NullHandler())
            self._logger.setLevel(logging.DEBUG)

        return self._logger

    @logger.setter
    def logger(self, logger):
        self._logger = logger


class Notifier(loggable):
    """
    It sends a message to destinations (followers) with twitter API.
    """

    def __init__(self, api):
        self._api = api

        # Cache dos seguidores...
        self._followers = None

    def send(self, message):
        self.logger.debug("Message to send: \"{}\"".format(message))

        # Casting message
        message = str(message)

        if len(message.strip()) == 0:
            # @todo - Change this to exception
            self.logger.warn("Empty message")
            return

        for follower in self._get_followers():
            self.logger.info("Sending message to \"{}\": \"{}\"".format(
                follower.screen_name, message))

            self._api.send_direct_message(user_id=follower.id, text=message)

    def _get_followers(self):
        if self._followers is None:
            self._followers = self._api.followers()

        return self._followers


class Routine(loggable):
    """
    Representação de uma rotina
    """

    __metaclass__ = ABCMeta

    name = None            # Routine full name

    short_name = None      # Routine short name (it'll be used in message)

    def __init__(self, notifier):
        self.notifier = notifier

        if self.name is None:
            self.name = self.__class__.__name__

        if self.short_name is None:
            self.short_name = self.__class__.__name__

    def run(self):
        return self._execute()

    @abstractmethod
    def _execute(self):
        return NotImplemented

    def notify(self, message):
        message = str(message)

        if len(message.strip()) == 0:
            self.logger.debug("Empty message")
            return

        new_message = "{}: {}".format(
            self.short_name, message)

        self.notifier.send(new_message)

    def __str__(self):
        return "Routine '{}'".format(self.name)