from django import forms
from feincms.admin.editor import ItemEditorForm
from django.utils.translation import ugettext as _

class TextileContentAdminForm(ItemEditorForm):
    content = forms.CharField(widget=forms.Textarea, required=False,
                              label=_('Textile content'))

    def __init__(self, *args, **kwargs):
        super(TextileContentAdminForm, self).__init__(*args, **kwargs)
        self.fields['content'].widget.attrs.update(
            {'class': 'item-textile-markitup'})
