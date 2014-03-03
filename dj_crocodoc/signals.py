# -*- coding: utf-8 -*-
"""
Webhook signals
"""
from django.dispatch import Signal, receiver
from django.contrib.contenttypes.models import ContentType

#
# Incoming events
#
send_to_crocodoc = Signal(providing_args=['document_object', 'app_label', 'field_name'])

#
# Outgoing Events
#
crocodoc_comment_create = Signal(providing_args=['verb', 'document', 'target', 'attachment_name'])
crocodoc_comment_delete = Signal(providing_args=['verb', 'document', 'target', 'attachment_name'])
crocodoc_annotation_highlight = Signal(providing_args=['verb', 'document', 'target', 'attachment_name'])
crocodoc_annotation_strikeout = Signal(providing_args=['verb', 'document', 'target', 'attachment_name'])
crocodoc_annotation_textbox = Signal(providing_args=['verb', 'document', 'target', 'attachment_name'])
crocodoc_annotation_drawing = Signal(providing_args=['verb', 'document', 'target', 'attachment_name'])
crocodoc_annotation_point = Signal(providing_args=['verb', 'document', 'target', 'attachment_name'])


@receiver(send_to_crocodoc)
def on_send_to_crocdoc(sender, document_object, app_label, field_name='attachment', **kwargs):
    from .models import CrocodocDocument
    #
    # Get the content_type of the passed in model
    #
    content_type = ContentType.objects.get(model=document_object.__class__.__name__.lower(),
                                           app_label='tests')
    #
    # Get or Create a new Crocodoc object associated with the document_object passed in
    #
    obj, is_new = CrocodocDocument.objects.get_or_create(content_object_type=content_type,
                                                         object_id=document_object.pk,
                                                         object_attachment_fieldname=field_name)
    # cause an upload to happen
    obj.crocodoc_service.uuid
