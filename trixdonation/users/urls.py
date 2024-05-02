from django.urls import path
from .views import AccessRecovery, UserCreateAPIView, UserLoginAPIView, CodeValidateApiView, EmailSendCodeView, UserUpdateAPIView

urlpatterns = [
    path(r'user/login/', UserLoginAPIView.as_view(), name='user-login'),
    path(r'user/access_token_recovery/', AccessRecovery.as_view(), name='access-token-recovery'),
    path(r'user/create/', UserCreateAPIView.as_view(), name='user-create'),
    path(r'user/', UserUpdateAPIView.as_view(), name='user'),
    path(r'email_verify/', EmailSendCodeView.as_view(), name='email_verify'),
    path(r'email_verify_validate/', CodeValidateApiView.as_view(),
         name='email_verify_validate'),
]