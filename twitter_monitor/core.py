# -*- coding: UTF-8 -*-

from abc import ABCMeta
from abc import abstractmethod
import common
import datetime
import hashlib
import logging
import tweepy
import anydbm
import tempfile

# Module logger
logger = logging.getLogger(__name__)


class ExecutorFactory(common.loggable):
    """
    Factory to create an executor.
    """

    def __init__(self, routines,
                 twitter_keys, setup_default_logger=True):
        self.routines = routines
        self.twitter_keys = twitter_keys
        self.setup_default_logger = setup_default_logger

    def create_default(self):
        self._setup_logger()
        self.logger.debug("Creating a default Executor")

        notifier = self._create_notifier(self._create_twitter_api())

        executor = Executor(
            notifier, self.routines, self._create_key_value_store())

        return executor

    def _setup_logger(self):
        """
        Setup module logger to
        """
        if not self.setup_default_logger:
            return

        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s')

        handler = logging.StreamHandler()
        handler.setFormatter(formatter)

        logger = logging.getLogger("twitter_monitor")
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
            return anydbm.open(filename, "c")
        except Exception, e:
            pass

        return None


class Executor(common.loggable):
    """
    Responsable to run routines
    """

    def __init__(self, notifier, routines, key_value_store={}):
        self.notifier = notifier
        self.routines = routines
        self.key_value_store = key_value_store
        self._routines_instances = None

    def run(self):
        success = True

        try:
            for rt in self.routines_instances():
                self.logger.info(u"Running \"{}\"".format(unicode(rt)))

                if not rt.run():
                    self.logger.error(
                        u"Error on running routine \"{}\"".format(unicode(rt)))

                    success = False

                self.logger.info(u"Finished \"{}\"".format(unicode(rt)))
        except Exception, e:
            if (hasattr(self.key_value_store, "close")
                    and callable(getattr(self.key_value_store, "close"))):
                    self.key_value_store.close()

            self.logger.error("Error: " + e.message)
            success = False

        return success

    def routines_instances(self):
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


class Routine(common.loggable):
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
            self.__class__.__name__,
            self.name.encode("ascii", "ignore"),
            self.short_name.encode("ascii", "ignore"))

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
