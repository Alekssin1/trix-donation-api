from rest_framework import serializers
from money_collections.models import MoneyCollectionRequisites, BankCard, OtherRequisite
from django.core.exceptions import ValidationError
import re
from helper.credit_card_validation import luhn_algorithm_validation
import requests

class MoneyCollectionRequisitesBaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = MoneyCollectionRequisites
        fields = "__all__"

    def validate(self, data):
        errors = []

        # Bitcoin wallet address validation
        bitcoin_wallet_address = data.get('bitcoin_wallet_address')
        bitcoin_wallet_pattern = r'^bc1q[a-zA-Z0-9]{38}$'
        if bitcoin_wallet_address and not re.match(bitcoin_wallet_pattern, bitcoin_wallet_address):
            errors.append('Номер Bitcoin гаманця введений неправильно. Будь ласка, переконайтесь, що введене посилання правильне і ви не допустили помилок.')

        # Ethereum wallet address validation
        ethereum_wallet_address = data.get('ethereum_wallet_address')
        ethereum_wallet_pattern = r'^0x[a-zA-Z0-9]{40}$'
        if ethereum_wallet_address and not re.match(ethereum_wallet_pattern, ethereum_wallet_address):
            errors.append('Номер Ethereum гаманця введений неправильно. Будь ласка, переконайтесь, що введене посилання правильне і ви не допустили помилок.')

        # USDT wallet address validation
        usdt_wallet_address = data.get('usdt_wallet_address')
        usdt_wallet_pattern = r'^TX[a-zA-Z0-9]{32}$'
        if usdt_wallet_address and not re.match(usdt_wallet_pattern, usdt_wallet_address):
            errors.append('Номер USDT гаманця введений неправильно. Будь ласка, переконайтесь, що введене посилання правильне і ви не допустили помилок.')

        if errors:
            raise serializers.ValidationError(errors)

        return data
    

class MoneyCollectionRequisitesCreateSerializer(MoneyCollectionRequisitesBaseSerializer):
    class Meta(MoneyCollectionRequisitesBaseSerializer.Meta):
        pass

    def validate(self, data):
        errors = []

        # Monobank jar link validation
        monobank_jar_link = data.get('monobank_jar_link')
        MONOBANK_JAR_LINK_PATTERN = r'^https://send\.monobank\.ua/jar/[a-zA-Z0-9]{10}(\?fbclid=[a-zA-Z0-9_-]+)?$'
        if monobank_jar_link and not re.match(MONOBANK_JAR_LINK_PATTERN, monobank_jar_link):
            errors.append('Схоже вказане посилання на банку є некоректним. Будь ласка, переконайтесь, що введене посилання правильне.')
        

        client_id = monobank_jar_link.split('jar/')[-1][:10]

        get_extJarId = {
            "c": "hello",
            "clientId": client_id,
            "Pc": "random"
        }
        # Відправте POST-запит на https://send.monobank.ua/api/handler
        response = requests.post("https://send.monobank.ua/api/handler", json=get_extJarId)
        # Перевірте статус відповіді
        if response.status_code == 200:
            json_data = response.json()
            # Receive extJarId from resposne
            ext_jar_id = json_data.get("extJarId")
            data["extJarId"] = ext_jar_id


        # Monobank jar number validation
        monobank_jar_number = data.get('monobank_jar_number')
        if monobank_jar_number:
            monobank_jar_number = ''.join(filter(str.isdigit, monobank_jar_number))
            if not luhn_algorithm_validation(monobank_jar_number):
                errors.append('Дані карти не пройшли перевірку. Будь ласка переконайтесь, що реквізити вказані правильно.')
            if monobank_jar_number[:6] not in ('537541', '444111'):
                errors.append('Номер банки має починатись або на 537541, або на 444111. Будь ласка переконайтесь, що реквізити вказані правильно.')

        if errors:
            raise serializers.ValidationError(errors)

        return data

    def to_representation(self, instance):
        from money_collections.serializers import BankCardSerializer, OtherRequisiteSerializer
        # Get the serialized representation of the requisites
        repr_data = super().to_representation(instance)
        # Get the bank cards associated with the requisites
        bank_cards_ids = repr_data.get('bank_cards')
        other_requisites_ids = repr_data.get('other_requisites')
        if bank_cards_ids:
            bank_cards = BankCard.objects.filter(id__in=bank_cards_ids)
            bank_cards_serializer = BankCardSerializer(bank_cards, many=True)
            repr_data['bank_cards'] = bank_cards_serializer.data
        if other_requisites_ids:
            other_requisites = OtherRequisite.objects.filter(id__in=other_requisites_ids)
            other_requisites_serializer = OtherRequisiteSerializer(other_requisites, many=True)
            repr_data['other_requisites'] = other_requisites_serializer.data
        return repr_data

class MoneyCollectionRequisitesUpdateSerializer(MoneyCollectionRequisitesBaseSerializer):
    class Meta(MoneyCollectionRequisitesBaseSerializer.Meta):
        fields = ['paypal_email', 'bitcoin_wallet_address', 'ethereum_wallet_address', 'usdt_wallet_address']

    def update(self, instance, validated_data):
        instance = super().update(instance, validated_data)
        return instance