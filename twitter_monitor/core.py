# -*- coding: UTF-8 -*-

from abc import ABCMeta
from abc import abstractmethod
import logging
import util
import datetime
import tempfile
import hashlib


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
    Routine representation
    """

    __metaclass__ = ABCMeta

    name = None  # Routine full name

    short_name = None  # Routine short name (it'll be used in message)

    interval_minutes = None  # Interval to execute routine

    _file_last_execution = None  # Cache of last execution file content

    def __init__(self, notifier, key_value_store={}):
        self.notifier = notifier
        self.key_value_store = key_value_store

        if self.name is None:
            self.name = self.__class__.__name__

        if self.short_name is None:
            self.short_name = self.__class__.__name__

    def run(self):
        """
        Run this routine
        """

        if self._skip_execution():
            self.logger.info("Skipping execution")
            return True

        if self._execute():
            self._set_last_execution()
            return True

        return False

    def _skip_execution(self):
        if self.interval_minutes is None or self.last_execution is None:
            return False

        timedelta_compare = datetime.timedelta(minutes=self.interval_minutes)

        diff = datetime.datetime.now() - self.last_execution

        if diff < timedelta_compare:
            message = ("Interval not reached. Elapsed {} minutes")
            self.logger.info(message.format(diff.seconds/60))
            return True

        return False

    @abstractmethod
    def _execute(self):
        """
        Put your code here in your subclasses.
        Must be implemented by subclasses.
        """

        return NotImplemented

    def clear_last_execution(self):
        """
        Clear last execution time of this routine
        """

        self._set_last_execution("")

    @property
    def last_execution(self):
        """
        Returns a datetime object with last execution of routine
        """

        self.logger.debug("Finding last execution time")

        try:
            if self.uid in self.key_value_store:
                val = self.key_value_store[self.uid]
                return datetime.datetime.strptime(val, "%Y-%m-%d %H:%M:%S.%f")
        except Exception, e:
            self.logger.debug(
                "Exception - Method/property 'last_execution': " + e.message)

        return None

    def _set_last_execution(self, val=None):
        now_str = datetime.datetime.now().isoformat(" ")
        now_str = now_str if val is None else val

        self.logger.debug(
            "Setting last execution file content to: '{}'".format(now_str))

        self.key_value_store[self.uid] = now_str

    @property
    def uid(self):
        """
        It returns the routine unique id
        """
        name = u"{} {} {}".format(
            self.__class__.__name__, self.name, self.short_name)

        m = hashlib.md5()
        m.update(name)

        return m.hexdigest()

    def notify(self, message):
        message = str(message)

        if len(message.strip()) == 0:
            self.logger.debug("Empty message")
            return

        new_message = u"{}: {}".format(
            self.short_name, message)

        self.notifier.send(new_message)

    def __str__(self):
        return u"Routine '{}'".format(self.name)
