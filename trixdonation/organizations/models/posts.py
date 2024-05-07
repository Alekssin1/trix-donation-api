import os
from django.conf import settings
from django.db import models
from helper.image_converter import convert_image_to_webp
from organizations.models.oranizations import Organization

class PostImage(models.Model):
    file = models.ImageField(upload_to='posts/images/')

    def save(self, *args, **kwargs):
        old_file_path = ''
        if self.file:
            old_file_path = os.path.join(settings.MEDIA_ROOT, str(self.file))
            self.file = convert_image_to_webp(self.file)
        super().save(*args, **kwargs)
        if old_file_path and not old_file_path.endswith('.webp'):
            try:
                os.remove(old_file_path)
            except FileNotFoundError:
                pass


class PostVideo(models.Model):
    file = models.FileField(upload_to='posts/videos/')

class Post(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='posts')
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    images = models.ManyToManyField(PostImage, related_name='posts', blank=True)
    videos = models.ManyToManyField(PostVideo, related_name='posts', blank=True)
    
    def __str__(self):
        return f"Пост від {self.organization.name}: {self.name}"