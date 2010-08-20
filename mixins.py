from django.conf import settings
from django.db import models
from django.template.loader import render_to_string

class FriendlyNamed(models.Model):
    name = models.CharField('Friendly name', max_length=255, help_text='Used in the admin interface only')
    
    class Meta:
        abstract = True
    
    def __unicode__(self):
        return self.name


MAX_CAPTION_LENGTH = 1024

class ImageUseMixIn(models.Model):
    IMAGE_POSITIONS = (
        ('L', 'Left'),
        ('R', 'Right'),
        ('C', 'Centre'),
        )
    EXPAND_OPTIONS = (
        ('100%', '100%'),
        ('75%', '75%'),
        ('50%', '50%'),
        ('33%', '33%'),
        ('25%', '25%'),
    )
    
    caption = models.CharField(max_length=MAX_CAPTION_LENGTH, blank=True)
    link_to_original = models.BooleanField(
        default=False, help_text='Allow users to download original file?')
    link_url = models.CharField(max_length=255, blank=True, help_text='Turns the image into a link to the given URL. Will override "Link to original" if provided')
    position = models.CharField(max_length=1, choices=IMAGE_POSITIONS, blank=True)
    wrappable = models.BooleanField(default=False, blank=True, help_text="Tick to let the following item wrap around the image")
    
    # Move these to the NFSA app or to a different mixin?
    expand = models.CharField(max_length=50, choices=EXPAND_OPTIONS, blank=True, help_text="Expands the image's width relatively to its container")
    width = models.PositiveIntegerField(blank=True, null=True, help_text="Forces the width to a certain value (in pixels)")
    height = models.PositiveIntegerField(blank=True, null=True, help_text="Forces the height to a certain value (in pixels)")
    
    render_template = 'feincmstools/content/imagemixin.html'
    
    class Meta:
        abstract = True
