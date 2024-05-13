from rest_framework import status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from money_collections.models import MoneyCollection
from money_collections.serializers import PaymentSerializer

class PaymentView(APIView):
    def post(self, request, *args, **kwargs):
        money_collection_id = kwargs.get('money_collection_id')
        money_collection = MoneyCollection.objects.get(pk=money_collection_id)

        serializer = PaymentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        amount = serializer.validated_data['amount']
        money_collection.collected_amount_on_platform += amount
        money_collection.save()

        return Response({'message': f'Ви успішно задонатили {amount} грн на збір {money_collection.goal_title}'}, status=status.HTTP_200_OK)
