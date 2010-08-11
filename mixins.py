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
IMAGE_TEMPLATE = 'feincmstools/content/imagemixin.html'


class ImageUseMixIn(models.Model):
	IMAGE_POSITIONS = (
		('L', 'Left'),
		('R', 'Right'),
		('C', 'Centre'),
		('B', 'Block'),
		('T', 'Thumbnail'),
		)
	
	caption = models.CharField(max_length=MAX_CAPTION_LENGTH, blank=True)
	link_to_original = models.BooleanField(
		default=False, help_text='Allow users to download original file?')
	position = models.CharField(max_length=1, choices=IMAGE_POSITIONS)
	
	class Meta:
		abstract = True

	def render(self, **kwargs):
		""" Called by FeinCMS """
		return render_to_string(IMAGE_TEMPLATE, dict(image=self))
	
	def rendersize(self):
		"""
		Returns a tuple (w, h) to which to resize the image
		"""
		return {
			'L': (212, 10000), #TODO: cheat!!
			'R': (222, 10000),
			'C': (212, 10000),
			'B': (444, 10000),
			'T': (202, 202),
		}[self.position]

	
	def css_classes(self):
		""" Return space-separated list of css classes for this image. """
		css = []
		position = dict(self.IMAGE_POSITIONS).get(self.position, '')
		css.append(position.lower())
		return ' '.join(css)


