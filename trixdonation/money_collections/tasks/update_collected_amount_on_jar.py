from celery import shared_task
from django.db.models import F
import requests
from money_collections.models import MoneyCollection, MoneyCollectionRequisites

@shared_task
def update_collected_amount_on_jar():
    # Get all MoneyCollectionRequisites with extJarId
    # requisites_with_ext_jar_id = MoneyCollectionRequisites.objects.exclude(extJarId__isnull=True)
    
    # for requisites in requisites_with_ext_jar_id:
    #     # Make API request to Monobank API
    #     url = f'https://api.monobank.ua/bank/jar/{requisites.extJarId}'
    #     response = requests.get(url)
    #     print(requisites.extJarId)
    #     if response.status_code == 200:
    #         data = response.json()
    #         collected_amount_on_jar = float(data['amount']) / 100.00
    #         if collected_amount_on_jar >= 0.00:
    #             MoneyCollection.objects.filter(requisites=requisites).update(collected_amount_on_jar=collected_amount_on_jar)
    all_requisites = MoneyCollectionRequisites.objects.all()
    
    for requisites in all_requisites:
        if requisites.extJarId:
            # Make API request to Monobank API
            url = f'https://api.monobank.ua/bank/jar/{requisites.extJarId}'
            response = requests.get(url)

            if response.status_code == 200:
                data = response.json()
                collected_amount_on_jar = float(data['amount']) / 100.00
                if collected_amount_on_jar >= 0.00:
                    MoneyCollection.objects.filter(requisites=requisites).update(collected_amount_on_jar=collected_amount_on_jar)
        elif requisites.monobank_jar_link:
            

        # Make API request to Monobank API if extJarId is not available
            url = 'https://send.monobank.ua/api/handler'
            body = {"c": "hello", "clientId": requisites.monobank_jar_link.split('jar/')[-1][:10], "Pc": "random"}
            response = requests.post(url, json=body)
            if response.status_code == 200:
                data = response.json()
                collected_amount_on_jar = float(data.get('jarAmount', 0)) / 100.00
                ext_jar_id = data.get('extJarId')
               

                # Update MoneyCollectionRequisites with collected amount and extJarId
                money_collection = MoneyCollectionRequisites.objects.filter(pk=requisites.pk).update(extJarId=ext_jar_id)
                print(money_collection)
                # Update MoneyCollection with collected amount
                MoneyCollection.objects.filter(pk=requisites.money_collection.pk).update(
                    collected_amount_on_jar=collected_amount_on_jar
                )