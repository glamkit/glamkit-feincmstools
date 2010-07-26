from django.db import models
from django.conf import settings
from django.template.loader import render_to_string
from easy_thumbnails.files import get_thumbnailer
from feincmstools.media.forms import ReusableImageForm, OneOffImageForm

MAX_CAPTION_LENGTH = 1024
MAX_ALT_TEXT_LENGTH = 1024
IMAGE_TEMPLATE = 'media/image.html'

class ImageCategory(models.Model):
    name = models.CharField(max_length=255)

    class Meta:
        verbose_name_plural = "Image categories"
    
    def __unicode__(self):
        return '%s' % self.name


class ImageBase(models.Model):
    file = models.ImageField(upload_to='uploads/images/%Y/%m/%d/',
                             height_field='height', width_field='width',
                             max_length=255)
    height = models.PositiveIntegerField(editable=False)
    width = models.PositiveIntegerField(editable=False)
    name = models.CharField('Friendly name', max_length=255)
    alt_text = models.CharField('Alternate text', blank=True,
                                max_length=MAX_ALT_TEXT_LENGTH,
                                help_text= 'Description of the image content')
    category = models.ForeignKey(ImageCategory, null=True, blank=True,
                                 related_name=
                                 '%(app_label)s_%(class)s_related')
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
        ('L', 'Left'),
        ('R', 'Right'),
        ('C', 'Centre'),
        ('B', 'Block'),
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
    
    def css_classes(self):
        """ Return space-separated list of css classes for this image. """
        css = []
        position = dict(ImageUseMixIn.IMAGE_POSITIONS).get(self.position, '')
        css.append(position.lower())
        return ' '.join(css)
        

class Image(ImageBase):
    """ Concrete class for storing reusable images. """
    pass


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
