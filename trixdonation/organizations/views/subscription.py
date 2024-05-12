from rest_framework import status
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated, AllowAny
from users.permissions import IsOrganizationStaff
from organizations.models import OrganizationSubscription
from helper.subsription_mixin import SubscriptionMixin
from organizations.serializers import OrganizationSubscriptionSerializer
from organizations.serializers import OrganizationSerializer
from organizations.models import Organization
from rest_framework.views import APIView
from rest_framework.generics import (
    ListAPIView,
    RetrieveUpdateDestroyAPIView,
    RetrieveUpdateAPIView,
    ListCreateAPIView,
    CreateAPIView,
    DestroyAPIView,
    RetrieveAPIView
)

class SubscribedOrganizationPagination(PageNumberPagination):
    page_size = 6
    page_size_query_param = 'page_size'

class OrganizationSubscriptionCreateView(SubscriptionMixin, CreateAPIView):
    queryset = OrganizationSubscription.objects.all()
    serializer_class = OrganizationSubscriptionSerializer
    permission_classes = [IsAuthenticated]
    subscription_field = 'organization_id'
    success_message = 'Підписка на організацію успішно оформлена'


class OrganizationSubscriptionDeleteView(SubscriptionMixin, DestroyAPIView):
    queryset = OrganizationSubscription.objects.all()
    permission_classes = [IsAuthenticated]
    subscription_field = 'organization_id'


class OrganizationSubscriptionStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, organization_pk):
        # Retrieve the subscription for the authenticated user and the organization
        try:
            OrganizationSubscription.objects.get(user=request.user, organization_id=organization_pk)
            return Response({"is_subscribed": True}, status=status.HTTP_200_OK)
        except OrganizationSubscription.DoesNotExist:
            return Response({"is_subscribed": False}, status=status.HTTP_200_OK)


class UserSubscribedOrganizationsList(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = OrganizationSerializer
    pagination_class = SubscribedOrganizationPagination

    def get_queryset(self):
        user = self.request.user
        return Organization.objects.filter(organizationsubscription__user=user)