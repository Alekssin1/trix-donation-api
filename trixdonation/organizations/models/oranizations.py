from django.db import models
from django.forms import ValidationError
from helper.image_converter import convert_image_to_webp
from helper.social_media_validation import is_valid_social_media_url
from django.conf import settings
from money_collections.models.money_collections import MoneyCollection


class Organization(models.Model):
    organization_id = models.AutoField(primary_key=True)
    staff = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='organizations')
    money_collections = models.ManyToManyField(MoneyCollection, related_name='organizations')
    avatar = models.ImageField(upload_to='organizations-avatars', null=True, blank=True)
    name = models.CharField(max_length=100)
    twitter = models.URLField(null=True, blank=True)
    instagram = models.URLField(null=True, blank=True)
    facebook = models.URLField(null=True, blank=True)
    customURL = models.URLField(null=True, blank=True)
    foundation = models.BooleanField(default=False)
    created_at = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if self.avatar:
            self.avatar = convert_image_to_webp(self.avatar)

        self.validate_social_media_urls()

        super().save(*args, **kwargs)


    def validate_social_media_urls(self):
        urls = {
            "twitter": self.twitter,
            "instagram": self.instagram,
            "facebook": self.facebook
        }

        for platform, url in urls.items():
            if url and not is_valid_social_media_url(url, platform):
                raise ValidationError(f"Неправильний {platform.capitalize()} URL")
