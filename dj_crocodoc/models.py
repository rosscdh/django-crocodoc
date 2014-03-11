# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.contenttypes.models import ContentType

from mixins import CrocodocService

from uuidfield import UUIDField
from jsonfield import JSONField


class CrocodocDocument(models.Model):
    uuid = UUIDField(hyphenate=True, blank=True, null=True, db_index=True)
    # content type of the object, used to do lookups as .source_object
    content_object_type = models.ForeignKey('contenttypes.ContentType', db_index=True)
    # id of the specific object
    object_id = models.IntegerField(db_index=True)
    # used to specify the name of the FileField
    object_attachment_fieldname = models.CharField(max_length=255, default='attachment')
    # misc data
    data = JSONField(default={}, blank=True, null=True)

    _crocodoc_service = None

    @property
    def crocodoc_uuid(self):
        return self.data.get('crocodoc', {}).get('uuid')

    def get_url(self):
        return getattr(self.source_object, self.object_attachment_fieldname, 'attachment').url

    @property
    def crocodoc_service(self):
        if self._crocodoc_service is None:
            #
            # Pass in the source object with the attachment field
            #
            self._crocodoc_service = CrocodocService(attachment=self, source_object=self.source_object, attachment_field_name=self.object_attachment_fieldname)
        return self._crocodoc_service

    @property
    def source_object(self):
        """
        Return the object refered to by content_object_type and content_object_id
        """
        return self.content_object_type.get_object_for_this_type(pk=self.object_id)



"""
Import the one INCOMING signal which we recieve and process
"""
from .signals import (on_send_to_crocdoc,)