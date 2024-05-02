from django.db import models
from users.models import User
from money_collections.models import MoneyCollection

class Subscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    money_collection = models.ForeignKey(MoneyCollection, on_delete=models.CASCADE)
    subscribed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'money_collection')