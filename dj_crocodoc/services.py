# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType

from .models import CrocodocDocument
import signals as crocodoc_signals

import json
import logging
from bunch import Bunch
logger = logging.getLogger('django.request')


class CrocoDocConnectService(object):
    """
    Service to setup a crocodoc object
    """
    obj = None
    is_new = None

    def __init__(self, document_object, app_label, field_name='attachment', **kwargs):
        upload = kwargs.get('upload_immediately', False)
        #
        # Get the content_type of the passed in model
        #
        content_type = ContentType.objects.get(model=document_object.__class__.__name__.lower(),
                                               app_label=app_label)
        #
        # Get or Create a new Crocodoc object associated with the document_object passed in
        #
        self.obj, self.is_new = CrocodocDocument.objects.get_or_create(content_object_type=content_type,
                                                                       object_id=document_object.pk,
                                                                       object_attachment_fieldname=field_name)
        if upload in [True, 'true', 1, '1']:
            # cause an upload to happen
            self.obj.crocodoc_service.uuid



class CrocodocWebhookService(object):
    payload = None

    def __init__(self, payload, *args, **kwargs):
        self.user = kwargs.get('user')
        self.payload = json.loads(payload)
        self.items = [Bunch(**i) for i in self.payload]

    def process(self):
        page = None

        for c, i in enumerate(self.items):

            event = i.get('event')
            event_type = i.get('type')

            if i.get('page') is not None:
                page = i.get('page')

            logger.info("{event} is of type {event_type} on page: {page}".format(event_type=event_type,
                                                                                 event=event,
                                                                                 page=page))

            if event == 'comment.create':
                i = CrocodocCommentCreateEvent(page=page, **i)

            elif event == 'comment.delete':
                i = CrocodocCommentDeleteEvent(**i)

            elif event in ['annotation.create', 'annotation.delete']:

                if event_type == 'textbox':
                    i = CrocodocAnnotationTextboxEvent(**i)

                elif event_type == 'highlight':
                    i = CrocodocAnnotationHighlightEvent(**i)

                elif event_type == 'strikeout':
                    i = CrocodocAnnotationStrikeoutEvent(**i)

                elif event_type == 'drawing':
                    i = CrocodocAnnotationDrawingEvent(**i)

                elif event_type == 'point':
                    i = CrocodocAnnotationPointEvent(**i)

            return i.process(sender=self) if hasattr(i, 'process') else None


class CrocodocBaseEvent(Bunch):
    signal = None
    _verb = None
    _deleted_verb = None
    _user = None
    _attachment = None
    label = 'Crocodoc Webhook Callback'
    content = None
    event = None
    type = None
    owner = None
    page = None
    doc = None
    uuid = None

    def __init__(self, *args, **kwargs):
        super(CrocodocBaseEvent, self).__init__(*args, **kwargs)
        self.__dict__.update(kwargs)  # @TODO ugly ugly ugly fix this

    @property
    def user(self):
        """ Crocodoc provides userid as string(pk,user_name)"""
        if self._user is None:
            pk, full_name = self.owner.split(',')
            pk = int(pk)
            self._user = User.objects.get(pk=pk)
        return self._user

    @property
    def attachment(self):
        if self._attachment is None:
            from .models import CrocodocDocument
            try:

                self._attachment = CrocodocDocument.objects.get(uuid=str(self.doc))  # must call str to make filter happen

            except CrocodocDocument.DoesNotExist:
                logger.critical('CrocodocDocument.DoesNotExist: %s' % self.doc)

        return self._attachment

    @property
    def verb(self):
        if self.event is not None and 'delete' in self.event:
            return self._deleted_verb
        else:
            return self._verb

    def process(self, sender):
        # try:
        document = self.attachment
        target = filename = None

        if document is not None:
            target = document.source_object
            #
            # We allow the fieldname to be variable and is specified at the model
            # level by setting object_attachment_fieldname but default to attachment
            #
            filename = getattr(target, document.object_attachment_fieldname, 'attachment').name

            self.signal.send(sender=sender,
                             verb=self.verb,
                             document=document,
                             target=target,
                             attachment_name=filename)
                             #**self.toDict())
            logger.info('Send signal: {signal} {verb}'.format(signal=self.signal.__class__.__name__, verb=self.verb))
            return True

        logger.error('No document could be found by that id: {doc}'.format(doc=str(self.doc)))
        return False


class CrocodocCommentCreateEvent(CrocodocBaseEvent):
    signal = crocodoc_signals.crocodoc_comment_create
    _verb = 'Commented on an Document'


class CrocodocCommentDeleteEvent(CrocodocBaseEvent):
    signal = crocodoc_signals.crocodoc_comment_delete
    _verb = 'Deleted a Commented on an Document'


class CrocodocAnnotationHighlightEvent(CrocodocBaseEvent):
    signal = crocodoc_signals.crocodoc_annotation_highlight
    _verb = 'Hilighted some text on an Document'
    _deleted_verb = 'Deleted a Hilighted of some text on an Document'


class CrocodocAnnotationStrikeoutEvent(CrocodocBaseEvent):
    signal = crocodoc_signals.crocodoc_annotation_strikeout
    _verb = 'Struck out some text on an Document'
    _deleted_verb = 'Deleted the Strikeout of some text on an Document'


class CrocodocAnnotationTextboxEvent(CrocodocBaseEvent):
    signal = crocodoc_signals.crocodoc_annotation_textbox
    _verb = 'Added a text element on an Document'
    _deleted_verb = 'Deleted a text element on an Document'


class CrocodocAnnotationDrawingEvent(CrocodocBaseEvent):
    signal = crocodoc_signals.crocodoc_annotation_drawing
    _verb = 'Added a drawing element on an Document'
    _deleted_verb = 'Deleted a drawing element on an Document'


class CrocodocAnnotationPointEvent(CrocodocBaseEvent):
    signal = crocodoc_signals.crocodoc_annotation_point
    _verb = 'Added a point element to a Document'
    _deleted_verb = 'Deleted a point element on an Document'
