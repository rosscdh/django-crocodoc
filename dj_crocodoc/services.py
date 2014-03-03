# -*- coding: utf-8 -*-
from django.contrib.auth.models import User

from glynt.apps.todo.models import Attachment

from bunch import Bunch
from actstream import action

import json
import logging
logger = logging.getLogger('lawpal.services')


class CrocdocAttachmentService(object):
    """
    Service to manage uploading and general attribs of corcdoc attachments
    """
    attachment = None
    session = None

    def __init__(self, attachment, *args, **kwargs):
        logger.info('Init CrocdocAttachmentService.__init__ for attachment: {pk}'.format(pk=attachment.pk))
        self.attachment = attachment

    @property
    def uuid(self):
        """
        Calling this property will initiate an upload of the doc,
        if it has not already been uploaded (i.e. we have a crocdoc uuid in the json data)
        """
        if self.attachment.crocdoc_uuid is None:

            try:
                uuid = self.upload_document()
                logger.info('CrocdocAttachmentService.uuid: {uuid}'.format(uuid=uuid))

            except Exception as e:
                logger.error('CrocdocAttachmentService.uuid: Failed to Generate uuid')
                raise e

            crocdoc = self.attachment.data.get('crocdoc', {})
            crocdoc['uuid'] = uuid

            self.attachment.uuid = uuid

            self.attachment.data['crocdoc'] = crocdoc
            self.attachment.save(update_fields=['uuid', 'data'])

            return uuid
        else:
            return self.attachment.crocdoc_uuid

    def session_key(self, **kwargs):
        if self.session is None:
            self.session = '123-123-123' if settings.PROJECT_ENVIRONMENT == 'test' else crocodoc.session.create(self.uuid, **kwargs)
        return self.session

    def upload_document(self):
        url = self.attachment.get_url()
        logger.info('Upload file to crocdoc: {url}'.format(url=url))
        return crocodoc.document.upload(url=url)

    def view_url(self):
        url = 'http://example.com' if settings.PROJECT_ENVIRONMENT == 'test' else 'https://crocodoc.com/view/{session_key}'.format(session_key=self.session_key())
        logger.info('provide crocdoc view_url: {url}'.format(url=url))
        return url

    def remove(self):
        # delete from crocdoc based on uuid
        deleted = crocodoc.document.delete(self.attachment.crocdoc_uuid)
        if deleted:
            logger.info('Deleted crocdoc file: {pk} - {uuid}'.format(pk=self.attachment.pk, uuid=self.attachment.crocdoc_uuid))
        else:
            logger.error('Could not Delete crocdoc file: {pk} - {uuid}'.format(pk=self.attachment.pk, uuid=self.attachment.crocdoc_uuid))

    def process(self):
        logger.info('Start CrocdocAttachmentService.process')
        return self.uuid


class CrocdocWebhookService(object):
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
                i = CrocdocCommentCreateEvent(page=page, **i)

            elif event == 'comment.delete':
                i = CrocdocCommentDeleteEvent(**i)

            elif event in ['annotation.create', 'annotation.delete']:
                if event_type == 'textbox':
                    i = CrocdocAnnotationTextboxEvent(**i)

                elif event_type == 'highlight':
                    i = CrocdocAnnotationHighlightEvent(**i)

                elif event_type == 'strikeout':
                    i = CrocdocAnnotationStrikeoutEvent(**i)

                elif event_type == 'drawing':
                    i = CrocdocAnnotationDrawingEvent(**i)


            i.process() if hasattr(i, 'process') else None


class CrocdocBaseEvent(Bunch):
    _verb = None
    _deleted_verb = None
    _user = None
    _attachment = None
    label = 'Crocdoc Webhook Callback'
    content = None
    event = None
    type = None
    owner = None
    page = None
    doc = None
    uuid = None

    def __init__(self, *args, **kwargs):
        super(CrocdocBaseEvent, self).__init__(*args, **kwargs)
        self.__dict__.update(kwargs)

    @property
    def user(self):
        """ Crocdoc provides userid as string(pk,user_name)"""
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
        if 'delete' in self.event:
            return self._deleted_verb
        else:
            return self._verb

    def process(self):
        try:
            action.send(self.user, 
                        verb=self.verb,
                        action_object=self.attachment, 
                        target=self.attachment.todo,
                        attachment_name=self.attachment.filename,
                        **self.toDict())
        except Exception as e:
            logger.error('There was an exception with the CrocdocWebhookService: {error}'.format(error=e))


class CrocdocCommentCreateEvent(CrocdocBaseEvent):
    _verb = 'Commented on an Attachment'


class CrocdocCommentDeleteEvent(CrocdocBaseEvent):
    _verb = 'Deleted a Commented on an Attachment'


class CrocdocAnnotationHighlightEvent(CrocdocBaseEvent):
    _verb = 'Hilighted some text on an Attachment'
    _deleted_verb = 'Deleted a Hilighted of some text on an Attachment'


class CrocdocAnnotationStrikeoutEvent(CrocdocBaseEvent):
    _verb = 'Struck out some text on an Attachment'
    _deleted_verb = 'Deleted the Strikeout of some text on an Attachment'


class CrocdocAnnotationTextboxEvent(CrocdocBaseEvent):
    _verb = 'Added a text element on an Attachment'
    _deleted_verb = 'Deleted a text element on an Attachment'


class CrocdocAnnotationDrawingEvent(CrocdocBaseEvent):
    _verb = 'Added a drawing element on an Attachment'
    _deleted_verb = 'Deleted a drawing element on an Attachment'
