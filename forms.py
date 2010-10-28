from django import forms
from django.contrib.admin.widgets import ForeignKeyRawIdWidget
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _

from feincms.admin.editor import ItemEditorForm

class TextileContentAdminForm(ItemEditorForm):
	content = forms.CharField(widget=forms.Textarea, required=False,
							  label=_('Textile content'))

	def __init__(self, *args, **kwargs):
		super(TextileContentAdminForm, self).__init__(*args, **kwargs)
		self.fields['content'].widget.attrs.update(
			{'class': 'item-textile-markitup'})


# Image preview

class ImagePreviewWidget(forms.HiddenInput):
	def __init__(self, *args, **kwargs):
		self.instance = kwargs.pop('instance', None)
		super(ImagePreviewWidget, self).__init__(*args, **kwargs)
		
	def render(self, name, data, attrs={}):
		if self.instance:
			# TODO: remove inline styling
			return mark_safe('<img src="%s" class="feincmstools-thumbnail" '
							 'style="position: absolute; margin: 10px; '
							 'right: 0px; "/>' % (
					self.instance.get_content().get_thumbnail().url,))
		else:
			return ''

class ImagePreviewField(forms.Field):
	""" Dummy "field" to provide preview thumbnail. """
	def __init__(self, *args, **kwargs):
		self.instance = kwargs.pop('instance', None)
		kwargs['widget'] = ImagePreviewWidget(instance=self.instance)
		super(ImagePreviewField, self).__init__(*args, **kwargs)

# Forms

class FormWithRawIDFields(ItemEditorForm):
	raw_id_fields = []
	
	def __init__(self, *args, **kwargs):
		if self.raw_id_fields:
			for field_name in self.raw_id_fields:
				self.base_fields[field_name].widget=ForeignKeyRawIdWidget(
					rel=self._meta.model._meta.get_field(field_name).rel)
		super(FormWithRawIDFields, self).__init__(*args, **kwargs)	
		if hasattr(self, 'content_field_name') and self.content_field_name in self.fields:
			self.fields.insert(1, self.content_field_name, self.fields.pop(self.content_field_name))

class ImageForm(ItemEditorForm):
	""" Add image preview. """
	def __init__(self, *args, **kwargs):
		super(ImageForm, self).__init__(*args, **kwargs)
		self.fields.insert(0, 'preview', ImagePreviewField(
				required=False, instance=kwargs.get('instance', None)))

