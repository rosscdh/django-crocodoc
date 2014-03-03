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


class BaseContentProvider(TestCase):
    def setUp(self):
        super(BaseContentProvider, self).setUp()
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

class WebhookTest(BaseContentProvider):
    """
    Test the basic webhook callbacks (emulate a POST form crocodoc)
    """
    endpoint = reverse('crocodoc_webhook_callback')

    def send(self, data):
        """
        crocodoc wrap all webhooks in a payload object for some reason
        and a basic post
        """
        return self.client.post(self.endpoint, {"payload": json.dumps(data)})

    def test_comment_create(self):
        resp = self.send(data=crocodoc_data.CROCODOC_COMMENT_CREATE)
        self.assertEqual(cache.get('test_crocodoc_webhook_event_recieved'), ['target', 'signal', 'verb', 'attachment_name', 'document', 'sender'])
        self.assertEqual(json.loads(resp.content), {"details": True})

    def test_annotation_highlight(self):
        resp = self.send(data=crocodoc_data.CROCODOC_ANNOTATION_HIGHLIGHT)
        self.assertEqual(cache.get('test_crocodoc_webhook_event_recieved'), ['target', 'signal', 'verb', 'attachment_name', 'document', 'sender'])
        self.assertEqual(json.loads(resp.content), {"details": True})

    def test_annotation_textbox(self):
        resp = self.send(data=crocodoc_data.CROCODOC_ANNOTATION_TEXTBOX)
        self.assertEqual(cache.get('test_crocodoc_webhook_event_recieved'), ['target', 'signal', 'verb', 'attachment_name', 'document', 'sender'])
        self.assertEqual(json.loads(resp.content), {"details": True})


class IncomingSignalTest(TestCase):
    """
    Test we can issue a signal and have that signal provide us with an appropriate model
    """
    subject = crocodoc_signals.send_to_crocodoc

    def test_signal_provides_a_new_model(self):
        base_object_attachment = FakeDocumentObject.objects.create(my_document_field='')

        self.assertEqual(CrocodocDocument.objects.all().count(), 0)

        self.subject.send(sender=self, document_object=base_object_attachment, app_label='tests', field_name='my_document_field')

        # Success, we Created a new CrocodocDocument object from the signal
        self.assertEqual(CrocodocDocument.objects.all().count(), 1)
        obj = CrocodocDocument.objects.all().first()

        self.assertEqual(obj.uuid, None)  # as we have yet to call the upload process on it
        self.assertEqual(obj.content_object_type, ContentType.objects.get(model='fakedocumentobject', app_label='tests'))
        self.assertEqual(obj.object_id, 1)
        self.assertEqual(obj.object_attachment_fieldname, 'my_document_field')
