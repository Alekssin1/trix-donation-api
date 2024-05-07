from rest_framework.permissions import BasePermission

class IsStaffUser(BasePermission):
    """
    Custom permission to allow only staff members to access the view.
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_staff