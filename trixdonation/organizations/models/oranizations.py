import os

from django.db import models
from django.forms import ValidationError
from helper.social_media_validation import is_valid_social_media_url
from django.conf import settings
from money_collections.models.money_collections import MoneyCollection
from django.utils import timezone


class Organization(models.Model):
    organization_id = models.AutoField(primary_key=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, related_name='organizations_creator')
    money_collections = models.ManyToManyField(MoneyCollection, related_name='organizations', blank=True)
    avatar = models.ImageField(upload_to='organizations-avatars', null=True, blank=True)
    name = models.CharField(max_length=100)
    twitter = models.URLField(null=True, blank=True)
    instagram = models.URLField(null=True, blank=True)
    facebook = models.URLField(null=True, blank=True)
    customURL = models.URLField(null=True, blank=True)
    foundation = models.BooleanField(default=False)
    created_at = models.DateField(auto_now_add=True)
    verified = models.BooleanField(default=False)


    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        from helper.image_converter import convert_image_to_webp
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


class OrganizationStaff(models.Model):

    PENDING = 'p'
    APPROVED = 'a'
    DECLINED = 'd'

    STATUS_CHOICES = (
        (PENDING, 'Pending'),
        (APPROVED, 'Approved'),
        (DECLINED, 'Declined'),
    )

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='organization_staff')

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="organization_user")
    
    status = models.CharField(choices=STATUS_CHOICES, default=PENDING, max_length=1)


    def __str__(self):
        return f'{self.organization} - {self.user} - {self.status}'


class OrganizationRequest(models.Model):

    """ all DECLINED requests is removed after 5 days of been in DECLINED status """

    PENDING = 'p'
    APPROVED = 'a'
    DECLINED = 'd'

    STATUS_CHOICES = (
        (PENDING, 'Pending'),
        (APPROVED, 'Approved'),
        (DECLINED, 'Declined'),
    )

    REMOVE_DECLINED_REQUESTS_AFTER_DAYS = 5

    name = models.CharField(max_length=100)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    user_details = models.TextField()
    created_at = models.DateField(auto_now_add=True, null=True, blank=True)

    # Changed only when status is changed
    status_changed_at = models.DateTimeField(null=True, blank=True)
    instagram_url = models.URLField(blank=True, null=True)
    twitter_url = models.URLField(blank=True, null=True)
    facebook_url = models.URLField(blank=True, null=True)
    custom_url = models.URLField(blank=True, null=True)
    image = models.ImageField(upload_to='organization_requests/images/', blank=True, null=True)
    foundation = models.BooleanField(default=False)
    EGRPOU_code = models.CharField(max_length=8, null=True, blank=True)

    status = models.CharField(choices=STATUS_CHOICES, default=PENDING, max_length=1)
    
    def __str__(self):
        return f"Запит {self.user} на створення {'фонду' if self.foundation else 'волонтерської реєстрації'}"

    def save(self, *args, **kwargs): 
        from helper.image_converter import convert_image_to_webp
        
        if self.image:
            self.image= convert_image_to_webp(self.image)
        if self.pk:
            # updated
            old_object = OrganizationRequest.objects.get(pk=self.pk)
            if old_object.status != self.status:
                self.status_changed_at = timezone.now()

                if self.status == self.DECLINED:
                    self.user.declined_request_counter += 1
                    if self.user.declined_request_counter == self.user.MAXIMUM_RECLINED_REQUESTS:
                        self.user.blocked = True
                    
                    self.user.save()

            
        else:
            pass

        return super().save(*args, **kwargs)