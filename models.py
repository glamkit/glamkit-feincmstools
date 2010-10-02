""" IxC extensions to FeinCMS. May perhaps be pushed back to FeinCMS core """
import os

from django.conf import settings
from django.db import models
from django.utils.translation import ugettext as _
from django.template.loader import render_to_string, find_template
from django.template.context import RequestContext, Context
from django.template import TemplateDoesNotExist
from django.utils.importlib import import_module
from django.core.exceptions import ImproperlyConfigured

from easy_thumbnails.files import get_thumbnailer

from base import *
from forms import MarkdownContentAdminForm, TextileContentAdminForm, ImageLumpForm
import settings as feincmstools_settings

__all__ = ['LumpyContent', 'HierarchicalLumpyContent', 'Reusable', 'OneOff', 'TextContent', 'MarkdownTextContent', 'DownloadableContent', 'ImageContent', 'AudioContent', 'VideoContent', 'Lump']

class Reusable(object):
	__metaclass__ = ReusableBase

	class Meta:
		abstract = True

class OneOff(object):
	__metaclass__ = OneOffBase

	class Meta:
		abstract = True

class Lump(models.Model):
	class Meta:
		abstract = True

	init_template = None
	render_template = None

	def render(self, **kwargs):
		assert 'request' in kwargs
		template = getattr(self, 'render_template', getattr(self.get_content(), 'render_template', None) if hasattr(self, 'get_content') else None)
		if not template:
			raise NotImplementedError('No template defined for rendering %s content.' % self.__class__.__name__)
		context = Context({'content': self})
		if 'context' in kwargs:
			context.update(kwargs['context'])
		return render_to_string(template, context, context_instance=RequestContext(kwargs['request']))

	@classmethod
	def _detect_template(cls, name):
		"""
		Look for template in app/model-specific location.

		Return path to template or None if not found.
		Search using app/model names for parent classes to allow inheritance.
		
		"""
		_class = cls
		# traverse parent classes up to (but not including) Lump
		while(Lump not in _class.__bases__):
			# choose the correct path for multiple inheritance
			base = [
				base for base in _class.__bases__ if issubclass(base, Lump)][0]
			# (this will only take the left-most relevant path in any rare
			# cases involving diamond-relationships with Lump)
			path = '%(app_label)s/lump/%(model_name)s/%(name)s' % {
				'app_label': base._meta.app_label,
				'model_name': base._meta.module_name,
				'name': name,
			}
			try:
				find_template(path)
			except TemplateDoesNotExist:
				pass
			else:
				return path
			_class = base
		return None
	
	@classmethod
	def initialize_type(cls, **kwargs):
		""" FeinCMS hook calls this method upon creation of content types. """
		# inject init template (if present) into feincms_item_editor_includes
		# (must be injected into cls.__base__, which should be the actual
		# FeinCMS content type class rather than the registered subclass)
		init_path = cls.init_template or cls._detect_template('init.html')
		if init_path:
			if not hasattr(cls.__base__, 'feincms_item_editor_includes'):
				setattr(cls.__base__, 'feincms_item_editor_includes', {})
			if not hasattr(cls.__base__.feincms_item_editor_includes, 'head'):
				cls.__base__.feincms_item_editor_includes['head'] = []
			cls.__base__.feincms_item_editor_includes['head'].append(init_path)

		if cls.render_template is None:
			cls.render_template = cls._detect_template('render.html')

        
MAX_ALT_TEXT_LENGTH = 1024

UPLOAD_PATH = getattr(settings, 'UPLOAD_PATH', 'uploads/')

class TextContent(Lump):
	content = models.TextField()

	content_field_name = 'text_block'

	class Meta:
		abstract = True
		verbose_name = _("Text Block")

	form = TextileContentAdminForm
	feincms_item_editor_form = TextileContentAdminForm


class MarkdownTextContent(Lump):
	content = models.TextField()

	content_field_name = 'text_block'

	class Meta:
		abstract = True
		verbose_name = _("Text Block")

	form = MarkdownContentAdminForm
	feincms_item_editor_form = MarkdownContentAdminForm


class AbstractFile(Lump):
	title = models.CharField(max_length=255, blank=True, help_text=_('The filename will be used if not given.'))

	with_extension = False

	class Meta:
		abstract = True

	def __unicode__(self):
		return self.get_title()

	def get_title(self):
		if self.title:
			return self.title
		if hasattr(self, 'file'):
			return os.path.split(self.file.name)[1] if self.with_extension else os.path.splitext(self.file.name)[0]
		return None

	def save(self, *args, **kwargs):
		if not self.title:
			self.title = self.get_title()
		return super(AbstractFile, self).save(*args, **kwargs)

class DownloadableContent(AbstractFile):
	file = models.FileField(upload_to=UPLOAD_PATH+'file/%Y/%m/%d/')

	content_field_name = 'file'
	with_extension = True

	class Meta:
		abstract = True
		verbose_name = "Downloadable File"
		verbose_name_plural = "Downloadable Files"


# --- Media models ------------------------------------------------------------

class ImageContent(AbstractFile):
	file = models.ImageField(upload_to=UPLOAD_PATH+'images/%Y/%m/%d/',
							 height_field='file_height', width_field='file_width',
							 max_length=255)
	file_height = models.PositiveIntegerField(editable=False)
	file_width = models.PositiveIntegerField(editable=False)
	alt_text = models.CharField('Alternate text', blank=True,
								max_length=MAX_ALT_TEXT_LENGTH,
								help_text= 'Description of the image content')

	form_base = ImageLumpForm
	content_field_name = 'image'

	class Meta:
		abstract = True

	def get_thumbnail(self, **kwargs):
		options = dict(size=(100, 100), crop=True)
		options.update(kwargs)
		return get_thumbnailer(self.file).get_thumbnail(options)

class VideoContent(AbstractFile):
	file = models.FileField(upload_to=UPLOAD_PATH+'video/%Y/%m/%d/', max_length=255)
	image = models.ImageField(upload_to=UPLOAD_PATH+'video/%Y/%m/%d/still_image/', max_length=255, blank=True)

	content_field_name = 'video'

	class Meta:
		abstract = True

	def width(self):
		return 512

	def height(self):
		return 384

class AudioContent(AbstractFile):
	file = models.FileField(upload_to=UPLOAD_PATH+'audio/%Y/%m/%d/', max_length=255)

	content_field_name = 'audio'

	class Meta:
		abstract = True


class ViewContent(Lump):
    view = models.CharField(max_length=255, blank=False,
                            choices=feincmstools_settings.CONTENT_VIEW_CHOICES)

    class Meta:
        abstract = True

    @staticmethod
    def get_view_from_path(path):
        i = path.rfind('.')
        module, view_name = path[:i], path[i+1:]
        try:
            mod = import_module(module)
        except ImportError, e:
            raise ImproperlyConfigured(
                'Error importing ViewContent module %s: "%s"' %
                (module, e))
        try:
            view = getattr(mod, view_name)
        except AttributeError:
            raise ImproperlyConfigured(
                'Module "%s" does not define a "%s" method' %
                (module, view_name))
        return view

    def render(self, **kwargs):
        try:
            view = self.get_view_from_path(self.view)
        except:
            if settings.DEBUG:
                raise
            return '<p>Content could not be found.</p>'
        try:
            response = view(kwargs.get('request'))
        except:
            if settings.DEBUG:
                raise
            return '<p>Error rendering content.</p>'
        # extract response content if it is a HttpResponse object;
        # otherwise let's hope it is a raw content string...
        content = getattr(response, 'content', response)
        return content
