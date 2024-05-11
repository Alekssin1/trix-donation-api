from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import AllowAny

from rest_framework.response import Response
from rest_framework.generics import (
    RetrieveUpdateDestroyAPIView,
    CreateAPIView,
)
from money_collections.models import BankCard, MoneyCollectionRequisites
from money_collections.serializers import BankCardSerializer
from users.permissions import IsOrganizationStaff

class BankCardCreateAPIView(CreateAPIView):
    serializer_class = BankCardSerializer
    permission_classes = [IsOrganizationStaff]
    lookup_url_kwarg = 'money_collection_pk'

    def create(self, request, *args, **kwargs):
        requisites_id = self.kwargs.get('requisites_id')
        # Get the bank name and card number from request data
        bank_name = request.data.get('bank_name')
        card_number = request.data.get('card_number')

        # Create a dictionary with the data to pass to the serializer
        data = {'bank_name': bank_name, 'card_number': card_number}
        try:
            requisites = MoneyCollectionRequisites.objects.get(id=requisites_id)
        except MoneyCollectionRequisites.DoesNotExist:
            return Response({'detail': 'Реквізитів з таким id не знайдено'}, status=status.HTTP_404_NOT_FOUND)

        # Create the bank card object
        serializer = BankCardSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        bank_card = serializer.save() 

        requisites.bank_cards.add(bank_card)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

class BankCardRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    queryset = BankCard.objects.all()
    serializer_class = BankCardSerializer
    
    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        elif self.request.method in ['PUT', 'PATCH', 'DELETE']:
            organization_pk = self.kwargs.get('organization_pk')  
            return [IsOrganizationStaff(organization_pk=organization_pk)] 
        return []

    def get_object(self):
        bank_card_id = self.kwargs.get('pk')
        queryset = BankCard.objects.prefetch_related('money_collection_requisites__money_collection__organizations')
        bank_card = get_object_or_404(queryset, pk=bank_card_id)
        self.check_object_permissions(self.request, bank_card)  
        return bank_card

    def perform_update(self, serializer):
        serializer.save()

    def perform_destroy(self, instance):
        instance.delete()