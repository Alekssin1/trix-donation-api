from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import AllowAny

from rest_framework.response import Response
from rest_framework.generics import (
    RetrieveUpdateDestroyAPIView,
    CreateAPIView,
)
from money_collections.models import OtherRequisite, MoneyCollectionRequisites
from money_collections.serializers import OtherRequisiteSerializer
from users.permissions import IsOrganizationStaff

class OtherRequisitesCreateAPIView(CreateAPIView):
    serializer_class = OtherRequisiteSerializer
    permission_classes = [IsOrganizationStaff]
    lookup_url_kwarg = 'money_collection_pk'

    def create(self, request, *args, **kwargs):
        requisites_id = self.kwargs.get('requisites_id')
        # Get the bank name and card number from request data
        name  = request.data.get('name')
        value = request.data.get('value')

        # Create a dictionary with the data to pass to the serializer
        data = {'name': name, 'value': value}
        try:
            requisites = MoneyCollectionRequisites.objects.get(id=requisites_id)
        except MoneyCollectionRequisites.DoesNotExist:
            return Response({'detail': 'Реквізитів з таким id не знайдено'}, status=status.HTTP_404_NOT_FOUND)

        # Create other requisites
        serializer = OtherRequisiteSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        other_requisite = serializer.save() 

        requisites.other_requisites.add(other_requisite)
        

        return Response(serializer.data, status=status.HTTP_201_CREATED)
    

class OtherRequisiteRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    queryset = OtherRequisite.objects.all()
    serializer_class = OtherRequisiteSerializer
    
    
    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        elif self.request.method in ['PUT', 'PATCH', 'DELETE']:
            organization_pk = self.kwargs.get('organization_pk')  
            return [IsOrganizationStaff(organization_pk=organization_pk)] 
        return []
    

    def get_object(self):
        other_requisite_id = self.kwargs.get('pk')
        queryset = OtherRequisite.objects.prefetch_related('money_collection_requisites__money_collection__organizations')
        other_requisite = get_object_or_404(queryset, pk=other_requisite_id)
        self.check_object_permissions(self.request, other_requisite)  
        return other_requisite

    def perform_update(self, serializer):
        serializer.save()

    def perform_destroy(self, instance):
        instance.delete()