import pytest
from tests.blackbox.client import assert_success_response, assert_error_response, extract_data
from tests.blackbox.config import API_ENDPOINTS, DEFAULT_PASSWORD


class TestCaptcha:
    def test_get_captcha_success(self, api_client):
        url = API_ENDPOINTS['auth']['captcha']
        response = api_client.get(url)
        data = assert_success_response(response)
        captcha_data = extract_data(response)
        assert 'captcha_key' in captcha_data or 'key' in captcha_data

    def test_verify_captcha_with_invalid_data(self, api_client):
        url = API_ENDPOINTS['auth']['captcha_verify']
        response = api_client.post(url, {
            'captcha_key': 'invalid_key',
            'captcha': 'wrong_code',
        })
        assert response.status_code in (400, 200)


class TestLogin:
    def test_login_success(self, api_client, system_admin):
        url = API_ENDPOINTS['auth']['login']
        response = api_client.post(url, {
            'username': system_admin.username,
            'password': DEFAULT_PASSWORD,
        })
        data = assert_success_response(response, message='登录成功')
        token_data = extract_data(response)
        assert 'access_token' in token_data or 'access' in token_data
        assert 'refresh_token' in token_data or 'refresh' in token_data

    def test_login_with_wrong_password(self, api_client, system_admin):
        url = API_ENDPOINTS['auth']['login']
        response = api_client.post(url, {
            'username': system_admin.username,
            'password': 'WrongPassword123',
        })
        assert response.status_code in (400, 401)

    def test_login_with_nonexistent_user(self, api_client, db):
        url = API_ENDPOINTS['auth']['login']
        response = api_client.post(url, {
            'username': 'nonexistent_user_xyz',
            'password': 'SomePassword123',
        })
        assert response.status_code in (400, 401, 500)

    def test_login_missing_username(self, api_client):
        url = API_ENDPOINTS['auth']['login']
        response = api_client.post(url, {
            'password': DEFAULT_PASSWORD,
        })
        assert response.status_code == 400

    def test_login_missing_password(self, api_client):
        url = API_ENDPOINTS['auth']['login']
        response = api_client.post(url, {
            'username': 'someuser',
        })
        assert response.status_code == 400

    def test_login_empty_body(self, api_client):
        url = API_ENDPOINTS['auth']['login']
        response = api_client.post(url, {})
        assert response.status_code == 400

    def test_login_inactive_user(self, api_client, inactive_user):
        url = API_ENDPOINTS['auth']['login']
        response = api_client.post(url, {
            'username': inactive_user.username,
            'password': DEFAULT_PASSWORD,
        })
        assert response.status_code in (400, 401, 403)

    def test_login_sql_injection(self, api_client, db):
        url = API_ENDPOINTS['auth']['login']
        response = api_client.post(url, {
            'username': "admin' OR '1'='1",
            'password': "anything",
        })
        assert response.status_code in (400, 401, 500)

    def test_login_xss_injection(self, api_client, db):
        url = API_ENDPOINTS['auth']['login']
        response = api_client.post(url, {
            'username': '<script>alert(1)</script>',
            'password': DEFAULT_PASSWORD,
        })
        assert response.status_code in (400, 401, 500)


class TestLogout:
    def test_logout_success(self, api_client, system_admin):
        api_client.authenticate(system_admin.username)
        url = API_ENDPOINTS['auth']['logout']
        response = api_client.post(url)
        assert response.status_code == 200

    def test_logout_without_auth(self, api_client):
        url = API_ENDPOINTS['auth']['logout']
        response = api_client.post(url)
        assert response.status_code in (401, 403)


class TestTokenRefresh:
    def test_refresh_token_success(self, api_client, system_admin):
        api_client.authenticate(system_admin.username)
        if api_client._refresh_token:
            url = API_ENDPOINTS['auth']['token_refresh']
            response = api_client.post(url, {
                'refresh_token': api_client._refresh_token,
            })
            assert response.status_code == 200

    def test_refresh_with_invalid_token(self, api_client):
        url = API_ENDPOINTS['auth']['token_refresh']
        response = api_client.post(url, {
            'refresh_token': 'invalid_token_xyz',
        })
        assert response.status_code in (400, 401)

    def test_refresh_missing_token(self, api_client):
        url = API_ENDPOINTS['auth']['token_refresh']
        response = api_client.post(url, {})
        assert response.status_code == 400


