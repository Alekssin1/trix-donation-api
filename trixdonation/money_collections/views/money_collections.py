from datetime import datetime, timedelta
from rest_framework import generics, status
from rest_framework.response import Response
from django.db.models import Q
from rest_framework.filters import OrderingFilter, SearchFilter
import requests
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.generics import (
    ListAPIView,
    RetrieveUpdateAPIView,
    CreateAPIView,
)
from rest_framework.views import APIView
from organizations.models import Organization
from money_collections.models import MoneyCollection
from users.permissions import IsOrganizationStaff
from rest_framework.pagination import PageNumberPagination
from money_collections.serializers import MoneyCollectionSerializer, MoneyCollectionRequisitesCreateSerializer, MoneyCollectionPostSerializer,\
    MonoJarSerializer, MoneyCollectionInfoSerializer, MoneyCollectionUpdateSerializer

class MoneyCollectionByOrganization(PageNumberPagination):
    page_size_query_param = 'page_size'
    page_size = 6

class OrganizationsMoneyCollectionListView(ListAPIView):
    serializer_class = MoneyCollectionSerializer
    pagination_class = MoneyCollectionByOrganization
    permission_classes = [AllowAny]

    def get_queryset(self):
        organization_pk = self.kwargs.get('organization_pk') 
        organization = get_object_or_404(Organization, pk=organization_pk)
        queryset = organization.money_collections.all()
        active = self.request.query_params.get('active')
        if active is not None:
            active = True if self.request.query_params.get('active').lower() == 't' else False
            queryset = queryset.filter(active=active)
        return queryset
    
class MoneyCollectionListView(ListAPIView):
    serializer_class = MoneyCollectionSerializer
    pagination_class = MoneyCollectionByOrganization
    permission_classes = [AllowAny]
    filter_backends = [OrderingFilter, SearchFilter]
    ordering_fields = ['goal_amount', 'created_at']
    search_fields = ['goal_title', 'organizations__name']

    def get_queryset(self):
        queryset = MoneyCollection.objects.filter(active=True)
    
        # Фільтр за forgotten_collection
        forgotten_collection_param = self.request.query_params.get('param')
        if forgotten_collection_param == 't':
            # Обчислюємо дату 1 місяця тому
            one_month_ago = datetime.now() - timedelta(days=30)
            # Фільтруємо за 'created_at' більше або рівно одного місяця тому
            queryset = queryset.filter(created_at__lte=one_month_ago)
            queryset = queryset.order_by('created_at')
            return queryset
        
        # Пошук за goal_title та organizations__name
        search_param = self.request.query_params.get('search')
        if search_param:
            queryset = queryset.filter(
                Q(goal_title__icontains=search_param) | Q(organizations__name__icontains=search_param)
            )
    
        # Сортування за goal_amount або created_at
        ordering_param = self.request.query_params.get('ordering')
        if ordering_param:
            if ordering_param == '-goal_amount':
                queryset = queryset.order_by('-goal_amount')
            elif ordering_param == 'goal_amount':
                queryset = queryset.order_by('goal_amount')
            elif ordering_param == '-created_at':
                queryset = queryset.order_by('-created_at')
            elif ordering_param == 'created_at':
                queryset = queryset.order_by('created_at')
    
        return queryset
    


class MoneyCollectionCreateAPIView(CreateAPIView):
    serializer_class = MoneyCollectionPostSerializer
    permission_classes = [IsOrganizationStaff]

    def create(self, request, *args, **kwargs):
        organization_pk = self.kwargs.get('organization_pk')
        organization = Organization.objects.get(pk=organization_pk)

        # Витягуємо всі елементи з префіксом "requisites"
        data = {key : value for key, value in request.data.items() if not key.startswith('requisites.')}
        requisites_data = {key.replace('requisites.', ''): value for key, value in request.data.items() if key.startswith('requisites.')}

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)

        money_collection = serializer.save()

        money_collection_id = money_collection.id
        try:
        # Add the money_collection_id to the request data for MoneyCollectionRequisites
            requisites_data['money_collection'] = money_collection_id

            # Create the MoneyCollectionRequisites object with the updated request data
            requisites_serializer = MoneyCollectionRequisitesCreateSerializer(data=requisites_data)
            requisites_serializer.is_valid(raise_exception=True)
        except Exception as e:
            money_collection.delete()
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        requisites_serializer.money_collection = money_collection
        requisites_serializer.save()

        organization.money_collections.add(money_collection)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
class MonoJarDataView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, *args, **kwargs):
        serializer = MonoJarSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        jar_url = serializer.validated_data['jar_url']
        
        client_id = jar_url.split('jar/')[-1][:10]

        get_extJarId = {
            "c": "hello",
            "clientId": client_id,
            "Pc": "random"
        }
        # Відправте POST-запит на https://send.monobank.ua/api/handler
        response = requests.post("https://send.monobank.ua/api/handler", json=get_extJarId)
        
        if response.status_code == 200:
            money_collection_data = response.json()
            if money_collection_data["errCode"]:
                return Response({'detail': "Посилання на банку вказане неправильно, перевірте будь ласка посилання."}, status=status.HTTP_404_NOT_FOUND)
            # Jar data successfully received
            data = {}
            data["goal_title"] = money_collection_data["name"]
            data["description"] = money_collection_data["description"]
            data["goal_amount"] = float(money_collection_data["jarGoal"]/100)
            data["collected_amount_on_jar"] = float(money_collection_data["jarAmount"]/100)
            data["monobank_jar_link"] = jar_url
            data["preview"] = money_collection_data["avatar"]



            return Response(data, status=status.HTTP_200_OK)
        else:
            # Problem with API request
            return Response("Не вийшло отримати дані з банки.", status=status.HTTP_404_NOT_FOUND)
        
class MoneyCollectionRetrieveUpdateAPIView(RetrieveUpdateAPIView):
    queryset = MoneyCollection.objects.prefetch_related('organizations', 'requisites').all()
    permission_classes = [IsOrganizationStaff] 
    lookup_url_kwarg = 'money_collection_pk'

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        elif self.request.method in ['PUT', 'PATCH']:
            return [IsOrganizationStaff()]
        return super().get_permissions()

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return MoneyCollectionInfoSerializer
        elif self.request.method == 'PUT' or self.request.method == 'PATCH':
            return MoneyCollectionUpdateSerializer
        return MoneyCollectionUpdateSerializer  

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def perform_update(self, serializer):
        serializer.save()