# -*- coding: utf-8 -*-
from django.contrib import admin

from .models import CrocodocDocument


class CrocodocDocumentAdmin(admin.ModelAdmin):
    list_display = ('uuid',)
    list_filter = ('content_object_type',)
    search_fields = ('uuid',)


admin.site.register(CrocodocDocument, CrocodocDocumentAdmin)
