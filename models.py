""" IxC extensions to FeinCMS. May perhaps be pushed back to FeinCMS core """

from django.db import models

from base import *
from content import *
from mixins import FriendlyNamed, Categorised

# Concrete default models for use when not overriding.

class TextBlock(FriendlyNamed, TextContent):
	pass

class Video(FriendlyNamed, Categorised, VideoContent):
	pass

class Image(FriendlyNamed, Categorised, ImageContent):
	pass

# Other models

class Category(models.Model):
	name = models.CharField(max_length=255)

	class Meta:
		verbose_name_plural = "Categories"
	
	def __unicode__(self):
		return '%s' % self.name