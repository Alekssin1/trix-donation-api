from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from helper.subsription_mixin import SubscriptionMixin
from rest_framework.permissions import IsAuthenticated, AllowAny
from users.permissions import IsOrganizationStaff
from money_collections.models import MoneyCollectionSubscription
from money_collections.serializers import MoneyCollectionSubscriptionSerializer
from money_collections.serializers import MoneyCollectionSerializer
from money_collections.models import MoneyCollection
from rest_framework.views import APIView
from rest_framework.generics import (
    ListAPIView,
    CreateAPIView,
    DestroyAPIView,
)

class MoneyCollectionOrganizationsListPagination(PageNumberPagination):
    page_size = 6
    page_size_query_param = 'page_size'

class MoneyCollectionSubscriptionCreateView(SubscriptionMixin, CreateAPIView):
    queryset = MoneyCollectionSubscription.objects.all()
    serializer_class = MoneyCollectionSubscriptionSerializer
    permission_classes = [IsAuthenticated]
    subscription_field = 'money_collection_id'
    success_message = 'Підписка на збір успішно оформлена'


class MoneyCollectionSubscriptionDeleteView(SubscriptionMixin, DestroyAPIView):
    queryset = MoneyCollectionSubscription.objects.all()
    permission_classes = [IsAuthenticated]
    subscription_field = 'money_collection_id'


class MoneyCollectionSubscriptionStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, money_collection_pk):
        # Retrieve the subscription for the authenticated user and the organization
        try:
            MoneyCollectionSubscription.objects.get(user=request.user, money_collection_id=money_collection_pk)
            return Response({"is_subscribed": True}, status=status.HTTP_200_OK)
        except MoneyCollectionSubscription.DoesNotExist:
            return Response({"is_subscribed": False}, status=status.HTTP_200_OK)


class MoneyCollectionOrganizationsList(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = MoneyCollectionSerializer
    pagination_class = MoneyCollectionOrganizationsListPagination

    def get_queryset(self):
        user = self.request.user
        return MoneyCollection.objects.filter(moneycollectionsubscription__user=user)
    
    