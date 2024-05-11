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
    extJarId = models.CharField(max_length=32, null=True, blank=True)
    bank_cards = models.ManyToManyField(BankCard, related_name='money_collection_requisites', blank=True)
    other_requisites = models.ManyToManyField(OtherRequisite, related_name='money_collection_requisites', blank=True)

    def __str__(self):
        return f"Реквізити збору({self.pk}): {self.money_collection}"
    

    def save(self, *args, **kwargs):
        MONOBANK_JAR_LINK_PATTERN = r'^https://send\.monobank\.ua/jar/[a-zA-Z0-9]{10}(\?fbclid=[a-zA-Z0-9_-]+)?$'
        if not re.match(MONOBANK_JAR_LINK_PATTERN, self.monobank_jar_link):
            raise ValidationError('Схоже вказане посилання на банку є некоректним. Будь ласка, переконайтесь, що введене посилання правильне.')
        
        if self.monobank_jar_number:
            monobank_jar_number = ''.join(filter(str.isdigit, self.monobank_jar_number))

            if not luhn_algorithm_validation(monobank_jar_number):
                raise ValidationError('Дані карти не пройшли перевірку. Будь ласка переконайтесь, що реквізити вказані правильно.')
            
            if monobank_jar_number[:6] not in ('537541', '444111'):
                raise ValidationError('Номер банки має починатись або на 537541, або на 444111. Будь ласка переконайтесь, що реквізити вказані правильно.')
        
        super().save(*args, **kwargs)