import mptt, sys, types

from django.conf import settings
from django.db import models
from django.utils.translation import ugettext as _

from feincms.models import Base, Template
from . import content

__all__ = ['LumpyContent', 'HierarchicalLumpyContent', 'OneOffBase', 'ReusableBase']


# --- Lumpy models ------------------------------------------------------------

class LumpyContentBase(models.base.ModelBase):
	""" Metaclass which simply calls _register() for each new class. """
	def __new__(cls, name, bases, attrs):
		new_class = super(LumpyContentBase, cls).__new__(cls, name, bases, attrs)
		new_class._register()
		return new_class


class LumpyContent(Base):
	""" As opposed to FlatPage content -- can have FeinCMS content regions. """
	
	__metaclass__ = LumpyContentBase
	
	class Meta:
		abstract = True
	
	# auto-registered default FeinCMS regions and content types:
	default_regions = (('main', _('Main')),)
	default_content_types = [getattr(content, contype) for contype in content.__all__]

	# undocumented trick:
	feincms_item_editor_includes = {
		'head': set(['feincmstools/item_editor_head.html' ]),
		}
	
	@classmethod
	def _register(cls):
		if not cls._meta.abstract: # concrete subclasses only
			# auto-register FeinCMS regions
			# cls.register_regions(cls.default_regions)
			# -- produces odd error, do manually:
			cls.template = Template('','',cls.default_regions)
			cls._feincms_all_regions = cls.template.regions
			# auto-register FeinCMS content types:
			for content_type in cls.default_content_types:
				kwargs = {}
				if type(content_type) in (list, tuple):
					content_type, kwargs['regions'] = content_type
				new_content_type = cls.create_content_type(content_type, **kwargs)
				# make it available in the module for convenience
				name = '%s%s' % (cls.__name__, content_type.__name__)
				if hasattr(sys.modules[cls.__module__], name):
					pass # don't overwrite anything though...
				else:
					setattr(sys.modules[cls.__module__], name,
							new_content_type)
						

				
class HierarchicalLumpyContent(LumpyContent):
	""" LumpyContent with hierarchical encoding via MPTT. """
	
	parent = models.ForeignKey('self', verbose_name=_('Parent'), blank=True,
							   null=True, related_name='children')
	parent.parent_filter = True # Custom FeinCMS list_filter
	
	class Meta:
		abstract = True
		ordering = ['tree_id', 'lft'] # required for FeinCMS TreeEditor
	
	@classmethod
	def _register(cls):
		if not cls._meta.abstract: # concrete subclasses only
			# auto-register with mptt
			try:
				mptt.register(cls)
			except mptt.AlreadyRegistered:
				pass
			super(HierarchicalLumpyContent, cls)._register()
	
	def get_path(self):
		""" Returns list of slugs from tree root to self. """
		# TODO: cache in database for efficiency?
		page_list = list(self.get_ancestors()) + [self]
		return '/'.join([page.slug for page in page_list])


# --- Content type models -----------------------------------------------------

class OneOffBase(models.base.ModelBase):
	def __new__(cls, name, bases, attrs):
		attrs['get_media'] = lambda self: self
		attrs.setdefault('Meta', types.ClassType('Meta', (), {})).abstract = True
		klass = super(OneOffBase, cls).__new__(cls, name, bases, attrs)
		return klass

class ReusableBase(models.base.ModelBase):
	def __new__(cls, name, bases, attrs):
		attrs['get_media'] = lambda self: self.media
		concrete_model = attrs.get('concrete_model', Video)
		app_label = '_'.join([pckg for pckg in attrs['__module__'].split('.') if pckg != 'models'])
		attrs['media'] = models.ForeignKey(concrete_model,
										   related_name='%s_%s_related' %
											   (app_label, concrete_model.__name__.lower()))
		attrs.setdefault('Meta', types.ClassType('Meta', (), {})).abstract = True
		klass = super(ReusableBase, cls).__new__(cls, name, bases, attrs)
		return klass

