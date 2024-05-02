from random import randint
import redis
from rest_framework import status
from rest_framework.generics import (
    CreateAPIView,
    RetrieveUpdateAPIView
)
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User
from .serializers import UserCreateSerializer, EmailSerializer, \
    PasswordCodeValidateSerializer, UserUpdateSerializer

from .services import handle_user
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


class UserLoginAPIView(TokenObtainPairView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        password = request.data.get('password')
        user = authenticate(request, email=email, password=password)
        if user is not None:
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            return Response({
                'access_token': access_token,
                'refresh_token': str(refresh),
            }, status=status.HTTP_200_OK)
        else:
            return Response({'detail': 'Invalid credentials'},
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
            refresh = RefreshToken(refresh_token_value)
            access_token = str(refresh.access_token)

            return Response({
                'access_token': access_token,
                'refresh_token': str(refresh),
            }, status=status.HTTP_200_OK)
        else:
            return Response({'detail': 'Refresh token is missing'},
                            status=status.HTTP_400_BAD_REQUEST)
        
    
class CodeValidateApiView(APIView):

    def post(self, request):
        serializer = PasswordCodeValidateSerializer(data=request.data)
        if serializer.is_valid():
            real_code = redis_con.get(serializer.data['email'])
            if not real_code:
                return Response(
                    {"message": "Verification code is expired"},
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


class EmailSendCodeView(APIView):

    def post(self, request):
        serializer = EmailSerializer(data=request.data)
        if serializer.is_valid():
            code = randint(100000, 999999)
            redis_con.set(serializer.data['email'], code, "300")

            handle_user.handle_send_email_verify(
                serializer.data['email'],
                code
            )
            return Response("Okay", status=status.HTTP_200_OK)

        message = get_errors_as_string(serializer)
        return Response({"message": message}, status=status.HTTP_403_FORBIDDEN)

