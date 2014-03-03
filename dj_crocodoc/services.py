# -*- coding: utf-8 -*-
from django.contrib.auth.models import User

from .models import CrocodocDocument

import signals as crocodoc_signals

from bunch import Bunch

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
                             action_object=document,
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
