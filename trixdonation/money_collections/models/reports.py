from django.db import models
from helper.image_converter import convert_image_to_webp
from money_collections.models.money_collections import MoneyCollection

class ReportImage(models.Model):
    file = models.ImageField(upload_to='reports/images/')

    def save(self, *args, **kwargs):
        if self.file:
            self.file = convert_image_to_webp(self.file)
        super().save(*args, **kwargs)


class ReportVideo(models.Model):
    file = models.FileField(upload_to='reports/videos/')

class Report(models.Model):
    money_collection = models.ForeignKey(MoneyCollection, on_delete=models.CASCADE, related_name='reports')
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(null=True, blank=True)
    images = models.ManyToManyField(ReportImage, related_name='reports', blank=True)
    videos = models.ManyToManyField(ReportVideo, related_name='reports', blank=True)
    
    def __str__(self):
        return f"Звіт за {self.money_collection.goal_title}: {self.name}"