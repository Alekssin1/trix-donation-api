from rest_framework import serializers
from money_collections.models import BankCard
from helper.credit_card_validation import luhn_algorithm_validation

class BankCardSerializer(serializers.ModelSerializer):
    class Meta:
        model = BankCard
        fields = ['id', 'bank_name', 'card_number']

    def validate_card_number(self, value):
        card_number_digits = ''.join(filter(str.isdigit, value))
        if not luhn_algorithm_validation(card_number_digits):
            raise serializers.ValidationError('Дані карти не пройшли перевірку. Будь ласка, переконайтесь, що реквізити вказані правильно.')
        return value

    def create(self, validated_data):
        return BankCard.objects.create(**validated_data)