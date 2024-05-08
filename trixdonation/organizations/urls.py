from django.urls import path
from .views import OrganizationRequestCreateView, StaffOrganizationRequestListView, StaffOrganizationRequestRetrieveUpdateView, \
    OrganizationRequestRetrieveUpdateView, OrganizationListView, OrganizationEditView, ManageOrganizationStaffView, ApproveDeclineOrganizationStaffView

urlpatterns = [
    path(r'request/create/', OrganizationRequestCreateView.as_view(), name='request-create'),
    path(r'requests/', StaffOrganizationRequestListView.as_view(), name='organization-request-list'),
    path(r'user/request/', OrganizationRequestRetrieveUpdateView.as_view(), name='user-organization-request'),
    path(r'requests/<int:pk>/', StaffOrganizationRequestRetrieveUpdateView.as_view(), name='organization-request-detail'),
    path(r'organizations/', OrganizationListView.as_view(), name='organization-list'), 
    path(r'organizations/edit/', OrganizationEditView.as_view(), name='organization-edit'),
    path(r'organizations/<int:pk>/staff/', ManageOrganizationStaffView.as_view(), name='manage_organization_staff_action'),

    path('organization-staff/<pk>/change-status/<status>/', ApproveDeclineOrganizationStaffView.as_view(),
         name='approve-decline-organization-staff')
]