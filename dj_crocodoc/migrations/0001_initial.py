# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'CrocodocDocument'
        db.create_table(u'dj_crocodoc_crocodocdocument', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('uuid', self.gf('uuidfield.fields.UUIDField')(db_index=True, max_length=32, null=True, blank=True)),
            ('content_object_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'])),
            ('object_id', self.gf('django.db.models.fields.IntegerField')(db_index=True)),
            ('object_attachment_fieldname', self.gf('django.db.models.fields.CharField')(default='attachment', max_length=255)),
            ('data', self.gf('jsonfield.fields.JSONField')(default={}, null=True, blank=True)),
        ))
        db.send_create_signal(u'dj_crocodoc', ['CrocodocDocument'])


    def backwards(self, orm):
        # Deleting model 'CrocodocDocument'
        db.delete_table(u'dj_crocodoc_crocodocdocument')


    models = {
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'dj_crocodoc.crocodocdocument': {
            'Meta': {'object_name': 'CrocodocDocument'},
            'content_object_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            'data': ('jsonfield.fields.JSONField', [], {'default': '{}', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_attachment_fieldname': ('django.db.models.fields.CharField', [], {'default': "'attachment'", 'max_length': '255'}),
            'object_id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True'}),
            'uuid': ('uuidfield.fields.UUIDField', [], {'db_index': 'True', 'max_length': '32', 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['dj_crocodoc']