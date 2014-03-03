# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.contenttypes.models import ContentType

from uuidfield import UUIDField
from jsonfield import JSONField


class CrocodocDocument(models.Model):
    uuid = UUIDField(db_index=True)
    # content type of the object, used to do lookups as .source_object
    content_object_type = models.ForeignKey('contenttypes.ContentType', db_index=True)
    # id of the specific object
    object_id = models.IntegerField(db_index=True)
    # used to specify the name of the FileField
    object_attachment_fieldname = models.CharField(max_length=255)
    # misc data
    data = JSONField(default={}, blank=True, null=True)

    @property
    def source_object(self):
        """
        Return the object refered to by content_object_type and content_object_id
        """
        return self.content_object_type.get_object_for_this_type(pk=self.object_id)