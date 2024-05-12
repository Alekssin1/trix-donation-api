from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework import status

class SubscriptionMixin:
    serializer_class = None
    success_message = None
    subscription_field = None

    def create(self, serializer):
        user = self.request.user
        subscription_id = self.request.data.get(self.subscription_field)
        serializer = self.serializer_class(data={'user': user.id, self.subscription_field[:-3]: subscription_id})
        if serializer.is_valid():
            serializer.save()
            return Response({'detail': self.success_message}, status=status.HTTP_201_CREATED)

        print(serializer.errors)
        return Response({'detail': serializer.errors}, status=status.HTTP_401_UNAUTHORIZED)

    def destroy(self, request, *args, **kwargs):
        user = self.request.user
        subscription_id = self.request.data.get(self.subscription_field)

        try:
            subscription = self.queryset.get(user=user, **{self.subscription_field: subscription_id})
            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except self.queryset.model.DoesNotExist:
            return Response({"detail": f"Ви не були підписані на цей {self.subscription_field[:-3]}."}, status=status.HTTP_404_NOT_FOUND)