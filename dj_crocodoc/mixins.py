# -*- coding: utf-8 -*-
from django.core.validators import URLValidator
from django.core.files.storage import default_storage
from django.core.exceptions import ValidationError

from . import CROCDOC_API_KEY
import logging
import crocodoc as CROCODOC_BASE_SERVICE
logger = logging.getLogger('django.request')


CROCODOC_BASE_SERVICE.api_token = CROCDOC_API_KEY


class CrocodocService(object):
    """
    Service to manage uploading and general attribs of corcdoc attachments
    """
    attachment = None
    session = None

    def __init__(self, attachment, source_object, attachment_field_name, *args, **kwargs):
        logger.info('Init CrocodocAttachmentService.__init__ for attachment: {pk}'.format(pk=attachment.pk))
        self.attachment = attachment
        self.source_object = source_object
        self.attachment_field_name = attachment_field_name

    @property
    def uuid(self):
        """
        Calling this property will initiate an upload of the doc,
        if it has not already been uploaded (i.e. we have a crocodoc uuid in the json data)
        """
        crocodoc_uuid = self.attachment.crocodoc_uuid

        if crocodoc_uuid is None:

            try:
                crocodoc_uuid = self.upload_document()
                logger.info('CrocodocAttachmentService.uuid: {uuid}'.format(uuid=crocodoc_uuid))

            except Exception as e:
                logger.error('CrocodocAttachmentService.uuid: Failed to Generate uuid')
                raise e

            crocodoc_data = self.attachment.data.get('crocodoc', {})

            crocodoc_data['uuid'] = crocodoc_uuid
            self.attachment.uuid = crocodoc_uuid

            self.attachment.data['crocodoc'] = crocodoc_data
            self.attachment.save(update_fields=['uuid', 'data'])

        return crocodoc_uuid

    def session_key(self, **kwargs):
        #if self.session is None:
        if 1:
            self.session = CROCODOC_BASE_SERVICE.session.create(self.uuid, **kwargs)
            logger.info('Session start:crocodoc: {session}'.format(session=self.session))
        return self.session

    def upload_document(self):
        validate = URLValidator()
        url = self.attachment.get_url()

        try:
            #
            # validate taht we are using a url
            #
            validate(url)
            logger.info('Upload url:file to crocodoc: {url}'.format(url=url))
            #
            # @TODO download the file locally? instead of trying to upload as a url?
            #
            return CROCODOC_BASE_SERVICE.document.upload(url=url)

        except ValidationError, e:
            #
            # was not a url is a patch
            #
            logger.info('Upload file to crocodoc: {url}'.format(url=url))
            #return CROCODOC_BASE_SERVICE.document.upload(file=codecs.open(url, mode='r', encoding="ISO8859-1"))
            return CROCODOC_BASE_SERVICE.document.upload(file=default_storage.open(url))

        

    def view_url(self, **kwargs):
        """
        Please see: https://crocodoc.com/docs/api/#session-create
        for a list of the session kwargs that are accepted
        filter=[1,5,3,7] a list of user ids that can see the document commments
        """
        url = 'https://crocodoc.com/view/{session_key}'.format(session_key=self.session_key(**kwargs))
        logger.info('provide crocodoc view_url: {url}'.format(url=url))
        return url

    def remove(self):
        # delete from crocodoc based on uuid
        deleted = CROCODOC_BASE_SERVICE.document.delete(self.attachment.crocodoc_uuid)

        if deleted:
            logger.info('Deleted crocodoc file: {pk} - {uuid}'.format(pk=self.attachment.pk, uuid=self.attachment.crocodoc_uuid))

        else:
            logger.error('Could not Delete crocodoc file: {pk} - {uuid}'.format(pk=self.attachment.pk, uuid=self.attachment.crocodoc_uuid))

    def process(self):
        logger.info('Start CrocodocAttachmentService.process')
        return self.uuid