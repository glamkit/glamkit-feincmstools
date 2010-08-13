from feincms.admin.item_editor import ItemEditorForm
from django.contrib.admin.widgets import ForeignKeyRawIdWidget
from django import forms
from django.utils.safestring import mark_safe

class FormWithRawIDFields(ItemEditorForm):
	raw_id_fields = []
	
	def __init__(self, *args, **kwargs):
		for field_name in self.raw_id_fields:
			self.base_fields[field_name].widget=ForeignKeyRawIdWidget(
				rel=self._meta.model._meta.get_field(field_name).rel)
		super(FormWithRawIDFields, self).__init__(*args, **kwargs)	


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
					self.instance.get_image().get_thumbnail().url,))
		else:
			return ''


class ImagePreviewField(forms.Field):
	""" Dummy "field" to provide preview thumbnail. """
	def __init__(self, *args, **kwargs):
		self.instance = kwargs.pop('instance', None)
		kwargs['widget'] = ImagePreviewWidget(instance=self.instance)
		super(ImagePreviewField, self).__init__(*args, **kwargs)


class ReusableImageForm(FormWithRawIDFields):
	""" For raw-ID widget and image preview. """

	raw_id_fields = ['image']
	
	def __init__(self, *args, **kwargs):
		super(ReusableImageForm, self).__init__(*args, **kwargs)
		self.fields.insert(0, 'preview', ImagePreviewField(
				required=False, instance=kwargs.get('instance', None)))

		
class OneOffImageForm(ItemEditorForm):
	""" Add image preview. """
	def __init__(self, *args, **kwargs):
		super(OneOffImageForm, self).__init__(*args, **kwargs)
		self.fields.insert(0, 'preview', ImagePreviewField(
				required=False, instance=kwargs.get('instance', None)))	


class ReusableTextForm(FormWithRawIDFields):
	""" For raw-ID widget. """

	#raw_id_fields = ['text_block']
	# remove until there is a need -- will necessitate text preview
	
