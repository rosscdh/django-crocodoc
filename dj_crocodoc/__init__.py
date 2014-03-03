# -*- coding: utf-8 -*-
from django.conf import settings


CROCDOC_API_KEY = getattr(settings, 'CROCDOC_API_KEY', None)
if CROCDOC_API_KEY is None:
    raise Exception("You must specify a CROCDOC_API_KEY in settings.py")