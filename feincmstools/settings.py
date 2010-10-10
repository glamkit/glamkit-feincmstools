""" Any of the settings below can be easily overridden in the project settings
by simply defining a value with the PREFIX included in its name -- e.g. FEINCMSTOOLS_CONTENT_VIEW_CHOICES = (('My View', 'myapp.views.myview'),). """

from django.conf import settings
import sys

PREFIX = 'FEINCMSTOOLS_'
DEFAULT_SETTINGS = {
    'CONTENT_VIEW_CHOICES': (), # e.g. (('My View', 'myapp.views.myview'),)
    }

def prefixed(string):
    return '%s%s' % (PREFIX, string)

for name, default in DEFAULT_SETTINGS.items():
    setattr(sys.modules[__name__], name,
            getattr(settings, prefixed(name), default))

