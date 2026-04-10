"""
自定义装饰器
"""

from functools import wraps
from django.http import JsonResponse
from apps.core.exceptions import PermissionDenied


def permission_required(permission_code):
    """权限检查装饰器"""
    def decorator(func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return JsonResponse({
                    'success': False,
                    'code': 'UNAUTHORIZED',
                    'message': '请先登录'
                }, status=401)
            
            if not request.user.has_perm(permission_code):
                raise PermissionDenied(f'缺少权限: {permission_code}')
            
            return func(request, *args, **kwargs)
        return wrapper
    return decorator


def role_required(*roles):
    """角色检查装饰器"""
    def decorator(func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return JsonResponse({
                    'success': False,
                    'code': 'UNAUTHORIZED',
                    'message': '请先登录'
                }, status=401)
            
            from apps.core.constants import UserRole
            has_role = any(request.user.has_role(role) for role in roles)
            if not has_role and not request.user.is_superuser:
                raise PermissionDenied('权限不足')
            
            return func(request, *args, **kwargs)
        return wrapper
    return decorator


def log_action(action_name):
    """操作日志装饰器"""
    def decorator(func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            import logging
            logger = logging.getLogger('action')
            logger.info(f"用户 {request.user} 执行操作: {action_name}")
            return func(request, *args, **kwargs)
        return wrapper
    return decorator
