# -*- coding: utf-8 -*-
"""
Webhook signals
"""
from django.core.cache import cache
from django.dispatch import receiver

import dj_crocodoc.signals as crocodoc_signals


@receiver(crocodoc_signals.crocodoc_comment_create)
@receiver(crocodoc_signals.crocodoc_comment_delete)
@receiver(crocodoc_signals.crocodoc_annotation_highlight)
@receiver(crocodoc_signals.crocodoc_annotation_strikeout)
@receiver(crocodoc_signals.crocodoc_annotation_textbox)
@receiver(crocodoc_signals.crocodoc_annotation_drawing)
def test_crocodoc_webhook_event_recieved(**kwargs):
    """
    Test signal listner to handle the signal fired event
    """
    cache.set('test_crocodoc_webhook_event_recieved', kwargs.keys())