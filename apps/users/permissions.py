from rest_framework.permissions import BasePermission

class IsSuperAdmin(BasePermission):
    """
    Allows access only to users with user_role `SuperAdmin`.
    """
    
    def has_permission(self, request, view):
        print('test role ',request.user.user_role.role_code)
        return (
            request.user
            and request.user.is_authenticated
            and hasattr(request.user, 'role')  
            and request.user.user_role
            and request.user.user_role.role_code == 'SuperAdmin'
        )


class IsAdminOrSuperAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.user_role.role_code in ["Admin", "SuperAdmin"]