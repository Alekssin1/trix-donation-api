from django.db import models
from django.forms import ValidationError
from helper.credit_card_validation import luhn_algorithm_validation

class BankCard(models.Model):
    bank_name = models.CharField(max_length=100)
    card_number = models.CharField(max_length=16)

    def save(self, *args, **kwargs):
        card_number_digits = ''.join(filter(str.isdigit, self.card_number))
        # if not luhn_algorithm_validation(card_number_digits):
        #     raise ValidationError('Дані карти не пройшли перевірку. Будь ласка переконайтесь, що реквізити вказані правильно.')
        super().save(*args, **kwargs)

    