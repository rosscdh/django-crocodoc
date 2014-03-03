# -*- coding: utf-8 -*-
from django.contrib.auth.models import User

from .models import CrocodocDocment

from bunch import Bunch
import signals as crocodoc_signals

import json
import logging
logger = logging.getLogger('django.request')


class CrocodocService(object):
    """
    Service to manage uploading and general attribs of corcdoc attachments
    """
    attachment = None
    session = None

    def __init__(self, attachment, *args, **kwargs):
        logger.info('Init CrocodocAttachmentService.__init__ for attachment: {pk}'.format(pk=attachment.pk))
        self.attachment = attachment

    @property
    def uuid(self):
        """
        Calling this property will initiate an upload of the doc,
        if it has not already been uploaded (i.e. we have a crocodoc uuid in the json data)
        """
        if self.attachment.crocodoc_uuid is None:

            try:
                uuid = self.upload_document()
                logger.info('CrocodocAttachmentService.uuid: {uuid}'.format(uuid=uuid))

            except Exception as e:
                logger.error('CrocodocAttachmentService.uuid: Failed to Generate uuid')
                raise e

            crocodoc = self.attachment.data.get('crocodoc', {})
            crocodoc['uuid'] = uuid

            self.attachment.uuid = uuid

            self.attachment.data['crocodoc'] = crocodoc
            self.attachment.save(update_fields=['uuid', 'data'])

            return uuid
        else:
            return self.attachment.crocodoc_uuid

    def session_key(self, **kwargs):
        if self.session is None:
            self.session = '123-123-123' if settings.PROJECT_ENVIRONMENT == 'test' else crocodoc.session.create(self.uuid, **kwargs)
        return self.session

    def upload_document(self):
        url = self.attachment.get_url()
        logger.info('Upload file to crocodoc: {url}'.format(url=url))
        return crocodoc.document.upload(url=url)

    def view_url(self):
        url = 'http://example.com' if settings.PROJECT_ENVIRONMENT == 'test' else 'https://crocodoc.com/view/{session_key}'.format(session_key=self.session_key())
        logger.info('provide crocodoc view_url: {url}'.format(url=url))
        return url

    def remove(self):
        # delete from crocodoc based on uuid
        deleted = crocodoc.document.delete(self.attachment.crocodoc_uuid)
        if deleted:
            logger.info('Deleted crocodoc file: {pk} - {uuid}'.format(pk=self.attachment.pk, uuid=self.attachment.crocodoc_uuid))
        else:
            logger.error('Could not Delete crocodoc file: {pk} - {uuid}'.format(pk=self.attachment.pk, uuid=self.attachment.crocodoc_uuid))

    def process(self):
        logger.info('Start CrocodocAttachmentService.process')
        return self.uuid


class CrocodocWebhookService(object):
    payload = None

    def __init__(self, payload=payload, *args, **kwargs):
        self.user = kwargs.get('user')
        self.payload = json.loads(payload)
        self.items = [Bunch(**i) for i in self.payload]

    def process(self):
        page = None
        for c, i in enumerate(self.items):
            #print '{num}: Item: {i}'.format(num=c, i=i)
            event = i.get('event')
            event_type = i.get('type')
            if i.get('page') is not None:
                page = i.get('page')

            logger.info("{event} is of type {event_type} on page: {page}".format(event_type=event_type, event=event, page=page))

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


            i.process() if hasattr(i, 'process') else None


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
        self.__dict__.update(kwargs)

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
            self._attachment = Attachment.objects.get(uuid=self.doc)
        return self._attachment

    @property
    def verb(self):
        if self.event is not None and 'delete' in self.event:
            return self._deleted_verb
        else:
            return self._verb

    def process(self):
        try:

            self.signal.send(verb=self.verb,
                             action_object=self.attachment, 
                             target=self.attachment.todo,
                             attachment_name=self.attachment.filename,
                             **self.toDict())

        except Exception as e:
            logger.error('There was an exception with the CrocodocWebhookService: {error}'.format(error=e))


class CrocodocCommentCreateEvent(CrocodocBaseEvent):
    signal = crocodoc_signals.crocodoc_comment_create
    _verb = 'Commented on an Attachment'


class CrocodocCommentDeleteEvent(CrocodocBaseEvent):
    signal = crocodoc_signals.crocodoc_comment_delete
    _verb = 'Deleted a Commented on an Attachment'


class CrocodocAnnotationHighlightEvent(CrocodocBaseEvent):
    signal = crocodoc_signals.crocodoc_annotation_highlight
    _verb = 'Hilighted some text on an Attachment'
    _deleted_verb = 'Deleted a Hilighted of some text on an Attachment'


class CrocodocAnnotationStrikeoutEvent(CrocodocBaseEvent):
    signal = crocodoc_signals.crocodoc_annotation_strikeout
    _verb = 'Struck out some text on an Attachment'
    _deleted_verb = 'Deleted the Strikeout of some text on an Attachment'


class CrocodocAnnotationTextboxEvent(CrocodocBaseEvent):
    signal = crocodoc_signals.crocodoc_annotation_textbox
    _verb = 'Added a text element on an Attachment'
    _deleted_verb = 'Deleted a text element on an Attachment'


class CrocodocAnnotationDrawingEvent(CrocodocBaseEvent):
    signal = crocodoc_signals.crocodoc_annotation_drawing
    _verb = 'Added a drawing element on an Attachment'
    _deleted_verb = 'Deleted a drawing element on an Attachment'
