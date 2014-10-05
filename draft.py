#!/usr/bin/python
# -*- coding: UTF-8 -*-

import logging
from abc import ABCMeta
from abc import abstractmethod


"""
Rascunho de uma aplicação simples de rotinas de monitoramento
integradas ao Twitter

Alisson R. Perez
"""


def api_creator():
    """
    Criação da API com o Twitter usando a lib tweepy
    """

    import tweepy

    consumer_key = ""
    consumer_secret = ""
    access_token_key = ""
    access_token_secret = ""

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token_key, access_token_secret)

    return tweepy.API(auth)


def create_logger():
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s')

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)

    logger = logging.getLogger(__name__)
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)

    return logger


class loggable(object):
    """
    Um objeto "logável"
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


class notifier(loggable):
    """
    Responsável por enviar a mensagem aos destinatários (seguidores) por meio
    da API do Twitter
    """

    def __init__(self, api):
        self._api = api

        # Cache dos seguidores...
        self._followers = None

    def send(self, message):
        self.logger.debug("Mensagem para enviar: \"{}\"".format(message))

        if message is None or not isinstance(message, str):
            self.logger.debug("Mensagem inválida")
            return

        if len(message.strip()) == 0:
            self.logger.debug("É vazia")
            return

        for follower in self._get_followers():
            self.logger.info("Enviando mensagem para \"{}\": \"{}\"".format(
                follower.screen_name, message))

            self._api.send_direct_message(user_id=follower.id, text=message)

    def _get_followers(self):
        if self._followers is None:
            self._followers = self._api.followers()

        return self._followers


class routine(loggable):
    """
    Representação de uma rotina
    """

    __metaclass__ = ABCMeta

    name = None            # Nome completo da rotina

    short_name = None      # Nome curto (usado o no Twit)

    def __init__(self, notifier):
        self.notifier = notifier

        if self.name is None:
            self.name = self.__class__.__name__

        if self.short_name is None:
            self.short_name = self.__class__.__name__

    @abstractmethod
    def run(self):
        return NotImplemented

    def notify(self, message):
        if message is None or not isinstance(message, str):
            self.logger.debug("Mensagem é inválida")
            return

        if len(message.strip()) == 0:
            self.logger.debug("É vazia")
            return

        new_message = "{}: {}".format(
            self.short_name, message)

        self.notifier.send(new_message)

    def __str__(self):
        return "Routine '{}'".format(self.name)


class runner(loggable):
    """
    Responsável por executar as rotinas
    """

    def __init__(self, notifier, routines):
        self.notifier = notifier
        self.routines = routines

    def run(self):
        for class_ref in self.routines:
            rt = class_ref(self.notifier)
            self.logger.info("Executando \"{}\"".format(str(rt)))
            rt.logger = self.logger
            rt.run()


class test_routine1(routine):
    """
    Implementação concreta de uma rotina
    """

    name = "Rotina 1"
    short_name = "ROT1"

    def run(self):
        self.notify("OK")


class test_routine2(routine):
    """
    Implementação concreta de uma rotina
    """

    name = "Rotina 2"
    short_name = "ROT2"

    def run(self):
        self.notify("ERRO, verificar")


if __name__ == "__main__":
    logger = create_logger()

    n = notifier(api_creator())
    n.logger = logger

    routines = [test_routine1, test_routine2]

    obj_runner = runner(n, routines)
    obj_runner.logger = logger
    obj_runner.run()
