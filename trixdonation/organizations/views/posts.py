from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import (
    ListAPIView,
    RetrieveUpdateDestroyAPIView,
    RetrieveUpdateAPIView,
    ListCreateAPIView,
    CreateAPIView,
    DestroyAPIView,
    RetrieveAPIView
)
from organizations.models import Post
from organizations.serializers import PostSerializer
from users.permissions import IsOrganizationStaff
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny

class PostPagination(PageNumberPagination):
    page_size = 6
    page_query_param = 'page'
    page_size_query_param = 'page_size'


class PostListCreateView(ListCreateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsOrganizationStaff]
    pagination_class = PostPagination

    def perform_create(self, serializer):
        # Set the organization based on the URL parameter
        serializer.save(organization_id=self.kwargs.get('organization_pk'))

class PostRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsOrganizationStaff]

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.images.all().delete() 
        instance.videos.all().delete()  
        self.perform_destroy(instance)

        return Response(status=status.HTTP_204_NO_CONTENT)
    

class PostListView(ListCreateAPIView):
    serializer_class = PostSerializer
    permission_classes = [AllowAny]
    pagination_class = PostPagination

    def get_queryset(self):
        print(self.kwargs.get('organization_pk'))
        organization_pk = self.kwargs.get('organization_pk')
        return Post.objects.filter(organization_id=organization_pk)
    