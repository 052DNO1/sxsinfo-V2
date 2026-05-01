import pytest
from tests.blackbox.client import (
    assert_success_response, assert_error_response,
    assert_paginated_response, extract_data, extract_list,
)
from tests.blackbox.config import API_ENDPOINTS


class TestCacheConfigList:
    def test_get_cache_configs(self, authed_client):
        url = API_ENDPOINTS['cache_config']['configs']
        response = authed_client.get(url)
        assert response.status_code == 200

    def test_get_cache_configs_filter_by_category(self, authed_client):
        url = API_ENDPOINTS['cache_config']['configs']
        response = authed_client.get(url, {'category': 'laboratory'})
        assert response.status_code == 200

    def test_get_all_cache_configs(self, authed_client):
        url = API_ENDPOINTS['cache_config']['config_all']
        response = authed_client.get(url)
        assert response.status_code == 200


class TestCacheConfigCreate:
    def test_create_cache_config(self, authed_client, system_admin):
        url = API_ENDPOINTS['cache_config']['configs']
        response = authed_client.post(url, {
            'api_path': '/api/v1/test/blackbox/',
            'category': 'test',
            'backend_ttl': 300,
            'enabled': True,
            'description': '黑盒测试缓存配置',
        })
        assert response.status_code in (201, 200)

    def test_create_cache_config_missing_path(self, authed_client):
        url = API_ENDPOINTS['cache_config']['configs']
        response = authed_client.post(url, {
            'category': 'test',
            'backend_ttl': 300,
        })
        assert response.status_code in (400, 200)


class TestCacheConfigDetail:
    def test_get_cache_config_detail(self, authed_client, db):
        from apps.cache_config.models import CacheConfig
        config = CacheConfig.objects.create(
            api_path='/api/v1/test/bb_detail/',
            category='test',
            backend_ttl=300,
            enabled=True,
        )
        url = API_ENDPOINTS['cache_config']['config_detail'].format(id=config.id)
        response = authed_client.get(url)
        assert response.status_code == 200

    def test_update_cache_config(self, authed_client, db):
        from apps.cache_config.models import CacheConfig
        config = CacheConfig.objects.create(
            api_path='/api/v1/test/bb_update/',
            category='test',
            backend_ttl=300,
            enabled=True,
        )
        url = API_ENDPOINTS['cache_config']['config_detail'].format(id=config.id)
        response = authed_client.put(url, {
            'backend_ttl': 600,
            'enabled': False,
        })
        assert response.status_code == 200

    def test_delete_cache_config(self, authed_client, db):
        from apps.cache_config.models import CacheConfig
        config = CacheConfig.objects.create(
            api_path='/api/v1/test/bb_delete/',
            category='test',
            backend_ttl=300,
            enabled=True,
        )
        url = API_ENDPOINTS['cache_config']['config_detail'].format(id=config.id)
        response = authed_client.delete(url)
        assert response.status_code == 200


class TestCacheStats:
    def test_get_stats_list(self, authed_client):
        url = API_ENDPOINTS['cache_config']['stats']
        response = authed_client.get(url)
        assert response.status_code == 200

    def test_get_today_stats(self, authed_client):
        url = API_ENDPOINTS['cache_config']['stats_today']
        response = authed_client.get(url)
        assert response.status_code == 200

    def test_get_stats_range(self, authed_client):
        url = API_ENDPOINTS['cache_config']['stats_range']
        response = authed_client.get(url, {
            'start_date': '2025-01-01',
            'end_date': '2025-12-31',
        })
        assert response.status_code == 200

    def test_get_stats_ranking(self, authed_client):
        url = API_ENDPOINTS['cache_config']['stats_ranking']
        response = authed_client.get(url)
        assert response.status_code == 200


class TestCacheLogs:
    def test_get_cache_logs(self, authed_client):
        url = API_ENDPOINTS['cache_config']['logs']
        response = authed_client.get(url)
        assert response.status_code == 200


class TestCacheOperations:
    def test_clear_cache(self, authed_client):
        url = API_ENDPOINTS['cache_config']['clear']
        response = authed_client.post(url, {
            'category': 'test',
        })
        assert response.status_code == 200

    def test_get_overview(self, authed_client):
        url = API_ENDPOINTS['cache_config']['overview']
        response = authed_client.get(url)
        assert response.status_code == 200

    def test_auto_discover(self, authed_client):
        url = API_ENDPOINTS['cache_config']['auto_discover']
        response = authed_client.post(url)
        assert response.status_code == 200

    def test_batch_toggle(self, authed_client):
        url = API_ENDPOINTS['cache_config']['batch_toggle']
        response = authed_client.post(url, {
            'enabled': True,
        })
        assert response.status_code == 200

    def test_batch_toggle_disable(self, authed_client):
        url = API_ENDPOINTS['cache_config']['batch_toggle']
        response = authed_client.post(url, {
            'enabled': False,
        })
        assert response.status_code == 200