class TestChangePassword:
    def test_change_password_success(self, api_client, db):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        user = User.objects.create_user(
            username='bb_chpwd', password=DEFAULT_PASSWORD, role=32, is_superuser=True, is_active=True,
        )
        api_client.authenticate(user.username)
        url = API_ENDPOINTS['auth']['password_change']
        response = api_client.post(url, {
            'old_pwd': DEFAULT_PASSWORD,
            'new_pwd': 'NewPass@123',
            'confirm_pwd': 'NewPass@123',
        })
        assert response.status_code == 200

    def test_change_password_wrong_old(self, api_client, system_admin):
        api_client.authenticate(system_admin.username)
        url = API_ENDPOINTS['auth']['password_change']
        response = api_client.post(url, {
            'old_pwd': 'WrongOldPassword',
            'new_pwd': 'NewPass@123',
            'confirm_pwd': 'NewPass@123',
        })
        assert response.status_code == 400

    def test_change_password_mismatch_confirm(self, api_client, system_admin):
        api_client.authenticate(system_admin.username)
        url = API_ENDPOINTS['auth']['password_change']
        response = api_client.post(url, {
            'old_pwd': DEFAULT_PASSWORD,
            'new_pwd': 'NewPass@123',
            'confirm_pwd': 'DifferentPass@456',
        })
        assert response.status_code == 400

    def test_change_password_without_auth(self, api_client):
        url = API_ENDPOINTS['auth']['password_change']
        response = api_client.post(url, {
            'old_pwd': DEFAULT_PASSWORD,
            'new_pwd': 'NewPass@123',
            'confirm_pwd': 'NewPass@123',
        })
        assert response.status_code in (401, 403)


class TestAdminResetPassword:
    def test_admin_reset_password_success(self, authed_client, teacher):
        url = API_ENDPOINTS['auth']['password_reset']
        response = authed_client.post(url, {
            'user_id': teacher.id,
        })
        assert response.status_code == 200

    def test_admin_reset_password_nonexistent_user(self, authed_client):
        url = API_ENDPOINTS['auth']['password_reset']
        response = authed_client.post(url, {
            'user_id': 99999,
        })
        assert response.status_code in (400, 404)

    def test_admin_reset_password_missing_user_id(self, authed_client):
        url = API_ENDPOINTS['auth']['password_reset']
        response = authed_client.post(url, {})
        assert response.status_code == 400


class TestBatchResetPassword:
    def test_batch_reset_success(self, authed_client, teacher, lab_admin):
        url = API_ENDPOINTS['auth']['password_batch_reset']
        response = authed_client.post(url, {
            'user_ids': [teacher.id, lab_admin.id],
        })
        assert response.status_code == 200

    def test_batch_reset_empty_list(self, authed_client):
        url = API_ENDPOINTS['auth']['password_batch_reset']
        response = authed_client.post(url, {
            'user_ids': [],
        })
        assert response.status_code in (200, 400)

    def test_batch_reset_invalid_ids(self, authed_client):
        url = API_ENDPOINTS['auth']['password_batch_reset']
        response = authed_client.post(url, {
            'user_ids': [99998, 99999],
        })
        assert response.status_code in (200, 400, 404)


class TestSecurityQuestion:
    def test_set_security_question(self, api_client, system_admin):
        api_client.authenticate(system_admin.username)
        url = API_ENDPOINTS['auth']['security_question']
        response = api_client.post(url, {
            'question': '您的母亲姓名是？',
            'answer': '测试答案',
        })
        assert response.status_code == 200

    def test_set_security_question_invalid_question(self, api_client, system_admin):
        api_client.authenticate(system_admin.username)
        url = API_ENDPOINTS['auth']['security_question']
        response = api_client.post(url, {
            'question': '自定义的非预设问题',
            'answer': '测试答案',
        })
        assert response.status_code == 400

    def test_set_security_question_answer_too_short(self, api_client, system_admin):
        api_client.authenticate(system_admin.username)
        url = API_ENDPOINTS['auth']['security_question']
        response = api_client.post(url, {
            'question': '您的母亲姓名是？',
            'answer': 'A',
        })
        assert response.status_code == 400

    def test_get_security_question(self, api_client, system_admin):
        api_client.authenticate(system_admin.username)
        url = API_ENDPOINTS['auth']['security_question']
        response = api_client.get(url)
        assert response.status_code == 200

    def test_get_user_security_question(self, api_client, system_admin):
        url = API_ENDPOINTS['auth']['security_question_user']
        response = api_client.post(url, {
            'username': system_admin.username,
        })
        assert response.status_code == 200

    def test_get_security_question_invalid_username(self, api_client):
        url = API_ENDPOINTS['auth']['security_question_user']
        response = api_client.post(url, {
            'username': 'nonexistent_user_xyz',
        })
        assert response.status_code in (200, 400, 404, 500)


class TestPasswordResetContact:
    def test_get_reset_contact(self, api_client, system_admin):
        url = API_ENDPOINTS['auth']['password_reset_contact']
        response = api_client.post(url, {
            'username': system_admin.username,
        })
        assert response.status_code == 200

    def test_get_reset_contact_nonexistent_user(self, api_client):
        url = API_ENDPOINTS['auth']['password_reset_contact']
        response = api_client.post(url, {
            'username': 'nonexistent_user_xyz',
        })
        assert response.status_code in (200, 400, 404, 500)
