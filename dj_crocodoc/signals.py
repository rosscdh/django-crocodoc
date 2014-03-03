# -*- coding: utf-8 -*-
"""
Webhook signals
"""
from django.dispatch import Signal

import logging
logger = logging.getLogger('django.request')


crocodoc_comment_create = Signal(providing_args=['verb', 'action_object', 'target', 'attachment_name'])
crocodoc_comment_delete = Signal(providing_args=['verb', 'action_object', 'target', 'attachment_name'])
crocodoc_annotation_highlight = Signal(providing_args=['verb', 'action_object', 'target', 'attachment_name'])
crocodoc_annotation_strikeout = Signal(providing_args=['verb', 'action_object', 'target', 'attachment_name'])
crocodoc_annotation_textbox = Signal(providing_args=['verb', 'action_object', 'target', 'attachment_name'])
crocodoc_annotation_drawing = Signal(providing_args=['verb', 'action_object', 'target', 'attachment_name'])
