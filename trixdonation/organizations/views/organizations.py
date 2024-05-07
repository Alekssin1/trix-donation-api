from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from organizations.serializers import OrganizationRequestPostSerializer, OrganizationRequestGetSerializer, StaffOrganizationRequestUpdateSerializer
from organizations.models import Organization, OrganizationRequest
from rest_framework.permissions import IsAuthenticated
import requests
from rest_framework.generics import (
    ListAPIView,
    RetrieveUpdateDestroyAPIView,
    RetrieveUpdateAPIView,
    ListCreateAPIView,
    CreateAPIView,
    DestroyAPIView,
    RetrieveAPIView
)
from xml.etree import ElementTree as ET
from rest_framework.pagination import PageNumberPagination
from users.permissions import IsStaffUser




class OrganizationRequestPagination(PageNumberPagination):
    page_size = 6
    page_size_query_param = 'page_size'

class OrganizationRequestCreateView(APIView):
    permission_classes = [IsAuthenticated]


    def post(self, request, *args, **kwargs):
        user = request.user
        serializer = OrganizationRequestPostSerializer(data=request.data, context={'user': user})
        has_organization = Organization.objects.filter(created_by=user).exists()
        if serializer.is_valid():
            validated_data = serializer.validated_data
            validated_data['user'] = user
            if validated_data.get('foundation'):
                egrpou_code = validated_data.get('EGRPOU_code')
                response = requests.get(f"https://adm.tools/action/gov/api/?egrpou={egrpou_code}")
                root = ET.fromstring(response.content)
                if root:
                    ET.dump(root)
                    name_short = root.find(".//company").get("name_short")
                    print(name_short)
                    if not name_short.startswith("БО"):
                        print(name_short)
                        return Response({"detail": "Заданий ЄДРПОУ не відповідає ЄДРПОУ благодійної організації."}, status=status.HTTP_400_BAD_REQUEST)
                    if OrganizationRequest.objects.filter(EGRPOU_code=egrpou_code, status='a').exists():
                        return Response({"detail": "Фонд з таким ЄДРПОУ вже зареєстрований. Якщо ви вважаєте, що це зловмисник, будь ласка зверніться до служби підтримки за адресою gamesdistributoragency@gmail.com."}, status=status.HTTP_400_BAD_REQUEST)
                    
                else:
                    return Response({'detail': "Заданий ЄДРПОУ не існує, якщо ви вважаєте, що сталася помилка, будь ласка зверніться до служби підтримки за адресою gamesdistributoragency@gmail.com."})
            if not has_organization:
                OrganizationRequest.objects.create(**validated_data)
                return Response({'detail': f"Ваш запит на реєстрацію {'фонду' if validated_data.get('foundation') else 'волонтерської організації'} додано. Очікуйте розгляду вашої заяви."}, status=status.HTTP_201_CREATED)
            else:
                existing_organization = Organization.objects.filter(created_by=user, foundation=False).first()
                if existing_organization and validated_data.get('foundation'):
                    existing_organization.foundation = True
                    existing_organization.save()
                    return Response({"detail": "Існуюча організація була оновлена, до статусу фонду!"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


class OrganizationRequestListView(ListAPIView):
    queryset = OrganizationRequest.objects.all()
    serializer_class = OrganizationRequestGetSerializer
    pagination_class = OrganizationRequestPagination
    permission_classes = [IsStaffUser] 

    def get_queryset(self):
        queryset = super().get_queryset()
        status = self.request.query_params.get('status')
        if status in ['a', 'p', 'd']:
            queryset = queryset.filter(status=status)
        return queryset
    

class OrganizationRequestRetrieveUpdateView(RetrieveUpdateAPIView):
    queryset = OrganizationRequest.objects.all()
    serializer_class = StaffOrganizationRequestUpdateSerializer
    permission_classes = [IsStaffUser]