import pytest
from unittest.mock import patch, MagicMock
from django.core.cache import cache
from apps.users.services.auth_service import (
    AuthService, CAPTCHA_CACHE_PREFIX, LOGIN_FAILED_PREFIX,
    SECURITY_RESET_PREFIX, SECURITY_QUESTIONS
)
from apps.core.exceptions import ValidationError, AuthenticationError
from apps.core.constants import UserRole
from apps.users.models import User


@pytest.fixture(autouse=True)
def clear_cache():
    cache.clear()
    yield
    cache.clear()


class TestGenerateCaptcha:
    def test_returns_dict_with_keys(self):
        result = AuthService.generate_captcha()
        assert 'captcha_key' in result
        assert 'captcha_image' in result

    def test_captcha_image_is_base64(self):
        result = AuthService.generate_captcha()
        assert result['captcha_image'].startswith('data:image/png;base64,')

    def test_captcha_key_is_uuid(self):
        result = AuthService.generate_captcha()
        assert len(result['captcha_key']) == 36

    def test_captcha_stored_in_cache(self):
        result = AuthService.generate_captcha()
        cached = cache.get(CAPTCHA_CACHE_PREFIX + result['captcha_key'])
        assert cached is not None
        assert len(cached) == 4

    def test_captcha_is_lowercase(self):
        result = AuthService.generate_captcha()
        cached = cache.get(CAPTCHA_CACHE_PREFIX + result['captcha_key'])
        assert cached == cached.lower()


class TestVerifyCaptcha:
    def test_verify_correct_captcha(self):
        result = AuthService.generate_captcha()
        cached = cache.get(CAPTCHA_CACHE_PREFIX + result['captcha_key'])
        assert AuthService.verify_captcha(result['captcha_key'], cached) is True

    def test_verify_case_insensitive(self):
        result = AuthService.generate_captcha()
        cached = cache.get(CAPTCHA_CACHE_PREFIX + result['captcha_key'])
        assert AuthService.verify_captcha(result['captcha_key'], cached.upper()) is True

    def test_verify_wrong_captcha(self):
        result = AuthService.generate_captcha()
        with pytest.raises(ValidationError, match='验证码错误'):
            AuthService.verify_captcha(result['captcha_key'], 'wrong')

    def test_verify_expired_captcha(self):
        with pytest.raises(ValidationError, match='验证码已过期'):
            AuthService.verify_captcha('nonexistent_key', '1234')

    def test_verify_empty_key(self):
        with pytest.raises(ValidationError, match='验证码不能为空'):
            AuthService.verify_captcha('', '1234')

    def test_verify_empty_input(self):
        with pytest.raises(ValidationError, match='验证码不能为空'):
            AuthService.verify_captcha('some_key', '')

    def test_verify_one_time_use(self):
        result = AuthService.generate_captcha()
        cached = cache.get(CAPTCHA_CACHE_PREFIX + result['captcha_key'])
        AuthService.verify_captcha(result['captcha_key'], cached)
        with pytest.raises(ValidationError, match='验证码已过期'):
            AuthService.verify_captcha(result['captcha_key'], cached)


