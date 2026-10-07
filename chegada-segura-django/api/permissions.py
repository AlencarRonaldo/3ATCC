from rest_framework.permissions import BasePermission
class RolesPermission(BasePermission):
    allowed_roles=()
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.active and request.user.role in self.allowed_roles)
class AnyStaff(RolesPermission): allowed_roles=('ADMIN','DIRECTION','EMPLOYEE')
class DirectionOrAdmin(RolesPermission): allowed_roles=('ADMIN','DIRECTION')
class AdminOnly(RolesPermission): allowed_roles=('ADMIN',)
class StaffForTablet(RolesPermission): allowed_roles=('ADMIN','DIRECTION','EMPLOYEE')
