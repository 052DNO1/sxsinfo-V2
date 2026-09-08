"""
公共 DRF 权限类

统一放置角色级权限判定，供各 app 视图复用，避免散落 if 判断。
"""

from rest_framework.permissions import BasePermission


class IsSuperAdmin(BasePermission):
    """仅超级管理员（含 Django superuser）可访问"""

    message = '仅超级管理员可执行此操作'

    def has_permission(self, request, view):
        user = request.user
        return bool(user and user.is_authenticated and user.is_super_admin)


class IsSystemAdmin(BasePermission):
    """系统管理员及以上（superuser / SYSTEM_ADMIN / SUPER_ADMIN）可访问"""

    message = '仅系统管理员可执行此操作'

    def has_permission(self, request, view):
        user = request.user
        return bool(user and user.is_authenticated and user.is_system_admin)


class IsDepartmentAdminOrAbove(BasePermission):
    """分院管理员及以上（superuser / SUPER_ADMIN / SYSTEM_ADMIN / DEPARTMENT_ADMIN）"""

    message = '无权限执行此操作'

    def has_permission(self, request, view):
        user = request.user
        if not (user and user.is_authenticated):
            return False
        return bool(
            user.is_super_admin
            or user.is_system_admin
            or user.is_department_admin
        )
