from django.urls import path
from .views import AccessRecovery, UserCreateAPIView, UserLoginAPIView, CodeValidateApiView, EmailConfirmationSendCodeView,\
PasswordResetApiView, PasswordSetApiView, UserUpdateAPIView, CreateStaffUserAPIView

urlpatterns = [
    path(r'login/', UserLoginAPIView.as_view(), name='user-login'),
    path(r'access_token_recovery/', AccessRecovery.as_view(), name='access-token-recovery'),
    path(r'create/', UserCreateAPIView.as_view(), name='user-create'),
    path(r'create_staff/', CreateStaffUserAPIView.as_view(), name='create-staff-user'),
    path(r'edit/', UserUpdateAPIView.as_view(), name='user-edit'),
    path(r'password_reset/', PasswordResetApiView.as_view(),
         name="password_reset"),
    path(r'password_set/', PasswordSetApiView.as_view(), name="password_set"),
    path(r'email_verify/', EmailConfirmationSendCodeView.as_view(), name='email_verify'),
    path(r'code_validate/', CodeValidateApiView.as_view(),
         name='validate_code'),
]