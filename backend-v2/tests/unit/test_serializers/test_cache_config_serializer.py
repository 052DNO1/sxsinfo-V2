import pytest
from apps.cache_config.serializers.cache_config import (
    CacheConfigSerializer, CacheConfigCreateSerializer, CacheConfigUpdateSerializer,
    CacheClearSerializer, CacheConfigBatchUpdateSerializer
)


class TestCacheConfigCreateSerializer:
    def test_valid_data(self, db):
        data = {
            'api_path': '/api/v1/test/',
            'category': 'laboratories',
            'backend_ttl': 300,
            'enabled': True,
        }
        serializer = CacheConfigCreateSerializer(data=data)
        assert serializer.is_valid(), serializer.errors

    def test_missing_api_path(self, db):
        data = {'category': 'laboratories', 'backend_ttl': 300}
        serializer = CacheConfigCreateSerializer(data=data)
        assert not serializer.is_valid()
        assert 'api_path' in serializer.errors


class TestCacheConfigUpdateSerializer:
    def test_update_ttl(self, db):
        data = {'backend_ttl': 600}
        serializer = CacheConfigUpdateSerializer(data=data, partial=True)
        assert serializer.is_valid(), serializer.errors

    def test_update_enabled(self, db):
        data = {'enabled': False}
        serializer = CacheConfigUpdateSerializer(data=data, partial=True)
        assert serializer.is_valid(), serializer.errors


class TestCacheClearSerializer:
    def test_with_api_path(self, db):
        data = {'api_path': '/api/v1/test/', 'reason': '测试清除'}
        serializer = CacheClearSerializer(data=data)
        assert serializer.is_valid()

    def test_without_api_path(self, db):
        data = {'reason': '清除所有'}
        serializer = CacheClearSerializer(data=data)
        assert serializer.is_valid()

    def test_empty_data(self, db):
        data = {}
        serializer = CacheClearSerializer(data=data)
        assert serializer.is_valid()


class TestCacheConfigBatchUpdateSerializer:
    def test_valid_data(self, db):
        data = {
            'configs': [{'id': 1, 'enabled': True}],
            'reason': '批量更新',
        }
        serializer = CacheConfigBatchUpdateSerializer(data=data)
        assert serializer.is_valid()

    def test_missing_configs(self, db):
        data = {'reason': '测试'}
        serializer = CacheConfigBatchUpdateSerializer(data=data)
        assert not serializer.is_valid()
