TwitterMonitor
==============

[![Build Status](https://travis-ci.org/alissonperez/TwitterMonitor.svg)](https://travis-ci.org/alissonperez/TwitterMonitor) [![Coverage Status](https://coveralls.io/repos/alissonperez/TwitterMonitor/badge.png?branch=master)](https://coveralls.io/r/alissonperez/TwitterMonitor?branch=master)


Code Example
------------


```python
from twitter_monitor import core


# A simple routine example
class RoutineTest(core.Routine):

    name = "Rotina Test 1"
    short_name = "RT1"

    interval_minutes = 10  # You can put a execution interval in minutes

    def _execute(self):
        # Put your logic here
        self.notify("A test message...")


# Manage your keys and tokens on https://apps.twitter.com/
twitter_keys = {
    "consumer_key": "BgDcBAwKpVK7E5KO2fREeLB4i",
    "consumer_secret": "rtJdiZzD1aqKsdHH3z3GePkFp3ZVTurAYAjn59VWjGAI6QyiGp",
    "access_token_key": "2806285067-zH2Soc11qR6jObVUwA4KUIYrU7xpwQ0yWkkbFM7",
    "access_token_secret": "9LLywwkei4SWlkJx5kPvzww2KKaHHztShFxlcVEZ9BNnC",
}

# A list of routine classes
routines = [
    RoutineTest
]

core.ExecutorFactory(routines, twitter_keys).create_default().run()
```
