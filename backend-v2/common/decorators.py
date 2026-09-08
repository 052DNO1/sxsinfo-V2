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
    """
    生成缓存键
    
    【已改进】正确处理对象参数，使用ID而不是字符串表示
    """
    key_parts = [prefix]
    
    for arg in args:
        if hasattr(arg, 'id'):
            key_parts.append(str(arg.id))
        elif hasattr(arg, 'pk'):
            key_parts.append(str(arg.pk))
        else:
            key_parts.append(str(arg))
    
    for k, v in sorted(kwargs.items()):
        if v is None:
            continue
        
        if hasattr(v, 'id'):
            key_parts.append(f"{k}:{v.id}")
        elif hasattr(v, 'pk'):
            key_parts.append(f"{k}:{v.pk}")
        elif isinstance(v, (list, tuple)):
            key_parts.append(f"{k}:{','.join(str(i) for i in v)}")
        elif isinstance(v, dict):
            sorted_items = sorted(v.items())
            key_parts.append(f"{k}:{','.join(f'{sk}:{sv}' for sk, sv in sorted_items if sv is not None)}")
        else:
            key_parts.append(f"{k}:{v}")
    
    key_string = ":".join(key_parts)
    
    if len(key_string) > 200:
        hash_obj = hashlib.md5(key_string.encode())
        key_string = f"{prefix}:{hash_obj.hexdigest()}"
    
    return f"api:{key_string}"


def cached_method(timeout=DEFAULT_CACHE_TIMEOUT, key_prefix=None):
    """
    方法缓存装饰器，专门用于类方法
    
    【已改进】自动检测并包含用户ID，防止数据串台
    
    用法:
        class MyService:
            @cached_method(timeout=60)
            def get_data(self, requester, ...):  # requester 参数会被自动包含在缓存key中
                ...
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            prefix = key_prefix or f"{self.__class__.__name__}.{func.__name__}"
            
            cache_kwargs = kwargs.copy()
            
            if args and hasattr(args[0], 'id') and hasattr(args[0], 'is_authenticated'):
                requester_id = args[0].id
                cache_kwargs['_uid'] = requester_id
                logger.debug(f"[Cache] Auto-include requester.id={requester_id} in cache key")
            
            if 'requester' in kwargs and hasattr(kwargs['requester'], 'id'):
                requester_id = kwargs['requester'].id
                cache_kwargs['_uid'] = requester_id
                cache_kwargs.pop('requester', None)
                logger.debug(f"[Cache] Auto-include requester.id={requester_id} in cache key (from kwargs)")
            
            cache_key = generate_cache_key(prefix, **cache_kwargs)
            
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
