""" IxC extensions to FeinCMS. May perhaps be pushed back to FeinCMS core """
import os

from django.conf import settings
from django.db import models
from django.utils.translation import ugettext as _
from easy_thumbnails.files import get_thumbnailer

from base import *
from forms import TextileContentAdminForm, ImageForm

#__all__ = ['TextContent', 'DownloadableContent', 'ImageContent', 'AudioContent', 'VideoContent']

class Reusable(object):
	__metaclass__ = ReusableBase
	
	class Meta:
		abstract = True

class OneOff(object):
	__metaclass__ = OneOffBase
	
	class Meta:
		abstract = True

MAX_ALT_TEXT_LENGTH = 1024

UPLOAD_PATH = getattr(settings, 'UPLOAD_PATH', 'uploads/')

class TextContent(models.Model):
	content = models.TextField()

	formatter = lambda x: x
	content_field_name = 'text_block'
	
	class Meta:
		abstract = True
		verbose_name = _("Text Block")

	def render(self, **kwargs):
		# this should possibly be done via a call to smartembed/textile
		# methods directly; just directly replacing the templatetag for now
		return self.formatter(self.content)

	form = TextileContentAdminForm
	feincms_item_editor_form = TextileContentAdminForm
	
	feincms_item_editor_includes = {
		'head': [ 'feincmstools/textilecontent/init.html' ],
		}
	

class DownloadableContent(models.Model):
	link_text = models.CharField(max_length=255)
	downloadable = models.FileField(upload_to=UPLOAD_PATH+'file/%Y/%m/%d/')
	include_icon = models.BooleanField(default=True)
	
	content_field_name = 'file'
	
	def get_file_name(self):
		return (os.path.split(self.downloadable.file.name)[1])

	def get_file_extension(self):
		extension = os.path.splitext(self.downloadable.file.name)[1][1:].lower()
		if extension in ['ppt','pptx','pptm','pot','potx','potm','pps','ppsx','ppsm','key']:
			extension = 'ppt'
		elif extension in ['pdf']:
			extension = 'pdf'
		else:
			extension = 'generic'
		return extension

	class Meta:
		abstract = True
		verbose_name = "Downloadable File"
		verbose_name_plural = "Downloadable Files"

	# def render(self, **kwargs):
	#	 downloadable = self.downloadable
	#	 template = get_template("lumpypages/downloadable.html")
	#	 c = Context({'downloadable': {'file': self.downloadable, 'link_text': self.link_text, 'include_icon': self.include_icon, 'filename': self.get_file_name(), 'file_extension': self.get_file_extension()}})
	#	 return template.render(c)

# --- Media models ------------------------------------------------------------

class ImageContent(models.Model):
	file = models.ImageField(upload_to=UPLOAD_PATH+'images/%Y/%m/%d/',
							 height_field='file_height', width_field='file_width',
							 max_length=255)
	file_height = models.PositiveIntegerField(editable=False)
	file_width = models.PositiveIntegerField(editable=False)
	alt_text = models.CharField('Alternate text', blank=True,
								max_length=MAX_ALT_TEXT_LENGTH,
								help_text= 'Description of the image content')
#	attribution = models.CharField(max_length=255, blank=True)
	
	form_base = ImageForm
	content_field_name = 'image'

	class Meta:
		abstract = True
	
	def get_thumbnail(self, **kwargs):
		options = dict(size=(100, 100), crop=True)
		options.update(kwargs)
		return get_thumbnailer(self.file).get_thumbnail(options)

class VideoContent(models.Model):
	file = models.FileField(upload_to=UPLOAD_PATH+'video/%Y/%m/%d/', max_length=255)
	image = models.ImageField(upload_to=UPLOAD_PATH+'video/%Y/%m/%d/still_image/', max_length=255, blank=True)
	
	content_field_name = 'video'
	
	class Meta:
		abstract = True

class AudioContent(models.Model):
	file = models.FileField(upload_to=UPLOAD_PATH+'audio/%Y/%m/%d/', max_length=255)
	
	content_field_name = 'audio'
	
	class Meta:
		abstract = True
