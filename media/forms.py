from feincms.admin.item_editor import ItemEditorForm
from django.contrib.admin.widgets import ForeignKeyRawIdWidget
from django import forms
from django.utils.safestring import mark_safe

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


class ReusableImageForm(ItemEditorForm):
    """ For raw-ID widget and image preview. """

    def __init__(self, *args, **kwargs):
        self.base_fields['image'].widget=ForeignKeyRawIdWidget(
            rel=self._meta.model._meta.get_field('image').rel)
        super(ReusableImageForm, self).__init__(*args, **kwargs)
        self.fields.insert(0, 'preview', ImagePreviewField(
                required=False, instance=kwargs.get('instance', None)))

        
class OneOffImageForm(ItemEditorForm):
    """ Add image preview. """
    def __init__(self, *args, **kwargs):
        super(OneOffImageForm, self).__init__(*args, **kwargs)
        self.fields.insert(0, 'preview', ImagePreviewField(
                required=False, instance=kwargs.get('instance', None)))    
