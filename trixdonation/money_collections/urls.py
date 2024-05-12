from django.urls import path
from .views import MoneyCollectionCreateAPIView, MonoJarDataView, OrganizationsMoneyCollectionListView, MoneyCollectionListView, MoneyCollectionRetrieveUpdateAPIView, BankCardCreateAPIView,\
BankCardRetrieveUpdateDestroyAPIView, OtherRequisitesCreateAPIView, OtherRequisiteRetrieveUpdateDestroyAPIView, MoneyCollectionSubscriptionCreateView,\
MoneyCollectionSubscriptionDeleteView, MoneyCollectionSubscriptionStatusView, MoneyCollectionOrganizationsList, ReportListCreateView, \
ReportRetrieveUpdateDestroyView, ReportListView
urlpatterns = [
    path(r'organizations/<int:organization_pk>/money_collections/', MoneyCollectionCreateAPIView.as_view(), name='money_collection_create'),
    path(r'jar/', MonoJarDataView.as_view(), name='mono_jar_info'),
    path(r'organizations/<int:organization_pk>/collections/', OrganizationsMoneyCollectionListView.as_view(), name='organization_money_collection_list'),
    path(r'<int:money_collection_pk>/', MoneyCollectionRetrieveUpdateAPIView.as_view(), name='money_collection_detail'),
    path(r'<int:money_collection_pk>/requisites/<int:requisites_id>/bank_card_create/', BankCardCreateAPIView.as_view(), name="create_bank_card"),
    path(r'<int:money_collection_pk>/requisites/<int:requisites_id>/other_requisite_create/', OtherRequisitesCreateAPIView.as_view(), name="create_other_requisite"),
    path(r'organizations/<int:organization_pk>/bank_card/<int:pk>/', BankCardRetrieveUpdateDestroyAPIView.as_view(), name='bankcard_detail'),
    path(r'organizations/<int:organization_pk>/other_requisite/<int:pk>/', OtherRequisiteRetrieveUpdateDestroyAPIView.as_view(), name='otherrequisite_detail'),
    path(r'', MoneyCollectionListView.as_view(), name='money_collection_list'),

    path(r'<int:money_collection_pk>/reports/', ReportListCreateView.as_view(), name='report-list-create'),
    path(r'<int:money_collection_pk>/reports/<int:pk>', ReportRetrieveUpdateDestroyView.as_view(), name='report-retrieve-update-destroy'),
    path(r'<int:money_collection_pk>/collection_reposts/', ReportListView.as_view(), name='collection-report-list'),

    path(r'collection-subscriptions/create/', MoneyCollectionSubscriptionCreateView.as_view(), name='money_collection-subscription-create'),
    path(r'collection-subscriptions/delete/', MoneyCollectionSubscriptionDeleteView.as_view(), name='money_collection-subscription-delete'),
    path(r'collections/<int:money_collection_pk>/subscription-status/', MoneyCollectionSubscriptionStatusView.as_view(), name='money_collection-subscription-status'),
    path(r'user/subscribed-collections/', MoneyCollectionOrganizationsList.as_view(), name='user-subscribed-collections-list'),

] 