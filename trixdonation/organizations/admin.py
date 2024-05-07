from django.contrib import admin

from .models import Post, PostImage, PostVideo, Organization, OrganizationRequest, OrganizationSubscription


admin.site.register(Organization)
admin.site.register(Post)
admin.site.register(PostImage)
admin.site.register(PostVideo)
admin.site.register(OrganizationRequest)
admin.site.register(OrganizationSubscription)