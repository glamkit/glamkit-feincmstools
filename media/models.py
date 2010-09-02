from django.db import models
from django.conf import settings
from django.utils.translation import ugettext as _
from django.template.loader import render_to_string
from easy_thumbnails.files import get_thumbnailer
from feincmstools.media.forms import ReusableImageForm, OneOffImageForm, \
    ReusableTextForm
from template_utils.templatetags.generic_markup import apply_markup

#---[ General ]----------------------------------------------------------------

class BaseCategory(models.Model):
    name = models.CharField(max_length=255)

    class Meta:
        abstract = True
        verbose_name_plural = "Categories"
    
    def __unicode__(self):
        return '%s' % self.name

#---[ Images ]-----------------------------------------------------------------

MAX_CAPTION_LENGTH = 1024
MAX_ALT_TEXT_LENGTH = 1024
IMAGE_TEMPLATE = 'media/image.html'

class ImageCategory(BaseCategory):
    class Meta:
        verbose_name_plural = "Image categories"


class ImageBase(models.Model):
    file = models.ImageField(upload_to='uploads/images/%Y/%m/%d/',
                             height_field='height', width_field='width',
                             max_length=255)
    height = models.PositiveIntegerField(editable=False)
    width = models.PositiveIntegerField(editable=False)
    alt_text = models.CharField('Alternate text', blank=True,
                                max_length=MAX_ALT_TEXT_LENGTH,
                                help_text= 'Description of the image content')
    attribution = models.CharField(max_length=255, blank=True)
    
    class Meta:
        abstract = True

    def __unicode__(self):
        return '%s' % self.name

    def get_thumbnail(self, **kwargs):
        options = dict(size=(100, 100), crop=True)
        options.update(kwargs)
        return get_thumbnailer(self.file).get_thumbnail(options)
    

class ImageUseMixIn(models.Model):
    IMAGE_POSITIONS = (
        ('F', 'full-width'),
        ('R', 'float-right'),
        )
    
    caption = models.CharField(max_length=MAX_CAPTION_LENGTH, blank=True)
    link_to_original = models.BooleanField(
        default=False, help_text='Allow users to download original file?')
    position = models.CharField(max_length=1, choices=IMAGE_POSITIONS)
    
    class Meta:
        abstract = True

    def render(self, **kwargs):
        """ Called by FeinCMS """
        return render_to_string(IMAGE_TEMPLATE, dict(imageuse=self))

    def get_image(self):
        """ Should be overridden by subclass -- return the ImageField. """
        if settings.DEBUG:
            raise RuntimeError('ImageUseMixIn.get_image called directly.')
        return None
    
    def rendersize(self):
        """
        Returns a tuple (w, h) to which to resize the image
        """
        return {
            'F': (510, 10000), #TODO: cheat!!
            'R': (250, 10000),                    
        }[self.position]

    
    def css_classes(self):
        """ Return space-separated list of css classes for this image. """
        css = []
        position = dict(ImageUseMixIn.IMAGE_POSITIONS).get(self.position, '')
        css.append(position.lower())
        return ' '.join(css)
        

class Image(ImageBase):
    """ Concrete class for storing reusable images. """
    name = models.CharField('Friendly name', max_length=255)
    category = models.ForeignKey(ImageCategory, null=True, blank=True,
                                 related_name=
                                 '%(app_label)s_%(class)s_related')


class ReusableImage(ImageUseMixIn):
    image = models.ForeignKey(Image, related_name=
                              '%(app_label)s_%(class)s_related')
    
    class Meta:
        abstract = True

    feincms_item_editor_form = ReusableImageForm
        
    def get_image(self):
        return self.image


class OneOffImage(ImageBase, ImageUseMixIn):

    class Meta:
        verbose_name = 'One-off Image'
        abstract = True

    feincms_item_editor_form = OneOffImageForm
        
    def get_image(self):
        return self

#---[ Text ]-------------------------------------------------------------------

class TextBlock(models.Model):
    """ A reusable block of text. """
    name = models.CharField('Friendly name', max_length=255, help_text=
                            'used in admin interface only')
    content = models.TextField()

    def __unicode__(self):
        return u'%s' % self.name


class ReusableTextileContent(models.Model):
    text_block = models.ForeignKey(TextBlock, related_name=
                                 '%(app_label)s_%(class)s_related')
    
    class Meta:
        abstract = True
        verbose_name = _("Reusable Text Block")

    feincms_item_editor_form = ReusableTextForm
        
    def render(self, **kwargs):
        # this should possibly be done via a call to smartembed/textile
        # methods directly; just directly replacing the templatetag for now
        return apply_markup(self.text_block.content)
