from rest_framework.permissions import BasePermission

class IsInGroup(BasePermission):
    """
    Custom permission to check if the user is a Manager or Superuser
    """
    def has_permission(self, request, view):
        return request.user.groups.filter(name='Manager').exists() or request.user.is_superuser
