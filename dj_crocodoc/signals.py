# -*- coding: utf-8 -*-
"""
Webhook signals
"""
from django.dispatch import Signal, receiver

#
# Incoming events
#
send_to_crocodoc = Signal(providing_args=['document_object', 'app_label', 'field_name'])

#
# Outgoing Events
#
crocodoc_comment_create = Signal(providing_args=['verb', 'document', 'target', 'attachment_name', 'user_info', 'crocodoc_event'])
crocodoc_comment_delete = Signal(providing_args=['verb', 'document', 'target', 'attachment_name', 'user_info', 'crocodoc_event'])
crocodoc_annotation_highlight = Signal(providing_args=['verb', 'document', 'target', 'attachment_name', 'user_info', 'crocodoc_event'])
crocodoc_annotation_strikeout = Signal(providing_args=['verb', 'document', 'target', 'attachment_name', 'user_info', 'crocodoc_event'])
crocodoc_annotation_textbox = Signal(providing_args=['verb', 'document', 'target', 'attachment_name', 'user_info', 'crocodoc_event'])
crocodoc_annotation_drawing = Signal(providing_args=['verb', 'document', 'target', 'attachment_name', 'user_info', 'crocodoc_event'])
crocodoc_annotation_point = Signal(providing_args=['verb', 'document', 'target', 'attachment_name', 'user_info', 'crocodoc_event'])


@receiver(send_to_crocodoc)
def on_send_to_crocdoc(sender, document_object, app_label, field_name='attachment', upload_immediately=True, **kwargs):
    """
    Signal to create a crocodoc object
    """
    from .services import CrocoDocConnectService
    kwargs.update({'upload_immediately': upload_immediately})

    service = CrocoDocConnectService(document_object=document_object,
                                     app_label=app_label,
                                     field_name=field_name,
                                     **kwargs)