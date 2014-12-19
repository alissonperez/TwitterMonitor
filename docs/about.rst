About
=====

.. image:: https://travis-ci.org/alissonperez/TwitterMonitor.svg?branch=develop
 :target: https://travis-ci.org/alissonperez/TwitterMonitor :alt:Tests status

.. image:: https://coveralls.io/repos/alissonperez/TwitterMonitor/badge.png?branch=master
 :target: https://coveralls.io/r/alissonperez/TwitterMonitor?branch=master :alt:Code coverage status

.. image:: https://readthedocs.org/projects/twittermonitor/badge/?version=latest
 :target: https://readthedocs.org/projects/twittermonitor/?badge=latest :alt: Documentation Status

TwitterMonitor is a small open source library that creates any kind of monitoring routines using **Twitter direct messages (DM)**.

For each notification request, the library will take all the followers of the configured account and instantly send a DM to each one.

Please, send me a feedback: arp-pp@outlook.com.br

Code example
------------

There is an example below of a simple routine (RoutineTest class) that sends "A test message" to every account followers configured in the dictionary *twitter_keys* with a minimum interval of 10 minutes between each notification::

    from twitter_monitor import core


    # A simple routine example
    class RoutineTest(core.Routine):

        name = "Test Routine 1"  # Routine full name.
        short_name = "RT1"       # Routine short name (it'll be used in message).

        interval_minutes = 10     # You can put a execution interval in minutes

        def _execute(self):
            # Put your logic here and use self.notify (bellow) to send messages.
            self.notify("A test message...")


    # Manage your keys and tokens on https://apps.twitter.com/
    twitter_keys = {
        "consumer_key": "AaAaAaAaAaAaAaAaAaAaAaAaA",
        "consumer_secret": "AaAaAaAaAaAaAaAaAaAaAaAaAAaAaAaAaAaAaAaAaAaAaAaAaA",
        "access_token_key": "999999999-AaAaAaAaAaAaAaAaAaAaAaAaA",
        "access_token_secret": "AaAaAaAaAaAaAaAaAaAaAaAaAAaAaAaAaAaAaAaAaAaAaAaAaA",
    }

    # A list of routine classes
    routines = [
        RoutineTest
    ]

    core.ExecutorFactory(routines, twitter_keys).create_default().run()
