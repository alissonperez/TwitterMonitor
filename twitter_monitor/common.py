# -*- coding: UTF-8 -*-

import logging


# Application's version
version = "1.0.1"


class loggable(object):
    """
    Include logger property in objects to handle log messages
    """

    _logger = None

    @property
    def logger(self):
        if self._logger is None:
            logger_name = "{}.{}".format(
                self.__class__.__module__,
                self.__class__.__name__)

            self._logger = logging.getLogger(logger_name)

        return self._logger

    @logger.setter
    def logger(self, logger):
        self._logger = logger


class Tc:
    """
    Terminal text with color.

    Usage:
    print(Tc('A warning message').warning)
    print(Tc('A fail message').fail)

    Available colors/formating:
    header
    okblue
    okgreen
    warning
    fail
    bold
    underline
    """

    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

    def __init__(self, message):
        self.message = message

    def __getattr__(self, name):
        name = name.upper()

        if not hasattr(self, name):
            raise Exception('Color \''+name+'\' not found')

        return getattr(self, name) + self.message + self.ENDC
