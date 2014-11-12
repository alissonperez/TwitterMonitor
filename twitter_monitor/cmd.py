# -*- coding: UTF-8 -*-


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