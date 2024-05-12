from rest_framework import serializers
from money_collections.models import MoneyCollectionSubscription

class MoneyCollectionSubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = MoneyCollectionSubscription
        fields = '__all__'