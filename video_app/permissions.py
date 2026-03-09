from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsStaff(BasePermission):
    """
    Permission class to allow access only to staff users.

    This permission handles:
    - granting access to users with is_staff=True
    - allowing read-only requests (GET, HEAD, OPTIONS) for any user
    """

    def has_permission(self, request, view):
        is_staff = bool(request.user and request.user.is_staff)
        return is_staff or request.method in SAFE_METHODS