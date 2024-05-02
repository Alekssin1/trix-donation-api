from django.db import models

class OtherRequisite(models.Model):
    name = models.CharField(max_length=100)
    value = models.CharField(max_length=255)