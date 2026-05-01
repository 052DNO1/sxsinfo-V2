import pytest
from apps.users.serializers.auth import (
    LoginSerializer, ChangePasswordSerializer,
    CaptchaVerifySerializer, SecurityQuestionSetSerializer,
    ResetPasswordBySecuritySerializer, AdminResetPasswordSerializer,
    BatchResetPasswordSerializer
)


class TestLoginSerializer:
    def test_valid_data(self):
        data = {'username': 'testuser', 'password': 'test123'}
        serializer = LoginSerializer(data=data)
        assert serializer.is_valid()

    def test_missing_username(self):
        data = {'password': 'test123'}
        serializer = LoginSerializer(data=data)
        assert not serializer.is_valid()
        assert 'username' in serializer.errors

    def test_missing_password(self):
        data = {'username': 'testuser'}
        serializer = LoginSerializer(data=data)
        assert not serializer.is_valid()
        assert 'password' in serializer.errors

    def test_invalid_username_format(self):
        data = {'username': 'user name', 'password': 'test123'}
        serializer = LoginSerializer(data=data)
        assert not serializer.is_valid()

    def test_username_with_special_chars(self):
        data = {'username': 'user_name', 'password': 'test123'}
        serializer = LoginSerializer(data=data)
        assert serializer.is_valid()

    def test_optional_captcha(self):
        data = {'username': 'testuser', 'password': 'test123'}
        serializer = LoginSerializer(data=data)
        assert serializer.is_valid()

    def test_with_captcha(self):
        data = {'username': 'testuser', 'password': 'test123', 'captcha_key': 'key', 'captcha': '1234'}
        serializer = LoginSerializer(data=data)
        assert serializer.is_valid()


class TestChangePasswordSerializer:
    def test_valid_data(self):
        data = {'old_pwd': 'Old@123', 'new_pwd': 'New@123', 'confirm_pwd': 'New@123'}
        serializer = ChangePasswordSerializer(data=data)
        assert serializer.is_valid()

    def test_password_mismatch(self):
        data = {'old_pwd': 'Old@123', 'new_pwd': 'New@123', 'confirm_pwd': 'Different@123'}
        serializer = ChangePasswordSerializer(data=data)
        assert not serializer.is_valid()

    def test_missing_fields(self):
        data = {'old_pwd': 'Old@123'}
        serializer = ChangePasswordSerializer(data=data)
        assert not serializer.is_valid()


class TestCaptchaVerifySerializer:
    def test_valid_data(self):
        data = {'captcha_key': 'test_key', 'captcha': '1234'}
        serializer = CaptchaVerifySerializer(data=data)
        assert serializer.is_valid()

    def test_missing_captcha_key(self):
        data = {'captcha': '1234'}
        serializer = CaptchaVerifySerializer(data=data)
        assert not serializer.is_valid()


class TestSecurityQuestionSetSerializer:
    def test_valid_data(self):
        data = {'question': '您的母亲姓名是？', 'answer': '张三'}
        serializer = SecurityQuestionSetSerializer(data=data)
        assert serializer.is_valid()

    def test_answer_too_short(self):
        data = {'question': '问题', 'answer': 'a'}
        serializer = SecurityQuestionSetSerializer(data=data)
        assert not serializer.is_valid()

    def test_answer_too_long(self):
        data = {'question': '问题', 'answer': 'a' * 51}
        serializer = SecurityQuestionSetSerializer(data=data)
        assert not serializer.is_valid()


class TestResetPasswordBySecuritySerializer:
    def test_valid_data(self):
        data = {'reset_token': 'token123', 'new_password': 'New@123', 'confirm_password': 'New@123'}
        serializer = ResetPasswordBySecuritySerializer(data=data)
        assert serializer.is_valid()

    def test_password_mismatch(self):
        data = {'reset_token': 'token123', 'new_password': 'New@123', 'confirm_password': 'Different@123'}
        serializer = ResetPasswordBySecuritySerializer(data=data)
        assert not serializer.is_valid()


class TestAdminResetPasswordSerializer:
    def test_valid_data(self):
        data = {'user_id': 1}
        serializer = AdminResetPasswordSerializer(data=data)
        assert serializer.is_valid()

    def test_missing_user_id(self):
        data = {}
        serializer = AdminResetPasswordSerializer(data=data)
        assert not serializer.is_valid()


class TestBatchResetPasswordSerializer:
    def test_valid_data(self):
        data = {'user_ids': [1, 2, 3]}
        serializer = BatchResetPasswordSerializer(data=data)
        assert serializer.is_valid()

    def test_missing_user_ids(self):
        data = {}
        serializer = BatchResetPasswordSerializer(data=data)
        assert not serializer.is_valid()
