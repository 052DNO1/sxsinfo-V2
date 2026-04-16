"""
缓存管理服务
提供统一的缓存管理和清理机制
"""

import logging
import functools
from typing import List, Optional, Set, Callable, Any
from django.core.cache import cache
from django.db import transaction

logger = logging.getLogger(__name__)


class CacheKeyManager:
    """缓存键管理器"""

    CACHE_PREFIX = 'lims:'

    STATISTICS_DASHBOARD = 'statistics:dashboard:{user_id}'
    STATISTICS_COMPREHENSIVE = 'statistics:comprehensive:{user_id}:{semester_id}'
    STATISTICS_TEACHER = 'statistics:teacher:{user_id}'
    STATISTICS_LAB_ADMIN = 'statistics:lab_admin:{user_id}'

    ARCHIVE_SETTINGS = 'archive:settings'
    SEMESTER_CURRENT = 'semester:current'
    SEMESTER_OPTIONS = 'semester:options'

    LABORATORY_OPTIONS = 'laboratory:options:{user_id}'
    EQUIPMENT_OPTIONS = 'equipment:options:{user_id}'

    USER_PERMISSIONS = 'user:permissions:{user_id}'
    USER_INFO = 'user:info:{user_id}'

    @classmethod
    def make_key(cls, template: str, **kwargs) -> str:
        return f"{cls.CACHE_PREFIX}{template.format(**kwargs)}"

    @classmethod
    def get_dashboard_key(cls, user_id: int) -> str:
        return cls.make_key(cls.STATISTICS_DASHBOARD, user_id=user_id)

    @classmethod
    def get_comprehensive_key(cls, user_id: int, semester_id: int) -> str:
        return cls.make_key(cls.STATISTICS_COMPREHENSIVE, user_id=user_id, semester_id=semester_id)

    @classmethod
    def get_teacher_stats_key(cls, user_id: int) -> str:
        return cls.make_key(cls.STATISTICS_TEACHER, user_id=user_id)

    @classmethod
    def get_lab_admin_stats_key(cls, user_id: int) -> str:
        return cls.make_key(cls.STATISTICS_LAB_ADMIN, user_id=user_id)


class CacheManager:
    """缓存管理器"""

    _pending_deletions: Set[str] = set()
    _in_transaction: bool = False

    @classmethod
    def delete(cls, key: str) -> None:
        if cls._in_transaction:
            cls._pending_deletions.add(key)
        else:
            cache.delete(key)
            logger.debug(f"Cache deleted: {key}")

    @classmethod
    def delete_many(cls, keys: List[str]) -> None:
        if cls._pending_deletions is None:
            cls._pending_deletions = set()

        if cls._in_transaction:
            cls._pending_deletions.update(keys)
        else:
            for key in keys:
                cache.delete(key)
                logger.debug(f"Cache deleted: {key}")

    @classmethod
    def delete_pattern(cls, pattern: str) -> int:
        try:
            if not pattern.endswith('*'):
                pattern = pattern + '*'
            keys = cache.keys(pattern)
            if keys:
                cache.delete_many(keys)
                logger.info(f"Cache pattern deleted: {pattern}, keys: {keys}")
                return len(keys)
            else:
                logger.info(f"No cache keys found for pattern: {pattern}")
        except Exception as e:
            logger.warning(f"Failed to delete cache pattern {pattern}: {e}")
        return 0

    @classmethod
    def flush_pending(cls) -> None:
        if cls._pending_deletions:
            for key in cls._pending_deletions:
                try:
                    cache.delete(key)
                    logger.debug(f"Cache deleted (pending): {key}")
                except Exception as e:
                    logger.warning(f"Failed to delete cache {key}: {e}")
            cls._pending_deletions.clear()

    @classmethod
    def clear_pending(cls) -> None:
        cls._pending_deletions.clear()

    @classmethod
    def enter_transaction(cls) -> None:
        cls._in_transaction = True
        cls._pending_deletions = set()

    @classmethod
    def exit_transaction(cls, success: bool = True) -> None:
        if success:
            cls.flush_pending()
        else:
            cls.clear_pending()
        cls._in_transaction = False


