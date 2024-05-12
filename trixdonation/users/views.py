from random import randint
import redis
from rest_framework import status
from rest_framework.generics import (
    CreateAPIView,
    RetrieveUpdateAPIView,
    RetrieveAPIView
)
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken

from organizations.models.oranizations import Organization
from users.permissions import IsOrganizationStaff, IsStaffUser
from organizations.serializers import OrganizationSerializer

from .models import User
from organizations.models import OrganizationStaff
from .serializers import UserCreateSerializer, EmailSerializer, \
    PasswordCodeValidateSerializer, UserUpdateSerializer, PasswordSetSerializer, UserGetSerializer

from .services import handle_user
from .tasks import send_password_recovery_email, send_email_verification_email
from helper.static_functions import get_errors_as_string

redis_con = redis.Redis(decode_responses=True)


class UserCreateAPIView(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserCreateSerializer
    permission_classes = [AllowAny]
    def perform_create(self, serializer):
        user = serializer.save()
        user.is_active = False 
        user.save()


class UserRetrieveAPIView(RetrieveAPIView):
    serializer_class = UserGetSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return User.objects.get(id=self.request.user.id)


class UserLoginAPIView(TokenObtainPairView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        password = request.data.get('password')
        user = authenticate(request, email=email, password=password)
        if user is not None:
            if user.is_active:
                refresh = RefreshToken.for_user(user)
                access_token = str(refresh.access_token)
                return Response({
                    'access_token': access_token,
                    'refresh_token': str(refresh),
                }, status=status.HTTP_200_OK)
        elif not handle_user.is_email_verified(email):
            return Response({'detail': 'Вам необхідно підтвердити свій email, щоб закінчити реєстрацію'},
                            status=status.HTTP_409_CONFLICT)       
        else:
            print(user)
            return Response({'detail': 'Введені неправильні дані облікового запису.'},
                            status=status.HTTP_401_UNAUTHORIZED)
        

class UserUpdateAPIView(RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserUpdateSerializer

    def get_queryset(self):
        return User.objects.filter(email=self.request.user.email)

    def get_object(self):
        return self.get_queryset().first()


class AccessRecovery(APIView):
    def post(self, request, *args, **kwargs):
        refresh_token_value = request.data.get('refresh_token')

        if refresh_token_value:
            try:
                refresh = RefreshToken(refresh_token_value)
                access_token = str(refresh.access_token)

                return Response({
                    'access_token': access_token,
                    'refresh_token': str(refresh),
                }, status=status.HTTP_200_OK)
            except:
                return Response({'detail': 'Refresh token вказано з помилкою або він застарілий', 'expired': 'true'}, status=status.HTTP_401_UNAUTHORIZED)

        else:
            return Response({'detail': 'Refresh token не введено.'},
                            status=status.HTTP_400_BAD_REQUEST)
        
    
class CodeValidateApiView(APIView):

    def post(self, request):
        serializer = PasswordCodeValidateSerializer(data=request.data)
        if serializer.is_valid():
            real_code = redis_con.get(serializer.data['email'])
            if not real_code:
                return Response(
                    {"message": "Введений неправильний верифікаційний код або ж код застарів."},
                    status=status.HTTP_403_FORBIDDEN
                )

            is_valid = int(real_code) == serializer.data['code']
            if is_valid:
                redis_con.delete(serializer.data['email'])
                user = User.objects.get(email=serializer.data['email'])
                user.is_active = True
                user.save()

            return Response({"valid": is_valid}, status=status.HTTP_200_OK)

        return Response("Okay", status=status.HTTP_200_OK)


class EmailConfirmationSendCodeView(APIView):

    def post(self, request):
        serializer = EmailSerializer(data=request.data)
        if serializer.is_valid():
            code = randint(100000, 999999)
            redis_con.set(serializer.data['email'], code, "300")

            send_email_verification_email.s(
                serializer.data['email'],
                code
            ).apply_async()
            return Response("Okay", status=status.HTTP_200_OK)

        message = get_errors_as_string(serializer)
        return Response({"message": message}, status=status.HTTP_403_FORBIDDEN)


class PasswordResetApiView(APIView):

    def post(self, request):
        serializer = EmailSerializer(data=request.data)
        if serializer.is_valid():
            try:
                user = handle_user.get_user_by_email(serializer.data['email'])
            except Exception:
                return Response(
                    {"message": f"На жаль користувача з електронною адресою {serializer.data['email']} не зареєстровано."},
                    status=status.HTTP_403_FORBIDDEN
                )

            code = randint(100000, 999999)
            redis_con.set(serializer.data['email'], code, "300")
            send_password_recovery_email.s(
                serializer.data['email'],
                user.name if user.name else "",
                user.surname if user.surname else "",
                code
            ).apply_async()

            return Response("Okay", status=status.HTTP_200_OK)

        message = get_errors_as_string(serializer)
        return Response({"message": message}, status=status.HTTP_403_FORBIDDEN)

class CreateStaffUserAPIView(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserCreateSerializer
    permission_classes = [IsAdminUser]  

    def perform_create(self, serializer):
        user = serializer.save()
        user.is_active = True  
        user.is_staff = True
        user.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    

class PasswordSetApiView(APIView):

    def post(self, request):
        serializer = PasswordSetSerializer(data=request.data)
        if serializer.is_valid():
            try:
                user = handle_user.get_user_by_email(serializer.data['email'])
                user.set_password(serializer.data['password'])
                user.save()

                return Response("Okay", status=status.HTTP_200_OK)
            except:
                return Response({"detail": "На платформі немає зареєстрованих користувачів з такою електроною поштою."}, status=status.HTTP_404_NOT_FOUND)

        message = get_errors_as_string(serializer)
        return Response({"detail": message}, status=status.HTTP_403_FORBIDDEN)
    

class UserStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        organization_id = kwargs.get('organization_pk')
        if not organization_id:
            return Response({'is_organization_creator': False, 'is_organization_staff': False, 'is_staff_user': False}, status=status.HTTP_200_OK)
        
        user = request.user
        is_staff_user = IsStaffUser().has_permission(request, self)
        
        # Check if the user is the creator of the organization and if the organization is active
        try:
            organization = Organization.objects.get(pk=organization_id, created_by=user)
            is_organization_creator = True
            is_organization_staff = True
        except Organization.DoesNotExist:
            is_organization_creator = False
            is_organization_staff = IsOrganizationStaff(organization_pk=organization_id).has_permission(request, self)
        
        return Response({
            'is_organization_creator': is_organization_creator,
            'is_organization_staff': is_organization_staff,
            'is_staff_user': is_staff_user
        }, status=status.HTTP_200_OK)


class UserOrganizations(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        organizations = Organization.objects.filter(organization_staff__user=user, organization_staff__status=OrganizationStaff.APPROVED)
        serializer = OrganizationSerializer(organizations, many=True)


        return Response(serializer.data)