class TestLogin:
    def test_login_success(self, db, wb_teacher, wb_request_factory):
        request = wb_request_factory.post('/auth/login/')
        request.META['REMOTE_ADDR'] = '127.0.0.1'
        result = AuthService.login(
            username='wb_teacher',
            password='WbTest@123456',
            request=request,
        )
        assert 'access_token' in result
        assert 'refresh_token' in result
        assert 'user' in result
        assert result['user']['username'] == 'wb_teacher'

    def test_login_empty_username(self, db):
        with pytest.raises(ValidationError, match='请输入用户名和密码'):
            AuthService.login(username='', password='test')

    def test_login_empty_password(self, db):
        with pytest.raises(ValidationError, match='请输入用户名和密码'):
            AuthService.login(username='test', password='')

    def test_login_invalid_username_format(self, db):
        with pytest.raises(ValidationError, match='用户名格式不正确'):
            AuthService.login(username='user name', password='test')

    def test_login_username_with_special_chars(self, db):
        valid_usernames = ['user@test', 'user.name', 'user-name', 'user_name']
        for uname in valid_usernames:
            try:
                AuthService.login(username=uname, password='test')
            except (ValidationError, AuthenticationError):
                pass

    def test_login_wrong_password(self, db, wb_teacher, wb_request_factory):
        request = wb_request_factory.post('/auth/login/')
        request.META['REMOTE_ADDR'] = '127.0.0.2'
        with pytest.raises(AuthenticationError, match='用户名或密码错误'):
            AuthService.login(
                username='wb_teacher',
                password='wrongpassword',
                request=request,
            )

    def test_login_inactive_user(self, db, wb_inactive_user, wb_request_factory):
        request = wb_request_factory.post('/auth/login/')
        request.META['REMOTE_ADDR'] = '127.0.0.3'
        with pytest.raises(AuthenticationError):
            AuthService.login(
                username='wb_inactive',
                password='WbTest@123456',
                request=request,
            )

    def test_login_rate_limiting(self, db, wb_teacher, wb_request_factory):
        request = wb_request_factory.post('/auth/login/')
        request.META['REMOTE_ADDR'] = '127.0.0.4'
        for _ in range(5):
            try:
                AuthService.login(
                    username='wb_teacher',
                    password='wrongpassword',
                    request=request,
                )
            except AuthenticationError:
                pass
        with pytest.raises(AuthenticationError, match='登录失败次数过多'):
            AuthService.login(
                username='wb_teacher',
                password='wrongpassword',
                request=request,
            )

    def test_login_updates_last_login_ip(self, db, wb_teacher, wb_request_factory):
        request = wb_request_factory.post('/auth/login/')
        request.META['REMOTE_ADDR'] = '192.168.1.1'
        AuthService.login(
            username='wb_teacher',
            password='WbTest@123456',
            request=request,
        )
        wb_teacher.refresh_from_db()
        assert wb_teacher.last_login_ip == '192.168.1.1'

    def test_login_clears_failed_count_on_success(self, db, wb_teacher, wb_request_factory):
        request = wb_request_factory.post('/auth/login/')
        request.META['REMOTE_ADDR'] = '127.0.0.5'
        try:
            AuthService.login(username='wb_teacher', password='wrong', request=request)
        except AuthenticationError:
            pass
        assert cache.get(f'{LOGIN_FAILED_PREFIX}127.0.0.5', 0) > 0
        AuthService.login(username='wb_teacher', password='WbTest@123456', request=request)
        assert cache.get(f'{LOGIN_FAILED_PREFIX}127.0.0.5') is None

    def test_login_user_info_contains_roles(self, db, wb_teacher, wb_request_factory):
        request = wb_request_factory.post('/auth/login/')
        request.META['REMOTE_ADDR'] = '127.0.0.6'
        result = AuthService.login(
            username='wb_teacher',
            password='WbTest@123456',
            request=request,
        )
        user_info = result['user']
        assert 'role' in user_info
        assert 'roles' in user_info
        assert 'is_teacher' in user_info


class TestChangePassword:
    def test_change_password_success(self, db, wb_teacher):
        AuthService.change_password(
            user=wb_teacher,
            old_password='WbTest@123456',
            new_password='NewPass@123',
            confirm_password='NewPass@123',
        )
        assert wb_teacher.check_password('NewPass@123')

    def test_change_password_mismatch(self, db, wb_teacher):
        with pytest.raises(ValidationError, match='两次密码输入不一致'):
            AuthService.change_password(
                user=wb_teacher,
                old_password='WbTest@123456',
                new_password='NewPass@123',
                confirm_password='Different@123',
            )

    def test_change_password_wrong_old(self, db, wb_teacher):
        with pytest.raises(ValidationError, match='原密码错误'):
            AuthService.change_password(
                user=wb_teacher,
                old_password='wrongpassword',
                new_password='NewPass@123',
                confirm_password='NewPass@123',
            )

    def test_change_password_sets_first_login_false(self, db, wb_teacher):
        wb_teacher.first_login = True
        wb_teacher.save()
        AuthService.change_password(
            user=wb_teacher,
            old_password='WbTest@123456',
            new_password='NewPass@123',
            confirm_password='NewPass@123',
        )
        wb_teacher.refresh_from_db()
        assert wb_teacher.first_login is False


