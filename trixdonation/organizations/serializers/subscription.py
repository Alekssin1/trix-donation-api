from rest_framework import serializers
from organizations.models import OrganizationSubscription

class OrganizationSubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrganizationSubscription
        fields = '__all__'