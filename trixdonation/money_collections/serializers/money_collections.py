from rest_framework import serializers
import re
from money_collections.models import MoneyCollection, MoneyCollectionRequisites
from money_collections.serializers import MoneyCollectionRequisitesCreateSerializer, MoneyCollectionRequisitesUpdateSerializer
from organizations.serializers import OrganizationSerializerIds


class MoneyCollectionSerializer(serializers.ModelSerializer):

    class Meta:
        model = MoneyCollection
        fields = "__all__"

class MoneyCollectionInfoSerializer(serializers.ModelSerializer):
    requisites = MoneyCollectionRequisitesCreateSerializer()
    organizations = OrganizationSerializerIds(many=True)

    class Meta:
        model = MoneyCollection
        fields = "__all__"

    def to_representation(self, instance):
        # Optimizing to_representation method to prefetch related data in a single query
        instance = MoneyCollection.objects.select_related('requisites').prefetch_related('organizations').get(pk=instance.pk)
        return super().to_representation(instance)
    

class MoneyCollectionUpdateSerializer(MoneyCollectionInfoSerializer):
    requisites = MoneyCollectionRequisitesUpdateSerializer()

    class Meta:
        model = MoneyCollection
        fields = ['requisites', 'goal_title', 'description', 'preview', 'active', 'collected_amount_from_other_requisites']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Exclude fields from the requisites serializer
        excluded_fields = ['id', 'monobank_jar_link', 'monobank_jar_number', 'bank_cards', 'other_requisites', 'extJarId', 'money_collection']
        for field in excluded_fields:
            self.fields['requisites'].fields.pop(field, None)

    def update(self, instance, validated_data):
        requisites_data = validated_data.pop('requisites', None)
        if requisites_data:
            requisites_serializer = self.fields['requisites']
            requisites_instance = instance.requisites
            requisites_serializer.update(requisites_instance, requisites_data)
        return super().update(instance, validated_data)

        
class MoneyCollectionPostSerializer(serializers.ModelSerializer):

    class Meta:
        model = MoneyCollection
        exclude = ('created_at', 'active')

    def create(self, validated_data):
        
        collection = MoneyCollection.objects.create(**validated_data)
        return collection
    

class MonoJarSerializer(serializers.Serializer):
    MONOBANK_JAR_LINK_PATTERN = r'^https://send\.monobank\.ua/jar/[a-zA-Z0-9]{10}(\?fbclid=[a-zA-Z0-9_-]+)?$'

    jar_url = serializers.URLField()

    def validate_jar_url(self, value):
        """
        Перевіряє, чи відповідає введене посилання на банку патерну MONOBANK_JAR_LINK_PATTERN.
        """
        if not re.match(self.MONOBANK_JAR_LINK_PATTERN, value):
            raise serializers.ValidationError(
                'Схоже вказане посилання на банку є некоректним. Будь ласка, переконайтесь, що введене посилання правильне.'
            )
        return value