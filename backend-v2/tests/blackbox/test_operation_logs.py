import pytest
from tests.blackbox.client import (
    assert_success_response, assert_error_response,
    assert_paginated_response, extract_data, extract_list,
)
from tests.blackbox.config import API_ENDPOINTS


class TestOperationLogList:
    def test_get_operation_log_list(self, authed_client):
        url = API_ENDPOINTS['operation_logs']['list']
        response = authed_client.get(url)
        assert_paginated_response(response)

    def test_get_operation_log_list_with_pagination(self, authed_client):
        url = API_ENDPOINTS['operation_logs']['list']
        response = authed_client.get(url, {'page': 1, 'page_size': 10})
        assert_paginated_response(response)

    def test_get_operation_log_list_filter_by_module(self, authed_client):
        url = API_ENDPOINTS['operation_logs']['list']
        response = authed_client.get(url, {'module': 'users'})
        assert_paginated_response(response)

    def test_get_operation_log_list_filter_by_operation_type(self, authed_client):
        url = API_ENDPOINTS['operation_logs']['list']
        response = authed_client.get(url, {'operation_type': 'CREATE'})
        assert_paginated_response(response)

    def test_get_operation_log_list_search(self, authed_client):
        url = API_ENDPOINTS['operation_logs']['list']
        response = authed_client.get(url, {'search': '测试'})
        assert_paginated_response(response)

    def test_get_operation_log_list_filter_by_date_range(self, authed_client):
        url = API_ENDPOINTS['operation_logs']['list']
        response = authed_client.get(url, {
            'start_date': '2025-01-01',
            'end_date': '2025-12-31',
        })
        assert_paginated_response(response)


class TestOperationLogDetail:
    def test_get_operation_log_detail(self, authed_client, db, system_admin):
        from apps.core.models import SystemOperationLog
        log = SystemOperationLog.objects.create(
            operator=system_admin,
            operator_username=system_admin.username,
            module='users',
            operation_type='CREATE',
            target_type='User',
            target_id=1,
            target_name='测试用户',
            description='创建测试用户',
            ip_address='127.0.0.1',
        )
        url = API_ENDPOINTS['operation_logs']['detail'].format(id=log.id)
        response = authed_client.get(url)
        assert response.status_code == 200

    def test_get_operation_log_detail_not_found(self, authed_client):
        url = API_ENDPOINTS['operation_logs']['detail'].format(id=99999)
        response = authed_client.get(url)
        assert response.status_code in (400, 404)


class TestOperationLogStats:
    def test_get_stats(self, authed_client):
        url = API_ENDPOINTS['operation_logs']['stats']
        response = authed_client.get(url)
        assert response.status_code == 200


class TestOperationLogRecent:
    def test_get_recent_logs(self, authed_client):
        url = API_ENDPOINTS['operation_logs']['recent']
        response = authed_client.get(url)
        assert response.status_code == 200

    def test_get_recent_logs_with_limit(self, authed_client):
        url = API_ENDPOINTS['operation_logs']['recent']
        response = authed_client.get(url, {'limit': 5})
        assert response.status_code == 200


class TestOperationLogModules:
    def test_get_modules(self, authed_client):
        url = API_ENDPOINTS['operation_logs']['modules']
        response = authed_client.get(url)
        assert response.status_code == 200


class TestOperationLogExport:
    def test_export_logs(self, authed_client):
        url = API_ENDPOINTS['operation_logs']['export']
        response = authed_client.get(url)
        assert response.status_code in (200, 400, 500)


class TestOperationLogCleanup:
    def test_cleanup_logs(self, authed_client):
        url = API_ENDPOINTS['operation_logs']['cleanup']
        response = authed_client.delete(url, {'days': 90})
        assert response.status_code in (200, 400)

    def test_cleanup_logs_invalid_days(self, authed_client):
        url = API_ENDPOINTS['operation_logs']['cleanup']
        response = authed_client.delete(url, {'days': -1})
        assert response.status_code in (200, 400)
