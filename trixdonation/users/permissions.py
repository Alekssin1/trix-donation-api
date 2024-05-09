from rest_framework.permissions import BasePermission
from organizations.models import OrganizationStaff


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

    def has_permission(self, request, view):
        # Check if the user is authenticated and a staff member of the organization
        return request.user.is_authenticated and OrganizationStaff.objects.filter(
            organization=view.kwargs.get('organization_pk'),
            user=request.user,
        ).exists()