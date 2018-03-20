# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.apps import AppConfig

from app.signals import hello_signal
from app.signals.handlers import print_hello


import hashlib

class AppConfig(AppConfig):
    name = 'app'
    def ready(self):
        func_uid = hashlib.sha256('print_hello'.encode()).hexdigest()
        hello_signal.connect(print_hello, dispatch_uid=func_uid)