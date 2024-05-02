from django.contrib import admin

from .models import Post, PostImage, PostVideo, Organization


admin.site.register(Organization)
admin.site.register(Post)
admin.site.register(PostImage)
admin.site.register(PostVideo)