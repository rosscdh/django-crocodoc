# -*- coding: utf-8 -*-
"""
Webhook signals
"""
from django.core.cache import cache
from django.dispatch import receiver
from django.test import TestCase, Client
from django.core.urlresolvers import reverse
from django.contrib.contenttypes.models import ContentType

from .models import FakeDocumentObject
import data as crocodoc_data

from dj_crocodoc.models import CrocodocDocument
import dj_crocodoc.signals as crocodoc_signals

from tempfile import NamedTemporaryFile

import json


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


class WebhookTest(TestCase):
    endpoint = reverse('crocodoc_webhook_callback')

    def setUp(self):
        super(WebhookTest, self).setUp()
        self.client = Client()
        self.document_uuid = 'b15532bb-c227-40f6-939c-a244d123c717'
        #
        # Create Test document
        #
        self.attachment = FakeDocumentObject.objects.create(my_document_field='')

        ctype = ContentType.objects.get(model=self.attachment.__class__.__name__.lower(), app_label='tests')

        self.doc = CrocodocDocument.objects.create(uuid=self.document_uuid,
                                                   content_object_type=ctype,
                                                   object_id=self.attachment.pk,
                                                   object_attachment_fieldname='my_document_field')

    def send(self, data):
        return self.client.post(self.endpoint, {"payload": json.dumps(data)})

    def test_comment_create(self):
        resp = self.send(data=crocodoc_data.CROCODOC_COMMENT_CREATE)

        self.assertEqual(cache.get('test_crocodoc_webhook_event_recieved'), ['target', 'signal', 'verb', 'attachment_name', 'action_object', 'sender'])
        self.assertEqual(json.loads(resp.content), {"details": True})

    def test_annotation_highlight(self):
        resp = self.send(data=crocodoc_data.CROCODOC_ANNOTATION_HIGHLIGHT)
        self.assertEqual(cache.get('test_crocodoc_webhook_event_recieved'), ['target', 'signal', 'verb', 'attachment_name', 'action_object', 'sender'])
        self.assertEqual(json.loads(resp.content), {"details": True})

    def test_annotation_textbox(self):
        resp = self.send(data=crocodoc_data.CROCODOC_ANNOTATION_TEXTBOX)
        self.assertEqual(cache.get('test_crocodoc_webhook_event_recieved'), ['target', 'signal', 'verb', 'attachment_name', 'action_object', 'sender'])
        self.assertEqual(json.loads(resp.content), {"details": True})
