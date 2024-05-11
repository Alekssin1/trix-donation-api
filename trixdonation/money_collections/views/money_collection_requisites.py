from rest_framework import status
from rest_framework.generics import CreateAPIView, RetrieveUpdateAPIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from users.permissions import IsOrganizationStaff
from money_collections.models import MoneyCollectionRequisites
from money_collections.serializers import MoneyCollectionRequisitesUpdateSerializer, MoneyCollectionRequisitesCreateSerializer

class MoneyCollectionRequisitesCreateView(CreateAPIView):
    queryset = MoneyCollectionRequisites.objects.all()
    serializer_class = MoneyCollectionRequisitesCreateSerializer
    permission_classes = [IsOrganizationStaff]

class MoneyCollectionRequisitesRetrieveUpdateView(RetrieveUpdateAPIView):
    queryset = MoneyCollectionRequisites.objects.all()
    serializer_class = MoneyCollectionRequisitesUpdateSerializer
    permission_classes = [IsOrganizationStaff]


