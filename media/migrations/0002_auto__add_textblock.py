# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'TextBlock'
        db.create_table('media_textblock', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('content', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('media', ['TextBlock'])


    def backwards(self, orm):
        
        # Deleting model 'TextBlock'
        db.delete_table('media_textblock')


    models = {
        'media.image': {
            'Meta': {'object_name': 'Image'},
            'alt_text': ('django.db.models.fields.CharField', [], {'max_length': '1024', 'blank': 'True'}),
            'attribution': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'category': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'media_image_related'", 'null': 'True', 'to': "orm['media.ImageCategory']"}),
            'file': ('django.db.models.fields.files.ImageField', [], {'max_length': '255'}),
            'height': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'width': ('django.db.models.fields.PositiveIntegerField', [], {})
        },
        'media.imagecategory': {
            'Meta': {'object_name': 'ImageCategory'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'media.textblock': {
            'Meta': {'object_name': 'TextBlock'},
            'content': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        }
    }

    complete_apps = ['media']
