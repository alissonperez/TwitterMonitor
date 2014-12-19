# -*- coding: UTF-8 -*-

from abc import ABCMeta
from abc import abstractmethod
from . import common
import datetime
import hashlib
import logging
import tweepy
import dbm
import tempfile
import collections

# Module logger
logger = logging.getLogger(__name__)


class ExecutorFactory(common.loggable):
    """
    Factory responsible to create
    an :class:`twitter_monitor.core.Executor` instance.

    :param routines: A list of :class:`twitter_monitor.core.Routine`
        subclasses (**not instances**)
    :param twitter_keys: A dictionary with api twitter keys. It must have these
        keys (you can manage all of them on https://apps.twitter.com/).

        - consumer_key
        - consumer_secret
        - access_token_key
        - access_token_secret
    :param setup_default_logger: If True (default) it'll setup the root logger.
    """

    def __init__(self, routines,
                 twitter_keys, setup_default_logger=True):
        self.routines = routines
        self.twitter_keys = twitter_keys
        self.setup_default_logger = setup_default_logger

    def create_default(self):
        """
        Create a default Executor and setup a default logger.
        """

        self._setup_logger()
        self.logger.debug("Creating a default Executor")

        notifier = self._create_notifier(self._create_twitter_api())

        executor = Executor(
            notifier, self.routines, self._create_key_value_store())

        return executor

    def _setup_logger(self):
        """
        Setup module logger to show processing messages.
        """

        if not self.setup_default_logger:
            return

        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s')

        handler = logging.StreamHandler()
        handler.setFormatter(formatter)

        logger = logging.getLogger("")
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)

    def _create_twitter_api(self):
        self.logger.debug("Creating a twitter api")

        ta = self.twitter_keys

        self.logger.debug("Consumer_key: " + ta["consumer_key"])
        self.logger.debug("Consumer_secret: " + ta["consumer_secret"])
        self.logger.debug("Access_token_key: " + ta["access_token_key"])
        self.logger.debug("Access_token_secret: " + ta["access_token_secret"])

        auth = tweepy.OAuthHandler(
            ta['consumer_key'], ta['consumer_secret'])
        auth.set_access_token(
            ta['access_token_key'], ta['access_token_secret'])

        return tweepy.API(auth)

    def _create_notifier(self, twitter_api):
        n = Notifier(twitter_api)
        return n

    def _create_key_value_store(self):
        try:
            name = ".twitter-monitor-info"
            filename = "{}/{}".format(tempfile.gettempdir(), name)
            return dbm.open(filename, "c")
        except Exception as e:
            pass

        return None


class Executor(common.loggable):
    """
    Responsible to run routines. This class must receive
    an instance of :class:`twitter_monitor.core.Notifier` class
    and an array of routines.

    :param notifier: An instance of :class:`twitter_monitor.core.Notifier`
    :param routines: A list of :class:`twitter_monitor.core.Routine`
        subclasses (**not instances**)
    :param key_value_store: A dictionary like storage.
        It is used to store info about last
        executions (like last execution time).
        It is usual to use a simple key store like *anydbm*.
    """

    def __init__(self, notifier, routines, key_value_store={}):
        self.notifier = notifier
        self.routines = routines
        self.key_value_store = key_value_store
        self._routines_instances = None

    def run(self):
        """
        Execute all routines. It returns True if all routines are
        executed with success.
        """

        success = True

        try:
            for rt in self.routines_instances():
                self.logger.info("Running \"{}\"".format(str(rt)))

                if not rt.run():
                    self.logger.error(
                        "Error on running routine \"{}\"".format(str(rt)))

                    success = False

                self.logger.info("Finished \"{}\"".format(str(rt)))
        except Exception as e:
            if (hasattr(self.key_value_store, "close")
                    and isinstance(getattr(self.key_value_store, "close"), collections.Callable)):
                    self.key_value_store.close()

            self.logger.error("Error: " + str(e))
            success = False

        return success

    def routines_instances(self):
        """
        Instantiate and return all routines instances.
        """

        if self._routines_instances is not None:
            return self._routines_instances

        self._routines_instances = []

        for class_ref in self.routines:
            self._routines_instances.append(
                class_ref(self.notifier, self.key_value_store))

        return self._routines_instances


class Notifier(common.loggable):
    """
    It sends a message to destinations (followers) with twitter API.

    :param api: An API instance (for now, we are using Tweepy)
    """

    def __init__(self, api):
        self._api = api

        # Cache dos seguidores...
        self._followers = None

    def send(self, message):
        """
        Send a message to all destinations

        :param message: A message to send to all followers.
        """

        if not isinstance(message, str):
            message = str(message, errors="ignore")

        self.logger.debug("Message to send: \"{}\"".format(message))

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


class Routine(common.loggable, metaclass=ABCMeta):
    """
    Routine representation

    :param notifier: An instance of :class:`twitter_monitor.core.Notifier`
    :param key_value_store: A dictionary like storage.
        It is used to store info about last
        executions (like last execution time).
        It is usual to use a simple key store like *anydbm*.
    """

    name = None  #: Routine full name.

    short_name = None  #: Routine short name (it'll be used in the message).

    interval_minutes = None  #: Interval (in minutes) to execute routine

    _file_last_execution = None  #: Cache of last execution file content

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
            message = "Interval not reached. Elapsed {} minutes"
            self.logger.info(message.format(diff.seconds/60))
            return True

        return False

    @abstractmethod
    def _execute(self):
        """
        Put your code here in your subclasses.
        Must be implemented by subclasses.

        Use self.notify('Some message') to send a message to recepients.
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
        except Exception as e:
            self.logger.debug(
                "Exception - Method/property 'last_execution': " + str(e))

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
        Routine unique id (md5 format)
        """

        name = "{} {} {}".format(
            self.__class__.__name__, self.name, self.short_name)

        m = hashlib.md5()
        m.update(name.encode("ascii", errors="ignore"))

        return m.hexdigest()

    def notify(self, message):
        """
        Send the message
        """

        if not isinstance(message, str):
            message = str(message)

        if len(message.strip()) == 0:
            self.logger.debug("Empty message")
            return

        new_message = "{}: {}".format(
            self.short_name, message)

        self.notifier.send(new_message)

    def __str__(self):
        return "Routine '{}'".format(self.name)
