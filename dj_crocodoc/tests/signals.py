# -*- coding: utf-8 -*-
"""
Webhook signals
"""
#
# Required for reading files
#
import sys;
reload(sys);
sys.setdefaultencoding("utf8")

from django.conf import settings
from django.core.files import File
from django.core.cache import cache
from django.dispatch import receiver
from django.test import TestCase, Client
from django.core.urlresolvers import reverse
from django.contrib.contenttypes.models import ContentType

from ..services import CrocoDocConnectService

from .models import FakeDocumentObject
import data as crocodoc_data

from dj_crocodoc.models import CrocodocDocument
import dj_crocodoc.signals as crocodoc_signals

import os
import json
import codecs
import httpretty

TEST_PDF_PATH = os.path.join(os.path.dirname(__file__), 'test.pdf')

def GET_FAKE_DOC_OBJECT():
    base_object_attachment = FakeDocumentObject()

    with codecs.open(TEST_PDF_PATH, mode='r', encoding="ISO8859-1") as filename:
        base_object_attachment.my_document_field.save('test.pdf', File(filename))
    base_object_attachment.save()

    return base_object_attachment


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


def _ensure_object_has_correct_values(clazz, obj):
    """
    Test we have the right standard values
    used in all tests below
    """
    clazz.assertEqual(obj.content_object_type, ContentType.objects.get(model='fakedocumentobject', app_label='tests'))
    clazz.assertEqual(obj.object_attachment_fieldname, 'my_document_field')
    clazz.assertEqual(type(obj.source_object), FakeDocumentObject)  # should return the base object that created the request


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

    @httpretty.activate
    def test_signal_provides_a_new_model(self):
        #
        # Crocdoc
        #
        httpretty.register_uri(httpretty.POST, "https://crocodoc.com/api/v2/document/upload",
                       body='{"success": true, "uuid": "b15532bb-c227-40f6-939c-a244d123c717"}',
                       status=200)


        base_object_attachment = GET_FAKE_DOC_OBJECT()

        self.assertEqual(CrocodocDocument.objects.all().count(), 0)

        self.subject.send(sender=self,
                          document_object=base_object_attachment,
                          app_label='tests',
                          field_name='my_document_field')

        # Success, we Created a new CrocodocDocument object from the signal
        self.assertEqual(CrocodocDocument.objects.all().count(), 1)
        obj = CrocodocDocument.objects.all().first()

        self.assertEqual(str(obj.uuid), 'b15532bb-c227-40f6-939c-a244d123c717')  # as we have yet to call the upload process on it
        _ensure_object_has_correct_values(clazz=self, obj=obj)


class CrocoDocConnectServiceTest(TestCase):
    """
    Test we can use the CrocoDocConnectService directly
    """
    subject = CrocoDocConnectService

    @httpretty.activate
    def test_service_provides_a_model_with_upload_immediately_false(self):
        """
        Note the CrocoDocConnectService will not upload_immediately unless u
        specify upload_immediately=True
        """
        #
        # Crocdoc
        #
        httpretty.register_uri(httpretty.POST, "https://crocodoc.com/api/v2/document/upload",
                       body='{"success": true, "uuid": "b15532bb-c227-40f6-939c-a244d123c717"}',
                       status=200)

        base_object_attachment = GET_FAKE_DOC_OBJECT()

        self.assertEqual(CrocodocDocument.objects.all().count(), 0)

        self.subject(document_object=base_object_attachment, app_label='tests', field_name='my_document_field')

        # Success, we Created a new CrocodocDocument object from the signal
        self.assertEqual(CrocodocDocument.objects.all().count(), 1)
        obj = CrocodocDocument.objects.all().first()

        self.assertEqual(obj.uuid, None)  # Service does not upload right away
        _ensure_object_has_correct_values(clazz=self, obj=obj)

    @httpretty.activate
    def test_service_provides_a_model_with_upload_immediately_true(self):
        """
        Note the CrocoDocConnectService will not upload_immediately unless u
        specify upload_immediately=True
        """
        #
        # Crocdoc
        #
        httpretty.register_uri(httpretty.POST, "https://crocodoc.com/api/v2/document/upload",
                       body='{"success": true, "uuid": "b15532bb-c227-40f6-939c-a244d123c717"}',
                       status=200)

        base_object_attachment = GET_FAKE_DOC_OBJECT()

        self.assertEqual(CrocodocDocument.objects.all().count(), 0)

        service = self.subject(document_object=base_object_attachment,
                               app_label='tests',
                               field_name='my_document_field',
                               upload_immediately=True)

        # Success, we Created a new CrocodocDocument object from the signal
        self.assertEqual(CrocodocDocument.objects.all().count(), 1)
        obj = CrocodocDocument.objects.all().first()

        self.assertEqual(str(obj.uuid), 'b15532bb-c227-40f6-939c-a244d123c717')  # Service does not upload right away
        _ensure_object_has_correct_values(clazz=self, obj=obj)

