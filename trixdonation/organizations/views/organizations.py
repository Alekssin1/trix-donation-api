from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.generics import (
    ListAPIView,
    RetrieveUpdateDestroyAPIView,
    RetrieveUpdateAPIView,
    ListCreateAPIView,
    CreateAPIView,
    DestroyAPIView,
    RetrieveAPIView
)
from rest_framework.pagination import PageNumberPagination


from organizations.tasks import send_updated_status_email, send_found_invitation
from users.models import User
from users.permissions import IsStaffUser
from helper.validate_egrpou import validate_egrpou
from organizations.serializers import OrganizationRequestPostSerializer, \
    OrganizationRequestGetSerializer, StaffOrganizationRequestUpdateSerializer, \
    OrganizationSerializer, OrganizationRequestUpdateSerializer,  OrganizationRequestBaseSerializer,\
    OrganizationEditSerializer, OrganizationStaffSerializer
from organizations.models import Organization, OrganizationRequest, OrganizationStaff
from users.services.handle_user import get_user_by_email




class OrganizationRequestPagination(PageNumberPagination):
    page_size = 6
    page_query_param = 'page'
    page_size_query_param = 'page_size'

class OrganizationPagination(PageNumberPagination):
    page_size = 3
    page_query_param = 'page'
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
                valid, detail = validate_egrpou(egrpou_code)
                if not valid:
                    return Response({"detail": detail}, status=status.HTTP_400_BAD_REQUEST)
            if not has_organization:
                OrganizationRequest.objects.create(**validated_data)
                return Response({'detail': f"Ваш запит на реєстрацію {'фонду' if validated_data.get('foundation') else 'волонтерської організації'} додано. Очікуйте розгляду вашої заяви."}, status=status.HTTP_201_CREATED)
            else:
                existing_organization = Organization.objects.filter(created_by=user, foundation=False).first()
                if existing_organization and validated_data.get('foundation'):
                    existing_organization.foundation = True
                    existing_organization.save()
                    return Response({"detail": "Існуюча організація була оновлена, до статусу фонду!"}, status=status.HTTP_200_OK)
                else:
                    return Response({'detail': "У вас вже є волонтерська організація, ви не можете створювати більше однієї організації."}, status=status.HTTP_409_CONFLICT)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


