# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url
from django.views.decorators.csrf import csrf_exempt

from .views import CrocdocCallbackView


urlpatterns = patterns('',
    url(r'^webhook/$', csrf_exempt(CrocdocCallbackView.as_view()), name='callback'),
)
