import pytest
from unittest.mock import patch, MagicMock
from django.core.cache import cache
from common.services.cache_service import (
    CacheKeyManager, CacheManager, CacheInvalidator, CacheContext
)


@pytest.fixture(autouse=True)
def clear_cache():
    cache.clear()
    CacheManager._pending_deletions = set()
    CacheManager._in_transaction = False
    yield
    cache.clear()


class TestCacheKeyManager:
    def test_make_key_with_prefix(self):
        key = CacheKeyManager.make_key('test:{id}', id=1)
        assert key == 'lims:test:1'

    def test_make_key_multiple_params(self):
        key = CacheKeyManager.make_key('stats:{user_id}:{sem_id}', user_id=5, sem_id=3)
        assert key == 'lims:stats:5:3'

    def test_get_dashboard_key(self):
        key = CacheKeyManager.get_dashboard_key(user_id=1)
        assert key == 'lims:statistics:dashboard:1'

    def test_get_comprehensive_key(self):
        key = CacheKeyManager.get_comprehensive_key(user_id=1, semester_id=2)
        assert key == 'lims:statistics:comprehensive:1:2'

    def test_cache_prefix_is_lims(self):
        assert CacheKeyManager.CACHE_PREFIX == 'lims:'


class TestCacheManager:
    def test_delete_directly(self):
        cache.set('test_key', 'test_value')
        CacheManager.delete('test_key')
        assert cache.get('test_key') is None

    def test_delete_many(self):
        cache.set('key1', 'val1')
        cache.set('key2', 'val2')
        CacheManager.delete_many(['key1', 'key2'])
        assert cache.get('key1') is None
        assert cache.get('key2') is None

    def test_delete_in_transaction_deferred(self):
        CacheManager._in_transaction = True
        CacheManager._pending_deletions = set()
        cache.set('deferred_key', 'value')
        CacheManager.delete('deferred_key')
        assert cache.get('deferred_key') == 'value'
        assert 'deferred_key' in CacheManager._pending_deletions

    def test_delete_many_in_transaction(self):
        CacheManager._in_transaction = True
        CacheManager._pending_deletions = set()
        CacheManager.delete_many(['key1', 'key2'])
        assert 'key1' in CacheManager._pending_deletions
        assert 'key2' in CacheManager._pending_deletions

    def test_delete_pattern_returns_int(self):
        result = CacheManager.delete_pattern('nonexistent_pattern:*')
        assert isinstance(result, int)


class TestCacheContext:
    def test_context_manager_commits_on_success(self):
        cache.set('ctx_key', 'value')
        with CacheContext():
            CacheManager.delete('ctx_key')
            assert cache.get('ctx_key') == 'value'
        assert cache.get('ctx_key') is None

    def test_context_manager_rollback_on_exception(self):
        cache.set('rollback_key', 'value')
        try:
            with CacheContext():
                CacheManager.delete('rollback_key')
                raise Exception('test error')
        except Exception:
            pass
        assert cache.get('rollback_key') == 'value'


class TestCacheInvalidator:
    def test_invalidate_user_cache(self):
        cache.set('api:user:permissions:1', 'perms')
        cache.set('api:user:info:1', 'info')
        CacheInvalidator.invalidate_user_cache(user_id=1)
        assert cache.get('api:user:permissions:1') is None
        assert cache.get('api:user:info:1') is None

    def test_invalidate_semester_cache(self):
        cache.set('api:semester:list:1', 'list')
        cache.set('api:semester:options:1', 'options')
        CacheInvalidator.invalidate_semester_cache()
        assert cache.get('api:semester:list:1') is None
        assert cache.get('api:semester:options:1') is None

    def test_invalidate_all_statistics(self):
        # 统计缓存统一为 api:stats:* 前缀（generate_cache_key 硬编码 api:），
        # 失效必须能真正清掉，不再允许"时好时坏"
        cache.set('api:stats:dashboard:1', 'data')
        cache.set('api:stats:comprehensive:1:2', 'data2')
        CacheInvalidator.invalidate_all_statistics()
        assert cache.get('api:stats:dashboard:1') is None
        assert cache.get('api:stats:comprehensive:1:2') is None