class StaffOrganizationRequestListView(ListAPIView):
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
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return OrganizationRequestBaseSerializer
        elif self.request.method == 'PUT' or self.request.method == 'PATCH':
            return OrganizationRequestUpdateSerializer

    def get_object(self):
        user_pk = self.request.user.pk
        queryset = OrganizationRequest.objects.filter(user=user_pk, status__in=['d', 'p'])
        obj = get_object_or_404(queryset)
        self.check_object_permissions(self.request, obj)
        return obj

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({'detail': "Запит користувача на створення знайдений.", 'data': serializer.data}, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer_context = {'user': request.user}
        serializer = self.get_serializer(instance, data=request.data, partial=partial, context=serializer_context)
        serializer.is_valid(raise_exception=True)
        egrpou_code = serializer.validated_data.get('EGRPOU_code')
        if egrpou_code:
            valid, detail = validate_egrpou(egrpou_code)
            if not valid:
                return Response({"detail": detail}, status=status.HTTP_400_BAD_REQUEST)
        self.perform_update(serializer)

        # Bulk update organization requests
        OrganizationRequest.objects.filter(user=request.user, status="d").update(status="p")

        return Response({'detail': "Ваш запит успішно оновлений."}, status=status.HTTP_200_OK)
    

class StaffOrganizationRequestRetrieveUpdateView(RetrieveUpdateAPIView):
    queryset = OrganizationRequest.objects.all()
    serializer_class = StaffOrganizationRequestUpdateSerializer
    permission_classes = [IsStaffUser]

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        if instance.status == 'a' and serializer.validated_data.get('status') != 'a':
            return Response({'detail': "Ви не можете змінити статус заявки, яка була прийнята раніше."},
                        status=status.HTTP_400_BAD_REQUEST)
        self.perform_update(serializer)
        status_value = serializer.validated_data.get('status')

        # Get user details
        user = instance.user

        # Determine organization type
        organization_type = "фонду" if instance.foundation else "волонтерської організації"

        # Set detail message based on status
        match status_value:
            case "a":
                detail_message = f"Запит на створення організації {organization_type} прийнято."
                # Create organization
                organization_data = {
                    'created_by': user.pk,
                    'avatar': instance.image,
                    'name': instance.name,
                    'twitter': instance.twitter_url,
                    'instagram': instance.instagram_url,
                    'facebook': instance.facebook_url,
                    'customURL': instance.custom_url,
                    'foundation': instance.foundation,
                    'verified': instance.foundation,
                }
                
                organization_serializer = OrganizationSerializer(data=organization_data)
                if organization_serializer.is_valid():
                    organization = organization_serializer.save()

                    OrganizationStaff.objects.create(
                        organization=organization,
                        user=user,
                        status=OrganizationStaff.APPROVED
                    )
                else:
                    return Response(organization_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            case "d":
                detail_message = f"Запит на створення організації {organization_type} відхилено."
                user.declined_request_counter = user.declined_request_counter + 1 if user.declined_request_counter is not None else 1
                if user.declined_request_counter >= user.MAXIMUM_RECLINED_REQUESTS:
                    user.blocked = True
                user.save()
            case _:
                detail_message = f"Статус змінено на {status_value}"


        send_updated_status_email.s(
            user.email,
            user.name,
            user.surname,
            status_value,
            instance.foundation,
            instance.name
        ).apply_async()

        return Response({'detail': detail_message}, status=status.HTTP_200_OK)
    

class OrganizationListView(ListAPIView):
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer
    pagination_class = OrganizationPagination
    permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = Organization.objects.all()
        page = self.request.query_params.get('page')  
        if page is None:
            self.pagination_class = None  
        return queryset
    
class OrganizationEditView(RetrieveUpdateAPIView):
    queryset = Organization.objects.all()
    serializer_class = OrganizationEditSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.queryset.filter(created_by=self.request.user).first()

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance:  # if organization exist, use PUT to update
            return super().update(request, *args, **kwargs)
        else:  # else display response 404
            return Response({'detail': "На жаль у вас немає доступних для редагування Організацій."}, status=status.HTTP_404_NOT_FOUND)
        
        
class ManageOrganizationStaffView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        if not Organization.objects.filter(pk=pk, created_by=request.user).exists():
            return Response({'detail': 'Ви не можете переглядати персонал інших фондів.'}, status=status.HTTP_403_FORBIDDEN)
        
        queryset = OrganizationStaff.objects.filter(organization_id=pk).select_related('user')
        seriaizer = OrganizationStaffSerializer(queryset, many=True)
        return Response(seriaizer.data)

    def post(self, request, pk):
        organization = get_object_or_404(Organization.objects.select_related('created_by'), pk=pk)

        if not organization.foundation:
            return Response({'detail': 'Управління персоналом доступно тільки для фондів.'}, status=status.HTTP_400_BAD_REQUEST)
            
        if not request.user == organization.created_by:
            return Response({'detail': 'Ви не є власником цієї організації.'}, status=status.HTTP_403_FORBIDDEN)
    
        email = request.data.get('email')
        if not email:
            return Response({'detail': 'Будь ласка, надайте електронну пошту користувача.'}, status=status.HTTP_400_BAD_REQUEST)
    
        try:
            user = get_user_by_email(email)
        except:
            return Response({'detail': 'Користувач з цією електронною поштою не знайдений.'}, status=status.HTTP_404_NOT_FOUND)
    
        action = request.data.get('action')
        if action == 'add':
            existing_request = OrganizationStaff.objects.filter(organization=organization, user=user).exists()
            if existing_request:
                return Response({'detail': 'Ви вже запросили цього користувача до себе в команду.'}, status=status.HTTP_400_BAD_REQUEST)
            foundation_owner = OrganizationStaff.objects.filter(organization__foundation=True, organization__created_by=user).exists()
            if foundation_owner:
                return Response({'detail': 'Користувач якого ви намагаєтесь запросити також є власником фонду.'}, status=status.HTTP_400_BAD_REQUEST)

            OrganizationStaff.objects.create(
                organization=organization,
                user=user
            )
            send_found_invitation.s(
                email,
                user.pk,
                organization.name,
                user.name,
                user.surname,
            ).apply_async()
        elif action == 'remove':
            org_with_user_as_creator = Organization.objects.filter(created_by=user).exists()
            if org_with_user_as_creator:
                # Якщо користувач створив якусь організацію, додаємо його в цю організацію як staff зі статусом "a"
                organization = Organization.objects.get(created_by=user)
                OrganizationStaff.objects.create(
                    organization=organization,
                    user=user,
                    status='a'
                )
            # Видаляємо користувача з поточної організації
            OrganizationStaff.objects.filter(
                organization=organization,
                user=user
            ).delete()
        else:
            return Response({'detail': 'Не вказано, що саме ви хочете зробити з користувачем. Вкажіть action = "add" або "remove".'}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = OrganizationSerializer(organization)
        return Response(serializer.data)


class ApproveDeclineOrganizationStaffView(APIView):
    def post(self, request, pk, decision):
        
        try:
            organization_staff = OrganizationStaff.objects.get(pk=pk)

            if decision == "a":
                # Delete the user from the staff of their previous organization
                previous_organization_staff = OrganizationStaff.objects.filter(user=organization_staff.user)
                if previous_organization_staff.exists():
                    previous_organization_staff.delete()

            serializer = OrganizationStaffSerializer(instance=organization_staff, data={'status': decision}, partial=True)
            if serializer.is_valid():
                serializer.save()
                decision_selected = "прийняли" if decision == "a" else 'відхилили'
                return Response({'detail': f'Ви {decision_selected} запрошення.', 'result': serializer.data}, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except OrganizationStaff.DoesNotExist:
            return Response({'detail': 'Персоналу з таким id не існує в організації.'}, status=status.HTTP_400_BAD_REQUEST)
        
class OrganizationRetrieveView(RetrieveAPIView):
    permission_classes = [AllowAny]
    serializer_class = OrganizationSerializer
    queryset = Organization.objects.all()

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)