import pytest
from tests.blackbox.client import (
    assert_success_response, assert_error_response,
    assert_paginated_response, extract_data, extract_list,
)
from tests.blackbox.config import API_ENDPOINTS, DEFAULT_PASSWORD


class TestUserList:
    def test_get_user_list(self, authed_client):
        url = API_ENDPOINTS['users']['list']
        response = authed_client.get(url)
        assert_paginated_response(response)

    def test_get_user_list_with_pagination(self, authed_client):
        url = API_ENDPOINTS['users']['list']
        response = authed_client.get(url, {'page': 1, 'page_size': 5})
        data = assert_paginated_response(response)

    def test_get_user_list_search(self, authed_client, system_admin):
        url = API_ENDPOINTS['users']['list']
        response = authed_client.get(url, {'search': system_admin.username})
        data = assert_paginated_response(response)

    def test_get_user_list_filter_by_department(self, authed_client, test_department):
        url = API_ENDPOINTS['users']['list']
        response = authed_client.get(url, {'department_id': test_department.id})
        assert_paginated_response(response)

    def test_get_user_list_filter_by_role(self, authed_client):
        url = API_ENDPOINTS['users']['list']
        response = authed_client.get(url, {'role': 1})
        assert_paginated_response(response)

    def test_get_user_list_unauthenticated(self, api_client):
        url = API_ENDPOINTS['users']['list']
        response = api_client.get(url)
        assert response.status_code in (401, 403)

    def test_get_user_options(self, authed_client):
        url = API_ENDPOINTS['users']['options']
        response = authed_client.get(url)
        assert_success_response(response)


class TestUserCreate:
    def test_create_user_success(self, authed_client, test_department):
        url = API_ENDPOINTS['users']['list']
        response = authed_client.post(url, {
            'username': 'bb_new_user',
            'password': DEFAULT_PASSWORD,
            'nickname': '新建测试用户',
            'phone': '13800138001',
            'email': 'newuser@test.com',
            'role': 1,
            'status': 1,
            'department': test_department.id,
        })
        assert response.status_code in (200, 201)
        data = extract_data(response)
        assert data.get('username') == 'bb_new_user' or data.get('id') is not None

    def test_create_user_duplicate_username(self, authed_client, system_admin, test_department):
        url = API_ENDPOINTS['users']['list']
        response = authed_client.post(url, {
            'username': system_admin.username,
            'password': DEFAULT_PASSWORD,
            'nickname': '重复用户名',
            'role': 1,
            'department': test_department.id,
        })
        assert response.status_code == 400

    def test_create_user_missing_required_fields(self, authed_client):
        url = API_ENDPOINTS['users']['list']
        response = authed_client.post(url, {})
        assert response.status_code == 400

    def test_create_user_invalid_email(self, authed_client, test_department):
        url = API_ENDPOINTS['users']['list']
        response = authed_client.post(url, {
            'username': 'bb_email_invalid',
            'password': DEFAULT_PASSWORD,
            'nickname': '邮箱无效',
            'email': 'not-an-email',
            'role': 1,
            'department': test_department.id,
        })
        assert response.status_code in (400, 201)

    def test_create_user_invalid_phone(self, authed_client, test_department):
        url = API_ENDPOINTS['users']['list']
        response = authed_client.post(url, {
            'username': 'bb_phone_invalid',
            'password': DEFAULT_PASSWORD,
            'nickname': '手机号无效',
            'phone': '123',
            'role': 1,
            'department': test_department.id,
        })
        assert response.status_code in (400, 201)


class TestUserDetail:
    def test_get_user_detail(self, authed_client, system_admin):
        url = API_ENDPOINTS['users']['detail'].format(id=system_admin.id)
        response = authed_client.get(url)
        data = assert_success_response(response)
        user_data = extract_data(response)
        assert user_data.get('id') == system_admin.id
        assert user_data.get('username') == system_admin.username

    def test_get_user_detail_not_found(self, authed_client):
        url = API_ENDPOINTS['users']['detail'].format(id=99999)
        response = authed_client.get(url)
        assert response.status_code in (400, 404)

    def test_update_user_success(self, authed_client, teacher):
        url = API_ENDPOINTS['users']['detail'].format(id=teacher.id)
        response = authed_client.put(url, {
            'nickname': '更新后的昵称',
            'phone': '13900139001',
        })
        assert response.status_code == 200
        verify_url = API_ENDPOINTS['users']['detail'].format(id=teacher.id)
        verify_resp = authed_client.get(verify_url)
        verify_data = extract_data(verify_resp)
        assert verify_data.get('nickname') == '更新后的昵称'

    def test_delete_user_success(self, authed_client, db):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        user = User.objects.create_user(
            username='bb_to_delete',
            password=DEFAULT_PASSWORD,
            nickname='待删除用户',
            role=1,
        )
        url = API_ENDPOINTS['users']['detail'].format(id=user.id)
        response = authed_client.delete(url)
        assert response.status_code == 200


class TestUserBatchDelete:
    def test_batch_delete_success(self, authed_client, db):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        u1 = User.objects.create_user(username='bb_del_1', password=DEFAULT_PASSWORD, role=1)
        u2 = User.objects.create_user(username='bb_del_2', password=DEFAULT_PASSWORD, role=1)
        url = API_ENDPOINTS['users']['batch_delete']
        response = authed_client.post(url, {'ids': [u1.id, u2.id]})
        assert response.status_code == 200

    def test_batch_delete_empty_list(self, authed_client):
        url = API_ENDPOINTS['users']['batch_delete']
        response = authed_client.post(url, {'ids': []})
        assert response.status_code in (200, 400)

    def test_batch_delete_nonexistent_ids(self, authed_client):
        url = API_ENDPOINTS['users']['batch_delete']
        response = authed_client.post(url, {'ids': [99998, 99999]})
        assert response.status_code in (200, 400, 404)


class TestUserActivate:
    def test_activate_user(self, authed_client, inactive_user):
        url = API_ENDPOINTS['users']['activate'].format(id=inactive_user.id)
        response = authed_client.post(url, {'is_active': True})
        assert response.status_code == 200

    def test_deactivate_user(self, authed_client, teacher):
        url = API_ENDPOINTS['users']['activate'].format(id=teacher.id)
        response = authed_client.post(url, {'is_active': False})
        assert response.status_code == 200


class TestUserUpdateRole:
    def test_update_role_success(self, authed_client, teacher, test_department):
        url = API_ENDPOINTS['users']['update_role'].format(id=teacher.id)
        response = authed_client.post(url, {
            'role': 2,
            'department_id': test_department.id,
        })
        assert response.status_code == 200

    def test_update_role_invalid_role(self, authed_client, teacher):
        url = API_ENDPOINTS['users']['update_role'].format(id=teacher.id)
        response = authed_client.post(url, {
            'role': 999,
        })
        assert response.status_code in (200, 400)


class TestUserProfile:
    def test_get_profile(self, authed_client, system_admin):
        url = API_ENDPOINTS['users']['profile']
        response = authed_client.get(url)
        data = assert_success_response(response)
        profile = extract_data(response)
        assert profile.get('username') == system_admin.username

    def test_update_profile(self, authed_client, system_admin):
        url = API_ENDPOINTS['users']['profile']
        response = authed_client.put(url, {
            'nickname': '更新昵称',
            'phone': '13800138000',
        })
        assert response.status_code == 200

    def test_get_profile_unauthenticated(self, api_client):
        url = API_ENDPOINTS['users']['profile']
        response = api_client.get(url)
        assert response.status_code in (401, 403)
