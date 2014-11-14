# -*- coding: UTF-8 -*-

import unicodedata
import re


def slugfy(value):
    """
    Normalize a string.
    Eg.:
        "Alisson dos Reis Perez" to "alisson-dos-reis-perez"
        "  Verificação de  Fichas" to "verificacao-de-fichas"
    """

    value = unicode(value)
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore')
    value = unicode(re.sub('[^\w\s-]', '', value).strip().lower())
    return re.sub('[-\s]+', '-', value)