class CacheInvalidator:
    """缓存失效器 - 根据数据变更类型清理相关缓存"""

    @staticmethod
    def invalidate_schedule_cache(user_id: int = None, department_id: int = None) -> None:
        CacheManager.delete_pattern("api:schedule:list:*")

        keys_to_delete = []

        if user_id:
            keys_to_delete.extend([
                CacheKeyManager.get_dashboard_key(user_id),
                CacheKeyManager.get_teacher_stats_key(user_id),
                CacheKeyManager.get_lab_admin_stats_key(user_id),
            ])

        CacheManager.delete_pattern(f"{CacheKeyManager.CACHE_PREFIX}statistics:dashboard:*")
        CacheManager.delete_pattern(f"{CacheKeyManager.CACHE_PREFIX}statistics:comprehensive:*")

        if keys_to_delete:
            CacheManager.delete_many(keys_to_delete)

        logger.info(f"Schedule cache invalidated for user={user_id}, dept={department_id}")

    @staticmethod
    def invalidate_laboratory_cache(user_id: int = None, department_id: int = None) -> None:
        CacheManager.delete_pattern("api:lab:list:*")
        CacheManager.delete_pattern(f"{CacheKeyManager.CACHE_PREFIX}statistics:dashboard:*")
        CacheManager.delete_pattern(f"{CacheKeyManager.CACHE_PREFIX}statistics:comprehensive:*")
        CacheManager.delete_pattern(f"{CacheKeyManager.CACHE_PREFIX}laboratory:options:*")

        logger.info(f"Laboratory cache invalidated for user={user_id}, dept={department_id}")

    @staticmethod
    def invalidate_equipment_cache(user_id: int = None) -> None:
        CacheManager.delete_pattern("api:equipment:list:*")
        CacheManager.delete_pattern(f"{CacheKeyManager.CACHE_PREFIX}statistics:dashboard:*")
        CacheManager.delete_pattern(f"{CacheKeyManager.CACHE_PREFIX}statistics:comprehensive:*")
        CacheManager.delete_pattern(f"{CacheKeyManager.CACHE_PREFIX}equipment:options:*")

        logger.info(f"Equipment cache invalidated for user={user_id}")

    @staticmethod
    def invalidate_user_cache(user_id: int = None) -> None:
        CacheManager.delete_pattern("api:user:list:*")

        if user_id:
            CacheManager.delete_many([
                CacheKeyManager.make_key(CacheKeyManager.USER_PERMISSIONS, user_id=user_id),
                CacheKeyManager.make_key(CacheKeyManager.USER_INFO, user_id=user_id),
            ])

        CacheManager.delete_pattern(f"{CacheKeyManager.CACHE_PREFIX}statistics:dashboard:*")
        CacheManager.delete_pattern(f"{CacheKeyManager.CACHE_PREFIX}statistics:comprehensive:*")

        logger.info(f"User cache invalidated for user={user_id}")

    @staticmethod
    def invalidate_work_order_cache(user_id: int = None, department_id: int = None) -> None:
        CacheManager.delete_pattern("api:workorder:list:*")
        CacheManager.delete_pattern(f"{CacheKeyManager.CACHE_PREFIX}statistics:dashboard:*")
        CacheManager.delete_pattern(f"{CacheKeyManager.CACHE_PREFIX}statistics:comprehensive:*")

        logger.info(f"Work order cache invalidated for user={user_id}, dept={department_id}")

    @staticmethod
    def invalidate_record_cache(user_id: int = None, department_id: int = None) -> None:
        CacheManager.delete_pattern("api:record:list:*")
        CacheManager.delete_pattern(f"{CacheKeyManager.CACHE_PREFIX}statistics:dashboard:*")
        CacheManager.delete_pattern(f"{CacheKeyManager.CACHE_PREFIX}statistics:comprehensive:*")

        logger.info(f"Record cache invalidated for user={user_id}, dept={department_id}")

    @staticmethod
    def invalidate_semester_cache() -> None:
        CacheManager.delete_pattern("api:semester:list:*")
        CacheManager.delete(CacheKeyManager.make_key(CacheKeyManager.SEMESTER_CURRENT))
        CacheManager.delete(CacheKeyManager.make_key(CacheKeyManager.SEMESTER_OPTIONS))
        CacheManager.delete_pattern(f"{CacheKeyManager.CACHE_PREFIX}statistics:*")

        logger.info("Semester cache invalidated")

    @staticmethod
    def invalidate_all_statistics() -> None:
        CacheManager.delete_pattern(f"{CacheKeyManager.CACHE_PREFIX}statistics:*")

        logger.info("All statistics cache invalidated")


