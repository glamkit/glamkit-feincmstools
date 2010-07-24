from django.contrib import admin
from feincmstools.media.models import Image, ImageCategory
from django.template import Template, Context

ADMIN_THUMBNAIL_SIZE = (100, 100)

class ImageAdmin(admin.ModelAdmin):
    list_display = ('name', 'admin_thumbnail',)
    list_filter = ('category',)
    search_fields = ('name', 'category__name',)
    
    def admin_thumbnail(self, image):
        return '<img src="%s" />' % (
            image.get_thumbnail(size=ADMIN_THUMBNAIL_SIZE).url)
    admin_thumbnail.allow_tags = True
    admin_thumbnail.short_description = 'Thumbnail'

admin.site.register(ImageCategory)
admin.site.register(Image, ImageAdmin)
