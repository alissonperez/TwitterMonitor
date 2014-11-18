TwitterMonitor
==============

[![Build Status](https://travis-ci.org/alissonperez/TwitterMonitor.svg)](https://travis-ci.org/alissonperez/TwitterMonitor) [![Coverage Status](https://coveralls.io/repos/alissonperez/TwitterMonitor/badge.png?branch=master)](https://coveralls.io/r/alissonperez/TwitterMonitor?branch=master)

TwitterMonitor é uma pequena biblioteca open source para criar rotinas de monitoramento de qualquer natureza usando o envio de mensagens (*direct messages* ou simplesmente *DM*) do *Twitter* (http://twitter.com).

Para cada solicitação de envio de mensagem a biblioteca obterá **todos** os seguidores da conta configurada e enviará uma DM para cada um de forma automática.

Abaixo segue um exemplo de uma rotina simples (classe **RoutineTest**) que envia a mensagem "A test message" para todos os seguidores da conta configurada no dicionário *twitter_keys* em um intervalo de no mínimo 10 minutos entre cada notificação.


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
```
