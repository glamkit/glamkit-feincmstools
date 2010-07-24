from feincms.admin.item_editor import ItemEditorForm
from django.contrib.admin.widgets import ForeignKeyRawIdWidget
from django import forms

class ReusableImageForm(ItemEditorForm):
    """ Just to get a raw-ID widget for the image field... """
    def __init__(self, *args, **kwargs):
        self.base_fields['image'].widget=ForeignKeyRawIdWidget(
            rel=self._meta.model._meta.get_field('image').rel)
        super(ReusableImageForm, self).__init__(*args, **kwargs)        
