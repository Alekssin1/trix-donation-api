from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from users.permissions import IsOrganizationStaff
from organizations.models import OrganizationSubscription
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

class OrganizationSubscriptionCreateView(CreateAPIView):
    queryset = OrganizationSubscription.objects.all()
    serializer_class = OrganizationSubscriptionSerializer
    permission_classes = [IsAuthenticated]

    def create(self, serializer):

        user = self.request.user
        organization_id = self.request.data.get('organization_id') 

        serializer = OrganizationSubscriptionSerializer(data={
            'user': user.id, 'organization':organization_id
        })
        if serializer.is_valid():
            serializer.save()
            return Response({'detail':'Підписка на організацію успішно оформлена'}, status=status.HTTP_201_CREATED)
        
    
        print(serializer.errors)

        return Response({'detail':serializer.errors}, status=status.HTTP_401_UNAUTHORIZED)

class OrganizationSubscriptionDeleteView(DestroyAPIView):
    queryset = OrganizationSubscription.objects.all()
    permission_classes = [IsAuthenticated]

    def destroy(self, request, *args, **kwargs):
        user = self.request.user
        organization_id = self.request.data.get('organization_id') 

        try:
            subscription = OrganizationSubscription.objects.get(user=user, organization_id=organization_id)
        except OrganizationSubscription.DoesNotExist:
            return Response({"detail": "Ви не були підписані на цього користувача."}, status=status.HTTP_404_NOT_FOUND)
        
        # Delete the subscription instance
        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    


# class OrganizationSubscriptionCountByOrganization(APIView):
#     def get(self, request, *args, **kwargs):
#         subscription_counts = OrganizationSubscription.objects.values('organization_id').annotate(count=models.Count('id'))
#         return Response(subscription_counts)

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

    def get_queryset(self):
        user = self.request.user
        return Organization.objects.filter(organizationsubscription__user=user)