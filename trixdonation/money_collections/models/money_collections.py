import os
from django.conf import settings
from django.db import models


class MoneyCollection(models.Model):
    goal_title = models.CharField(max_length=255)
    description = models.TextField()
    preview = models.ImageField(upload_to='money_collections/previews', null=True, blank=True)
    active = models.BooleanField(default=True)
    collected_amount_on_jar = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    collected_amount_on_platform = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    collected_amount_from_other_requisites = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    goal_amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"Збір: {self.goal_title}"

    def save(self, *args, **kwargs):
        from helper.image_converter import convert_image_to_webp
        
        if self.preview:
            self.preview = convert_image_to_webp(self.preview)

        super().save(*args, **kwargs)
