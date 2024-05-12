from rest_framework.permissions import BasePermission
from organizations.models import OrganizationStaff
from money_collections.models import MoneyCollection


class IsStaffUser(BasePermission):
    """
    Custom permission to allow only staff members to access the view.
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_staff
        
    

class IsOrganizationStaff(BasePermission):
    """
    Custom permission to allow only staff of an organization to perform actions.
    """

    def __init__(self, organization_pk=None, money_collection_pk=None):
        self.organization_pk = organization_pk
        self.money_collection_pk = money_collection_pk
        super().__init__()

    def has_permission(self, request, view):
        organization_pk = None
        money_collection_pk = None
        money_collection_pk = self.money_collection_pk
        if not request.user.is_authenticated:
            return False
        
        if 'organization_pk' in view.kwargs:
            organization_pk = view.kwargs['organization_pk']
        elif 'money_collection_pk' in view.kwargs:
            money_collection_pk = view.kwargs['money_collection_pk']
        
        print(organization_pk)
        if organization_pk:
            return request.user.is_authenticated and OrganizationStaff.objects.filter(
                organization=organization_pk,
                user=request.user,
                ).exists()
        
        if money_collection_pk:
            try:
                money_collection = MoneyCollection.objects.get(pk=money_collection_pk)
            except MoneyCollection.DoesNotExist:
                return False
            
            organizations = money_collection.organizations.all()

            return any(OrganizationStaff.objects.filter(
                organization=organization.organization_id,
                user=request.user,
                ).exists() for organization in organizations)

        return False