# -*- coding: UTF-8 -*-

from core import loggable


class Executor(loggable):
    """
    Responsable to run routines
    """

    def __init__(self, notifier, routines):
        self.notifier = notifier
        self.routines = routines

    def run(self):
        success = True

        for class_ref in self.routines:
            rt = class_ref(self.notifier)
            self.logger.info(u"Running \"{}\"".format(unicode(rt)))

            rt.logger = self.logger

            if not rt.run():
                self.logger.error(u"Error on running routine \"{}\"".format(unicode(rt)))
                success = False

            self.logger.info(u"Finished \"{}\"".format(unicode(rt)))

        return success