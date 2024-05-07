from django.urls import path
from .views import OrganizationRequestCreateView, OrganizationRequestListView, OrganizationRequestRetrieveUpdateView

urlpatterns = [
    path(r'request/create/', OrganizationRequestCreateView.as_view(), name='request-create'),
    path(r'requests/', OrganizationRequestListView.as_view(), name='organization-request-list'),
    path(r'requests/<int:pk>/', OrganizationRequestRetrieveUpdateView.as_view(), name='organization-request-detail'),
]