class TestResetPasswordByAdmin:
    def test_super_admin_can_reset(self, db, wb_super_admin, wb_teacher):
        result = AuthService.reset_password_by_admin(wb_super_admin, wb_teacher.id)
        assert result['user_id'] == wb_teacher.id
        assert 'new_password' in result

    def test_dept_admin_can_reset_same_dept(self, db, wb_dept_admin, wb_teacher):
        result = AuthService.reset_password_by_admin(wb_dept_admin, wb_teacher.id)
        assert result['user_id'] == wb_teacher.id

    def test_dept_admin_cannot_reset_other_dept(self, db, wb_dept_admin):
        other_dept_user = User.objects.create_user(
            username='wb_other_dept_user',
            password='Test@123456',
            role=UserRole.TEACHER,
            is_active=True,
        )
        with pytest.raises(AuthenticationError, match='只能重置本部门用户密码'):
            AuthService.reset_password_by_admin(wb_dept_admin, other_dept_user.id)

    def test_teacher_cannot_reset(self, db, wb_teacher):
        with pytest.raises(AuthenticationError, match='无权限重置密码'):
            AuthService.reset_password_by_admin(wb_teacher, 1)

    def test_default_password_is_username_prefix(self, db, wb_super_admin, wb_teacher):
        result = AuthService.reset_password_by_admin(wb_super_admin, wb_teacher.id)
        assert result['new_password'] == 'wb_tea'

    def test_reset_nonexistent_user(self, db, wb_super_admin):
        with pytest.raises(ValidationError, match='用户不存在'):
            AuthService.reset_password_by_admin(wb_super_admin, 99999)

    def test_reset_sets_first_login(self, db, wb_super_admin, wb_teacher):
        wb_teacher.first_login = False
        wb_teacher.save()
        AuthService.reset_password_by_admin(wb_super_admin, wb_teacher.id)
        wb_teacher.refresh_from_db()
        assert wb_teacher.first_login is True


class TestBatchResetPassword:
    def test_batch_reset_success(self, db, wb_super_admin, wb_teacher, wb_lab_admin):
        result = AuthService.batch_reset_password(
            wb_super_admin, [wb_teacher.id, wb_lab_admin.id]
        )
        assert result['success_count'] == 2
        assert result['failed_count'] == 0

    def test_batch_reset_partial_failure(self, db, wb_super_admin, wb_teacher):
        result = AuthService.batch_reset_password(
            wb_super_admin, [wb_teacher.id, 99999]
        )
        assert result['success_count'] == 1
        assert result['failed_count'] == 1

    def test_batch_reset_no_permission(self, db, wb_teacher):
        with pytest.raises(AuthenticationError):
            AuthService.batch_reset_password(wb_teacher, [1])


