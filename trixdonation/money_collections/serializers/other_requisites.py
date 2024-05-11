from rest_framework import serializers
from money_collections.models import OtherRequisite

class OtherRequisiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = OtherRequisite
        fields = ['id', 'name', 'value']