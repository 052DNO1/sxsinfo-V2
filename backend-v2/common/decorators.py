"""
自定义装饰器
"""

import functools
import hashlib
import logging
import threading
from functools import wraps
from django.http import JsonResponse
from django.core.cache import cache
from apps.core.exceptions import PermissionDenied

logger = logging.getLogger(__name__)

DEFAULT_CACHE_TIMEOUT = 60

_thread_locals = threading.local()


def set_cache_hit(hit: bool):
    """设置当前线程的缓存命中状态"""
    _thread_locals.cache_hit = hit


def is_cache_hit() -> bool:
    """获取当前线程的缓存命中状态"""
    return getattr(_thread_locals, 'cache_hit', False)


def clear_cache_hit():
    """清除当前线程的缓存命中状态"""
    _thread_locals.cache_hit = False


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


def generate_cache_key(prefix, *args, **kwargs):
    """生成缓存键"""
    key_parts = [prefix]
    
    for arg in args:
        if hasattr(arg, 'id'):
            key_parts.append(str(arg.id))
        elif hasattr(arg, 'pk'):
            key_parts.append(str(arg.pk))
        else:
            key_parts.append(str(arg))
    
    for k, v in sorted(kwargs.items()):
        if v is not None:
            key_parts.append(f"{k}:{v}")
    
    key_string = ":".join(key_parts)
    
    if len(key_string) > 200:
        hash_obj = hashlib.md5(key_string.encode())
        key_string = f"{prefix}:{hash_obj.hexdigest()}"
    
    return f"api:{key_string}"


def cached_api(timeout=DEFAULT_CACHE_TIMEOUT, key_prefix=None, skip_args=None):
    """
    API缓存装饰器
    
    用法:
        @cached_api(timeout=60)
        def get_list(self, requester, page=1, page_size=20):
            ...
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            prefix = key_prefix or func.__name__
            
            cache_args = args
            cache_kwargs = kwargs.copy()
            
            if skip_args:
                for arg_name in skip_args:
                    cache_kwargs.pop(arg_name, None)
            
            cache_key = generate_cache_key(prefix, *cache_args, **cache_kwargs)
            
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                logger.debug(f"Cache hit: {cache_key}")
                set_cache_hit(True)
                return cached_result
            
            logger.debug(f"Cache miss: {cache_key}")
            set_cache_hit(False)
            
            result = func(*args, **kwargs)
            
            if result is not None:
                cache.set(cache_key, result, timeout)
                logger.debug(f"Cache set: {cache_key}, timeout: {timeout}s")
            
            return result
        
        return wrapper
    return decorator


def cached_method(timeout=DEFAULT_CACHE_TIMEOUT, key_prefix=None):
    """
    方法缓存装饰器，专门用于类方法
    
    用法:
        class MyService:
            @cached_method(timeout=60)
            def get_data(self, user_id):
                ...
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            prefix = key_prefix or f"{self.__class__.__name__}.{func.__name__}"
            
            cache_key = generate_cache_key(prefix, *args, **kwargs)
            
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                logger.debug(f"Cache hit: {cache_key}")
                set_cache_hit(True)
                return cached_result
            
            logger.debug(f"Cache miss: {cache_key}")
            set_cache_hit(False)
            
            result = func(self, *args, **kwargs)
            
            if result is not None:
                cache.set(cache_key, result, timeout)
                logger.debug(f"Cache set: {cache_key}, timeout: {timeout}s")
            
            return result
        
        return wrapper
    return decorator


def invalidate_cache_on_success(resource_types):
    """
    操作成功后清除相关缓存的装饰器
    
    用法:
        @invalidate_cache_on_success(['schedules', 'statistics'])
        def create_schedule(self, requester, data):
            ...
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            
            try:
                from common.services.cache_service import CacheInvalidator
                for resource_type in resource_types:
                    try:
                        CacheInvalidator.invalidate_by_resource_type(resource_type)
                    except Exception as e:
                        logger.warning(f"Failed to invalidate cache for {resource_type}: {e}")
            except Exception as e:
                logger.warning(f"Failed to import CacheInvalidator: {e}")
            
            return result
        
        return wrapper
    return decorator
