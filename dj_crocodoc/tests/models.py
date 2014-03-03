# -*- coding: utf-8 -*-
"""
Models used only for testing
"""
from django.db import models


class FakeDocumentObject(models.Model):
    my_document_field = models.FileField(upload_to='/tmp/')