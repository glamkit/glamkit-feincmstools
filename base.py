import mptt, sys, types

from django.conf import settings
from django.db import models
from django.core.exceptions import ImproperlyConfigured
from django.utils.importlib import import_module
from django.utils.translation import ugettext as _

from feincms.models import Base, Template

from forms import FormWithRawIDFields
import settings as feincmstools_settings

__all__ = ['LumpyContent', 'LumpyContentBase', 'HierarchicalLumpyContent', 'OneOffBase', 'ReusableBase']

class ViewContent(models.Model):
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
	
	# Auto-register default regions and all available feincmstools content types
	default_regions = (('main', _('Main')),)
	default_content_types = ()
	
	if feincmstools_settings.CONTENT_VIEW_CHOICES:
		default_content_types += (ViewContent,)
		# (only add if views registered)
		# Warning: this means syncdb won't add new tables until
		# a view is registered in settings
	
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

# Helper function to check all base class for an attribute
def get_base_attribute(bases, value, default=None):
	for base in bases:
		if hasattr(base, value):
			return getattr(base, value)
	return default

class OneOffBase(models.base.ModelBase):
	def __new__(cls, name, bases, attrs):
		# Since FeinCMS does a manual call to the content type metaclass after
		# altering the Meta and attributes, we don't need to reinitialise the
		# attributes if one of the bases is already OneOffBase metaclassed,
		# unless that base is one of the inheritable convenience classes.
		if not [base for base in bases
				if getattr(base, '__metaclass__', None) == cls
				and getattr(base, '__module__', None) != 'feincmstools.models']:
			# Add a get_content() method that returns the parent class instance
			attrs['get_content'] = lambda self: self
			# Generate an editor form based on the provided form_base
			form_base = attrs.get('form_base', get_base_attribute(bases, 'form_base'))
			# For one-off, we simply use an instance of the form_base
			if form_base and 'feincms_item_editor_form' not in attrs:
				attrs['feincms_item_editor_form'] = form_base
			# Make the content type abstract
			attrs.setdefault('Meta', types.ClassType('Meta', (), {})).abstract = True
		klass = super(OneOffBase, cls).__new__(cls, name, bases, attrs)
		return klass

class ReusableBase(models.base.ModelBase):
	def __new__(cls, name, bases, attrs):
		# If we're initialising the "Reusable" and "OneOff" classes that will be
		# inherited from, do nothing.
		if attrs['__module__'] == 'feincmstools.models':
			return super(ReusableBase, cls).__new__(cls, name, bases, attrs)
		# Since FeinCMS does a manual call to the content type metaclass after
		# altering the Meta and attributes, we don't need to reinitialise the
		# attributes if one of the bases is already ReusableBase metaclassed,
		# unless that base is one of the inheritable convenience classes.
		if not [base for base in bases
				if getattr(base, '__metaclass__', None) == cls
				and getattr(base, '__module__', None) != 'feincmstools.models']:
			# A concrete model is required to have a foreign key relationship to
			concrete_model = attrs.get('concrete_model', get_base_attribute(bases, 'concrete_model'))
			if not concrete_model:
				raise ImproperlyConfigured('No concrete model defined for %s.' % name)
			# Determine the name to be used for the field that refers to the
			# concrete model, defined by the content_field_name attribute
			content_field_name = attrs.get('content_field_name',
										   getattr(concrete_model, 'content_field_name',
										   get_base_attribute(bases, 'content_field_name', '_content')))
			# Create a get_content() method that returns the conrete model
			attrs['get_content'] = lambda self: getattr(self, content_field_name)
			# If a render() method is not being inherited, add one that calls
			# the concrete model's render()
			if not attrs.get('render', get_base_attribute(bases, 'render', None)) and getattr(concrete_model, 'render', None):
				attrs['render'] = lambda self, *args, **kwargs: self.get_content().render(*args, **kwargs)
			# Generate an editor form based on the provided form_base, looking
			# for it in the concrete model as well
			form_base = getattr(concrete_model, 'form_base', get_base_attribute(bases, 'form_base'))
			# Use an instance of the form_base initialised with FormWithRawIDFields
			# added to its superclasses, and content_field_name added to its
			# raw ID fields
			if 'feincms_item_editor_form' not in attrs:
				if form_base:
					reusable_form_base = type('Reusable%s' % form_base.__name__,
											  (FormWithRawIDFields, form_base,),
											  {'__module__': form_base.__module__, 
											   'raw_id_fields': getattr(form_base, 'raw_id_fields', []) + [content_field_name,],
											   'content_field_name': content_field_name})
				# If no form_base was specified, create a new class subclassing
				# FormWithRawIDFields
				else:
					reusable_form_base = type('Reusable%sForm' % concrete_model.__name__,
											  (FormWithRawIDFields,),
											  {'__module__': 'feincmstools.forms', 
											   'raw_id_fields': [content_field_name,],
											   'content_field_name': content_field_name})
				attrs['feincms_item_editor_form'] = reusable_form_base
			# Add a foreign key to the concrete model
			attrs[content_field_name] = models.ForeignKey(concrete_model, related_name='%(app_label)s_%(class)s_related')
			# Make the content type abstract
			attrs.setdefault('Meta', types.ClassType('Meta', (), {})).abstract = True
		# Create and return the class
		klass = super(ReusableBase, cls).__new__(cls, name, bases, attrs)
		return klass
		
			
