from rest_framework.response import Response
from rest_framework import status
from money_collections.models import MoneyCollection
from rest_framework.generics import (
    ListAPIView,
    RetrieveUpdateDestroyAPIView,
    RetrieveUpdateAPIView,
    ListCreateAPIView,
    CreateAPIView,
    DestroyAPIView,
    RetrieveAPIView
)
from money_collections.models import Report
from money_collections.serializers import ReportSerializer
from users.permissions import IsOrganizationStaff
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny

class ReportPagination(PageNumberPagination):
    page_size = 6
    page_query_param = 'page'
    page_size_query_param = 'page_size'


class ReportListCreateView(ListCreateAPIView):
    queryset = Report.objects.all()
    serializer_class = ReportSerializer
    permission_classes = [IsOrganizationStaff]
    pagination_class = ReportPagination

    def perform_create(self, serializer):
        money_collection_id = self.kwargs.get('money_collection_pk')
        money_collection = MoneyCollection.objects.get(pk=money_collection_id)
        serializer.save(money_collection=money_collection, images=self.request.FILES.getlist('images', []), videos=self.request.FILES.getlist('videos', []))

class ReportRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    queryset = Report.objects.all()
    serializer_class = ReportSerializer
    permission_classes = [IsOrganizationStaff]

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.images.all().delete() 
        instance.videos.all().delete()  
        self.perform_destroy(instance)

        return Response(status=status.HTTP_204_NO_CONTENT)
    

class ReportListView(ListCreateAPIView):
    serializer_class = ReportSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        money_collection_pk = self.kwargs.get('money_collection_pk')
        queryset = Report.objects.filter(money_collection_id=money_collection_pk).prefetch_related('images', 'videos')
        return queryset
    