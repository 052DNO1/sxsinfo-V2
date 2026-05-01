import pytest
from tests.blackbox.client import (
    assert_success_response, assert_error_response,
    extract_data,
)
from tests.blackbox.config import API_ENDPOINTS, DEFAULT_PASSWORD


class TestAuthenticationSecurity:
    def test_login_sql_injection(self, api_client):
        url = API_ENDPOINTS['auth']['login']
        payloads = [
            {"username": "admin' OR '1'='1", "password": "anything"},
            {"username": "admin'; DROP TABLE users;--", "password": "x"},
            {"username": "1' OR '1' = '1", "password": "x"},
        ]
        for payload in payloads:
            response = api_client.post(url, payload)
            assert response.status_code == 400, \
                f"SQL injection should be rejected: {payload}"

    def test_login_xss_injection(self, api_client):
        url = API_ENDPOINTS['auth']['login']
        payloads = [
            {"username": "<script>alert('xss')</script>", "password": "x"},
            {"username": "<img src=x onerror=alert(1)>", "password": "x"},
        ]
        for payload in payloads:
            response = api_client.post(url, payload)
            assert response.status_code == 400

    def test_expired_token_rejected(self, api_client):
        api_client.authenticate_with_token('eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.invalid.signature')
        url = API_ENDPOINTS['users']['profile']
        response = api_client.get(url)
        assert response.status_code in (401, 403)

    def test_malformed_token_rejected(self, api_client):
        api_client.authenticate_with_token('not-a-valid-jwt-token')
        url = API_ENDPOINTS['users']['profile']
        response = api_client.get(url)
        assert response.status_code in (401, 403)

    def test_empty_token_rejected(self, api_client):
        api_client.authenticate_with_token('')
        url = API_ENDPOINTS['users']['profile']
        response = api_client.get(url)
        assert response.status_code in (401, 403)


class TestAuthorizationSecurity:
    def test_unauthenticated_access_all_endpoints(self, api_client):
        protected_endpoints = [
            API_ENDPOINTS['users']['list'],
            API_ENDPOINTS['departments']['list'],
            API_ENDPOINTS['laboratories']['list'],
            API_ENDPOINTS['equipments']['list'],
            API_ENDPOINTS['schedules']['list'],
            API_ENDPOINTS['semesters']['list'],
            API_ENDPOINTS['records']['list'],
            API_ENDPOINTS['work_orders']['list'],
            API_ENDPOINTS['notifications']['list'],
            API_ENDPOINTS['statistics']['dashboard'],
            API_ENDPOINTS['backups']['stats'],
            API_ENDPOINTS['cache_config']['configs'],
            API_ENDPOINTS['operation_logs']['list'],
        ]
        for endpoint in protected_endpoints:
            response = api_client.get(endpoint)
            assert response.status_code in (401, 403), \
                f"Unauthenticated access should be rejected: {endpoint}"

    def test_teacher_cannot_create_department(self, authed_teacher):
        url = API_ENDPOINTS['departments']['list']
        response = authed_teacher.post(url, {
            'name': '教师创建分院',
            'code': 'TEACHER_DEPT',
        })
        assert response.status_code in (200, 201, 403)

    def test_teacher_cannot_delete_user(self, authed_teacher, system_admin):
        url = API_ENDPOINTS['users']['detail'].format(id=system_admin.id)
        response = authed_teacher.delete(url)
        assert response.status_code in (200, 403)

    def test_teacher_cannot_reset_password(self, authed_teacher, system_admin):
        url = API_ENDPOINTS['auth']['password_reset']
        response = authed_teacher.post(url, {
            'user_id': system_admin.id,
        })
        assert response.status_code in (200, 401, 403, 400)


class TestInputValidation:
    def test_create_user_with_very_long_username(self, authed_client, test_department):
        url = API_ENDPOINTS['users']['list']
        response = authed_client.post(url, {
            'username': 'a' * 500,
            'password': DEFAULT_PASSWORD,
            'nickname': '超长用户名',
            'role': 1,
            'department': test_department.id,
        })
        assert response.status_code == 400

    def test_create_laboratory_with_negative_capacity(self, authed_client, test_department):
        url = API_ENDPOINTS['laboratories']['list']
        response = authed_client.post(url, {
            'name': '负容量实训室',
            'code': 'BB_NEG_CAP',
            'building': '测试楼',
            'capacity': -10,
            'department': test_department.id,
        })
        assert response.status_code in (400, 500)

    def test_create_schedule_with_invalid_weekday(self, authed_client, test_laboratory, test_semester, teacher):
        url = API_ENDPOINTS['schedules']['list']
        for weekday in [0, 8, -1, 100]:
            response = authed_client.post(url, {
                'course_name': f'无效星期{weekday}',
                'weekday': weekday,
                'time_slot': '1-2',
                'laboratory_id': test_laboratory.id,
                'semester_id': test_semester.id,
                'teacher_id': teacher.id,
            })
            assert response.status_code in (400, 500), \
                f"Invalid weekday {weekday} should be rejected"


class TestDataIntegrity:
    def test_cannot_create_duplicate_code(self, authed_client, test_laboratory, test_department):
        url = API_ENDPOINTS['laboratories']['list']
        response = authed_client.post(url, {
            'name': '重复编码实训室',
            'code': test_laboratory.code,
            'department': test_department.id,
        })
        assert response.status_code == 400

    def test_cannot_create_duplicate_department_code(self, authed_client, test_department):
        url = API_ENDPOINTS['departments']['list']
        response = authed_client.post(url, {
            'name': '重复编码分院',
            'code': test_department.code,
        })
        assert response.status_code == 400


class TestResponseFormat:
    def test_success_response_format(self, authed_client, test_department):
        url = API_ENDPOINTS['departments']['detail'].format(id=test_department.id)
        response = authed_client.get(url)
        data = response.json()
        assert 'success' in data
        assert 'code' in data
        assert 'message' in data
        assert 'data' in data
        assert data['success'] is True

    def test_error_response_format(self, api_client):
        url = API_ENDPOINTS['users']['list']
        response = api_client.get(url)
        data = response.json()
        assert 'success' in data
        assert data['success'] is False

    def test_paginated_response_format(self, authed_client):
        url = API_ENDPOINTS['users']['list']
        response = authed_client.get(url, {'page': 1, 'page_size': 5})
        data = response.json()
        inner = data.get('data', data)
        if 'pagination' in inner:
            pagination = inner['pagination']
            assert 'total' in pagination
            assert 'page' in pagination
            assert 'page_size' in pagination
            assert isinstance(inner.get('list', []), list)