class TestSecurityQuestion:
    def test_set_security_question(self, db, wb_teacher):
        result = AuthService.set_security_question(
            wb_teacher, '您的母亲姓名是？', '张三'
        )
        assert result is True
        wb_teacher.refresh_from_db()
        assert wb_teacher.security_question == '您的母亲姓名是？'

    def test_set_empty_question(self, db, wb_teacher):
        with pytest.raises(ValidationError, match='请选择问题并填写答案'):
            AuthService.set_security_question(wb_teacher, '', 'answer')

    def test_set_empty_answer(self, db, wb_teacher):
        with pytest.raises(ValidationError, match='请选择问题并填写答案'):
            AuthService.set_security_question(wb_teacher, '问题', '')

    def test_set_invalid_question(self, db, wb_teacher):
        with pytest.raises(ValidationError, match='请选择预设的密保问题'):
            AuthService.set_security_question(wb_teacher, '自定义问题？', 'answer')

    def test_answer_too_short(self, db, wb_teacher):
        with pytest.raises(ValidationError, match='答案长度'):
            AuthService.set_security_question(wb_teacher, SECURITY_QUESTIONS[0], 'a')

    def test_answer_too_long(self, db, wb_teacher):
        with pytest.raises(ValidationError, match='答案长度'):
            AuthService.set_security_question(wb_teacher, SECURITY_QUESTIONS[0], 'a' * 51)

    def test_get_security_questions(self):
        questions = AuthService.get_security_questions()
        assert len(questions) == len(SECURITY_QUESTIONS)

    def test_get_user_security_question(self, db, wb_teacher):
        AuthService.set_security_question(wb_teacher, SECURITY_QUESTIONS[0], 'TestAnswer')
        result = AuthService.get_user_security_question('wb_teacher')
        assert result['has_question'] is True
        assert result['question'] == SECURITY_QUESTIONS[0]

    def test_get_user_no_security_question(self, db, wb_teacher):
        result = AuthService.get_user_security_question('wb_teacher')
        assert result['has_question'] is False

    def test_get_nonexistent_user_security_question(self, db):
        with pytest.raises(ValidationError, match='用户不存在'):
            AuthService.get_user_security_question('nonexistent_user')


class TestVerifySecurityAnswer:
    def test_verify_correct_answer(self, db, wb_teacher, wb_request_factory):
        AuthService.set_security_question(wb_teacher, SECURITY_QUESTIONS[0], 'TestAnswer')
        request = wb_request_factory.post('/')
        request.META['REMOTE_ADDR'] = '127.0.0.10'
        result = AuthService.verify_security_answer(
            request, 'wb_teacher', 'testanswer'
        )
        assert 'reset_token' in result
        assert 'expires_in' in result

    def test_verify_wrong_answer(self, db, wb_teacher, wb_request_factory):
        AuthService.set_security_question(wb_teacher, SECURITY_QUESTIONS[0], 'TestAnswer')
        request = wb_request_factory.post('/')
        request.META['REMOTE_ADDR'] = '127.0.0.11'
        with pytest.raises(ValidationError, match='答案错误'):
            AuthService.verify_security_answer(
                request, 'wb_teacher', 'wronganswer'
            )

    def test_verify_rate_limiting(self, db, wb_teacher, wb_request_factory):
        AuthService.set_security_question(wb_teacher, SECURITY_QUESTIONS[0], 'TestAnswer')
        request = wb_request_factory.post('/')
        request.META['REMOTE_ADDR'] = '127.0.0.12'
        for _ in range(5):
            try:
                AuthService.verify_security_answer(request, 'wb_teacher', 'wrong')
            except (ValidationError, AuthenticationError):
                pass
        with pytest.raises(AuthenticationError, match='验证失败次数过多'):
            AuthService.verify_security_answer(request, 'wb_teacher', 'wrong')


class TestResetPasswordBySecurity:
    def test_reset_success(self, db, wb_teacher, wb_request_factory):
        AuthService.set_security_question(wb_teacher, SECURITY_QUESTIONS[0], 'TestAnswer')
        request = wb_request_factory.post('/')
        request.META['REMOTE_ADDR'] = '127.0.0.20'
        result = AuthService.verify_security_answer(
            request, 'wb_teacher', 'testanswer'
        )
        reset_token = result['reset_token']
        AuthService.reset_password_by_security(
            reset_token, 'NewPass@123', 'NewPass@123'
        )
        wb_teacher.refresh_from_db()
        assert wb_teacher.check_password('NewPass@123')

    def test_reset_expired_token(self, db):
        with pytest.raises(ValidationError, match='重置令牌已过期'):
            AuthService.reset_password_by_security(
                'invalid_token', 'NewPass@123', 'NewPass@123'
            )

    def test_reset_password_mismatch(self, db):
        with pytest.raises(ValidationError, match='两次密码不一致'):
            AuthService.reset_password_by_security(
                'token', 'NewPass@123', 'Different@123'
            )

    def test_reset_empty_fields(self, db):
        with pytest.raises(ValidationError, match='请填写完整信息'):
            AuthService.reset_password_by_security('', 'pass', 'pass')
