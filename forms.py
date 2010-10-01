from django import forms
from django.utils.translation import ugettext as _
from django.contrib.admin.widgets import ForeignKeyRawIdWidget

from admin_enhancements.image_preview import ImagePreviewInlineForm
from feincms.admin.editor import ItemEditorForm

class TextileContentAdminForm(ItemEditorForm):
	content = forms.CharField(widget=forms.Textarea, required=False,
							  label=_('Textile content'))

	def __init__(self, *args, **kwargs):
		super(TextileContentAdminForm, self).__init__(*args, **kwargs)
		self.fields['content'].widget.attrs.update(
			{'class': 'item-textile-markitup'})

class MarkdownContentAdminForm(ItemEditorForm):
	content = forms.CharField(widget=forms.Textarea, required=False,
							  label=_('Markdown'))

	def __init__(self, *args, **kwargs):
		super(MarkdownContentAdminForm, self).__init__(*args, **kwargs)
		self.fields['content'].widget.attrs.update(
			{'class': 'item-markdown-markitup'})


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


class ImagePreviewLumpForm(ImagePreviewInlineForm, ItemEditorForm):

	def get_image(self, instance):
		return instance.get_content()