def cache_invalidate(*invalidators: Callable[..., None], **invalidator_kwargs):
    """
    缓存清理装饰器
    操作成功后自动清理缓存，操作失败则不清理

    用法:
        @cache_invalidate(CacheInvalidator.invalidate_schedule_cache, user_id='requester.id')
        def create_schedule(self, requester, data):
            ...

        @cache_invalidate(CacheInvalidator.invalidate_laboratory_cache)
        def update_laboratory(self, requester, laboratory_id, data):
            ...
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            resolved_kwargs = invalidator_kwargs.copy()

            for key, value in resolved_kwargs.items():
                if isinstance(value, str) and '.' in value:
                    parts = value.split('.')
                    obj = None

                    if parts[0] == 'requester' and len(args) > 1:
                        obj = args[1] if hasattr(args[1], 'id') else kwargs.get('requester')
                    elif parts[0] == 'self' and len(args) > 0:
                        obj = args[0]

                    if obj:
                        for part in parts[1:]:
                            obj = getattr(obj, part, None)
                            if obj is None:
                                break
                        resolved_kwargs[key] = obj

            result = func(*args, **kwargs)

            for invalidator in invalidators:
                try:
                    invalidator(**resolved_kwargs)
                except Exception as e:
                    logger.warning(f"Cache invalidation failed: {e}")

            return result

        return wrapper
    return decorator


def cache_invalidate_on_success(*cache_keys: str):
    """
    简单的缓存清理装饰器
    操作成功后清理指定的缓存键

    用法:
        @cache_invalidate_on_success('dashboard_stats', 'comprehensive_stats')
        def update_data(self):
            ...
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            result = func(*args, **kwargs)

            for key in cache_keys:
                try:
                    CacheManager.delete(key)
                except Exception as e:
                    logger.warning(f"Failed to delete cache key {key}: {e}")

            return result

        return wrapper
    return decorator


class CacheContext:
    """
    缓存上下文管理器
    用于事务中的缓存清理

    用法:
        with CacheContext():
            with transaction.atomic():
                schedule.delete()
                CacheInvalidator.invalidate_schedule_cache()
    """

    def __enter__(self):
        CacheManager.enter_transaction()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        success = exc_type is None
        CacheManager.exit_transaction(success=success)
        return False


def with_cache_invalidation(invalidator_func: Callable[..., None], **kwargs_resolver):
    """
    带参数解析的缓存清理装饰器

    用法:
        @with_cache_invalidation(
            CacheInvalidator.invalidate_schedule_cache,
            user_id=lambda args, kwargs: args[1].id if len(args) > 1 else kwargs.get('requester').id
        )
        def create_schedule(self, requester, data):
            ...
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            result = func(*args, **kwargs)

            resolved_kwargs = {}
            for key, resolver in kwargs_resolver.items():
                if callable(resolver):
                    resolved_kwargs[key] = resolver(args, kwargs)
                else:
                    resolved_kwargs[key] = resolver

            try:
                invalidator_func(**resolved_kwargs)
            except Exception as e:
                logger.warning(f"Cache invalidation failed: {e}")

            return result

        return wrapper
    return decorator
