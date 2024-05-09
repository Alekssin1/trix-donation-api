from django.urls import path
from .views import OrganizationRequestCreateView, StaffOrganizationRequestListView, StaffOrganizationRequestRetrieveUpdateView, \
    OrganizationRequestRetrieveUpdateView, OrganizationListView, OrganizationEditView, ManageOrganizationStaffView, ApproveDeclineOrganizationStaffView, \
    OrganizationRetrieveView, PostListCreateView, PostRetrieveUpdateDestroyView, PostListView, UserSubscribedOrganizationsList, OrganizationSubscriptionCreateView, \
    OrganizationSubscriptionDeleteView, OrganizationSubscriptionStatusView

urlpatterns = [

    path(r'request/create/', OrganizationRequestCreateView.as_view(), name='request-create'),
    path(r'requests/', StaffOrganizationRequestListView.as_view(), name='organization-request-list'),
    path(r'user/request/', OrganizationRequestRetrieveUpdateView.as_view(), name='user-organization-request'),
    path(r'requests/<int:pk>/', StaffOrganizationRequestRetrieveUpdateView.as_view(), name='organization-request-detail'),
    path(r'organizations/', OrganizationListView.as_view(), name='organization-list'), 
    path(r'organizations/<int:pk>/', OrganizationRetrieveView.as_view(), name='organization-detail'),
    path(r'organizations/edit/', OrganizationEditView.as_view(), name='organization-edit'),
    path(r'organizations/<int:pk>/staff/', ManageOrganizationStaffView.as_view(), name='manage_organization_staff_action'),

    path(r'organization-staff/<pk>/change-status/<status>/', ApproveDeclineOrganizationStaffView.as_view(),
         name='approve-decline-organization-staff'),

    path(r'organizations/<int:organization_pk>/posts/', PostListCreateView.as_view(), name='post-list-create'),
    path(r'organizations/<int:organization_pk>/posts/<int:pk>', PostRetrieveUpdateDestroyView.as_view(), name='post-retrieve-update-destroy'),
    path(r'organizations/<int:organization_pk>/posts/all/', PostListView.as_view(), name='post-list'),
    
    path(r'organization-subscriptions/create/', OrganizationSubscriptionCreateView.as_view(), name='organization-subscription-create'),
    path(r'organization-subscriptions/delete/', OrganizationSubscriptionDeleteView.as_view(), name='organization-subscription-delete'),
    path(r'user/subscribed-organizations/', UserSubscribedOrganizationsList.as_view(), name='user-subscribed-organizations-list'),
    path(r'organizations/<int:organization_pk>/subscription-status/', OrganizationSubscriptionStatusView.as_view(), name='organization-subscription-status'),


]