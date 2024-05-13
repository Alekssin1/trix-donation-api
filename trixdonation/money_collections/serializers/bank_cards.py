from rest_framework import serializers
from money_collections.models import BankCard
from helper.credit_card_validation import luhn_algorithm_validation
from datetime import datetime

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
    
class PaymentSerializer(serializers.Serializer):
    card_number = serializers.CharField()
    cvv = serializers.CharField(min_length=3, max_length=4)
    expiration_date = serializers.CharField(min_length=5, max_length=5)
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)

    def validate_card_number(self, value):
        card_number_digits = ''.join(filter(str.isdigit, value))
        if not luhn_algorithm_validation(card_number_digits):
            raise serializers.ValidationError('Дані карти не пройшли перевірку. Будь ласка, переконайтесь, що реквізити вказані правильно.')
        return value

    def validate_cvv(self, value):
        if not value.isdigit() or len(value) != 3 :
            raise serializers.ValidationError('CVV має містити тільки цифри')
        return value

    def validate_expiration_date(self, value):
        try:
            month, year = value.split('/')
            current_month = datetime.now().month
            current_year = datetime.now().year % 100  # Отримати поточний рік у форматі yy
            if not (1 <= int(month) <= 12):
                raise serializers.ValidationError('Неправильно вказаний місяць')
            if len(year) != 2:
                raise serializers.ValidationError('Рік має бути вказаний двома цифрами')
            if int(year) < current_year or (int(year) == current_year and int(month) < current_month):
                raise serializers.ValidationError('Ця карта застаріла')
        except ValueError:
            raise serializers.ValidationError('Неправильний формат дати (MM/YY)')
        return value

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError('Сума має бути більше 0.00')
        return value
