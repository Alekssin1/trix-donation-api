from django.db import models
from money_collections.models.money_collections import MoneyCollection
from money_collections.models.bank_card import BankCard
from money_collections.models.other_requisite import OtherRequisite
from helper.credit_card_validation import luhn_algorithm_validation
from django.forms import ValidationError
import re

class MoneyCollectionRequisites(models.Model):
    money_collection = models.OneToOneField(MoneyCollection, on_delete=models.CASCADE, related_name='requisites')
    monobank_jar_link = models.URLField()
    monobank_jar_number = models.CharField(max_length=16, blank=True)
    paypal_email = models.EmailField(null=True, blank=True)
    bitcoin_wallet_address = models.CharField(max_length=42, null=True, blank=True)
    ethereum_wallet_address = models.CharField(max_length=42, null=True, blank=True)
    usdt_wallet_address = models.CharField(max_length=34, null=True, blank=True)

    bank_cards = models.ManyToManyField(BankCard, related_name='money_collection_requisites', blank=True)
    other_requisites = models.ManyToManyField(OtherRequisite, related_name='money_collection_requisites', blank=True)


    def save(self, *args, **kwargs):
        MONOBANK_JAR_LINK_PATTERN = r'^https://send\.monobank\.ua/jar/[a-zA-Z0-9]{10}(\?fbclid=[a-zA-Z0-9_-]+)?$'
        if not bool(re.match(MONOBANK_JAR_LINK_PATTERN, self.monobank_jar_link)):
            raise ValidationError('Схоже вказане посилання на банку є некоректним. Будь ласка, переконайтесь, що введене посилання правильне.')
        
        if self.monobank_jar_number:
            monobank_jar_number = ''.join(filter(str.isdigit, self.monobank_jar_number))

            if not luhn_algorithm_validation(monobank_jar_number):
                raise ValidationError('Дані карти не пройшли перевірку. Будь ласка переконайтесь, що реквізити вказані правильно.')
            
            if monobank_jar_number[:6] not in ('537541', '444111'):
                raise ValidationError('Номер банки має починатись або на 537541, або на 444111. Будь ласка переконайтесь, що реквізити вказані правильно.')
        
        # if self.bitcoin_wallet_address:
        #     bitcoin_wallet_pattern = r'^bc1q[a-zA-Z0-9]{38}$'
        #     if not re.match(bitcoin_wallet_pattern, self.bitcoin_wallet_address):
        #         raise ValidationError(
        #             f'Номер Bitcoin гаманця введений неправильно. Будь ласка, переконайтесь, що введене посилання правильне і ви не допустили помилок.'
        #         )

        # if self.ethereum_wallet_address:
        #     ethereum_wallet_pattern = r'^0x[a-zA-Z0-9]{40}$'
        #     if not re.match(ethereum_wallet_pattern, self.ethereum_wallet_address):
        #         raise ValidationError(
        #             f'Номер Ethereum гаманця введений неправильно. Будь ласка, переконайтесь, що введене посилання правильне і ви не допустили помилок.'
        #         )

        # if self.usdt_wallet_address:
        #     usdt_wallet_pattern = r'^TX[a-zA-Z0-9]{32}$'
        #     if not re.match(usdt_wallet_pattern, self.usdt_wallet_address):
        #         raise ValidationError(
        #             f'Номер USDT гаманця введений неправильно. Будь ласка, переконайтесь, що введене посилання правильне і ви не допустили помилок.'
        #         )
        
        super().save(*args, **kwargs)