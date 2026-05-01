import pytest
from tests.blackbox.client import (
    assert_success_response, assert_error_response,
    assert_paginated_response, extract_data, extract_list,
)
from tests.blackbox.config import API_ENDPOINTS


class TestGlobalSearch:
    def test_search_with_keyword(self, authed_client):
        url = API_ENDPOINTS['common']['search']
        response = authed_client.get(url, {'keyword': '测试'})
        assert response.status_code == 200

    def test_search_with_limit(self, authed_client):
        url = API_ENDPOINTS['common']['search']
        response = authed_client.get(url, {'keyword': '测试', 'limit': 5})
        assert response.status_code == 200

    def test_search_empty_keyword(self, authed_client):
        url = API_ENDPOINTS['common']['search']
        response = authed_client.get(url, {'keyword': ''})
        assert response.status_code in (200, 400)

    def test_search_missing_keyword(self, authed_client):
        url = API_ENDPOINTS['common']['search']
        response = authed_client.get(url)
        assert response.status_code in (200, 400)


class TestHealthCheck:
    def test_health_check(self, api_client):
        url = API_ENDPOINTS['common']['health']
        response = api_client.get(url)
        assert response.status_code in (200, 400)

    def test_health_check_no_auth_required(self, api_client):
        url = API_ENDPOINTS['common']['health']
        response = api_client.get(url)
        assert response.status_code in (200, 400)


class TestProgress:
    def test_get_progress(self, authed_client):
        url = API_ENDPOINTS['common']['progress']
        response = authed_client.get(url, {'type': 'import'})
        assert response.status_code == 200


class TestExportEndpoints:
    def test_export_laboratories(self, authed_client):
        url = API_ENDPOINTS['common']['export_laboratories']
        response = authed_client.get(url)
        assert response.status_code in (200, 202)

    def test_export_schedules(self, authed_client):
        url = API_ENDPOINTS['common']['export_schedules']
        response = authed_client.get(url)
        assert response.status_code in (200, 202)

    def test_export_records(self, authed_client):
        url = API_ENDPOINTS['common']['export_records']
        response = authed_client.get(url)
        assert response.status_code in (200, 202)

    def test_export_work_orders(self, authed_client):
        url = API_ENDPOINTS['common']['export_work_orders']
        response = authed_client.get(url)
        assert response.status_code in (200, 202)

    def test_export_equipment(self, authed_client):
        url = API_ENDPOINTS['common']['export_equipment']
        response = authed_client.get(url)
        assert response.status_code in (200, 202)

    def test_export_users(self, authed_client):
        url = API_ENDPOINTS['common']['export_users']
        response = authed_client.get(url)
        assert response.status_code in (200, 202)

    def test_export_statistics(self, authed_client):
        url = API_ENDPOINTS['common']['export_statistics']
        response = authed_client.get(url)
        assert response.status_code in (200, 202, 400)

    def test_export_with_filters(self, authed_client, test_department):
        url = API_ENDPOINTS['common']['export_laboratories']
        response = authed_client.get(url, {
            'department_id': test_department.id,
            'status': 1,
        })
        assert response.status_code in (200, 202)

    def test_export_unauthenticated(self, api_client):
        url = API_ENDPOINTS['common']['export_laboratories']
        response = api_client.get(url)
        assert response.status_code in (401, 403)


class TestImportEndpoints:
    def test_import_laboratories_no_file(self, authed_client):
        url = API_ENDPOINTS['common']['import_laboratories']
        response = authed_client.post(url)
        assert response.status_code in (400, 200)

    def test_import_schedules_no_file(self, authed_client):
        url = API_ENDPOINTS['common']['import_schedules']
        response = authed_client.post(url)
        assert response.status_code in (400, 200)

    def test_import_equipment_no_file(self, authed_client):
        url = API_ENDPOINTS['common']['import_equipment']
        response = authed_client.post(url)
        assert response.status_code in (400, 200)

    def test_import_unauthenticated(self, api_client):
        url = API_ENDPOINTS['common']['import_laboratories']
        response = api_client.post(url)
        assert response.status_code in (401, 403)
