# -*- coding: UTF-8 -*-

import logging

# Application's version
version = "1.0.0"


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