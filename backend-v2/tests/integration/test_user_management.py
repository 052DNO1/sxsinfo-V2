import pytest
from apps.users.services.user_service import UserService
from apps.users.services.auth_service import AuthService
from apps.users.models import User
from apps.core.constants import UserRole


class TestUserManagementWorkflow:
    def test_create_update_activate_deactivate(self, db, wb_super_admin, wb_department, wb_mock_request):
        service = UserService()
        user = service.create_user(
            requester=wb_super_admin,
            data={
                'username': 'wf_user',
                'nickname': '工作流用户',
                'role': UserRole.TEACHER,
                'department': wb_department,
            },
            request=wb_mock_request,
        )
        assert user.is_active is True

        user = service.activate_user(wb_super_admin, user.id, False, request=wb_mock_request)
        assert user.is_active is False

        user = service.activate_user(wb_super_admin, user.id, True, request=wb_mock_request)
        assert user.is_active is True

    def test_login_after_password_reset(self, db, wb_super_admin, wb_teacher, wb_request_factory):
        result = AuthService.reset_password_by_admin(wb_super_admin, wb_teacher.id)
        new_pwd = result['new_password']
        request = wb_request_factory.post('/auth/login/')
        request.META['REMOTE_ADDR'] = '127.0.0.99'
        login_result = AuthService.login(
            username=wb_teacher.username,
            password=new_pwd,
            request=request,
        )
        assert 'access_token' in login_result

    def test_delete_user_cannot_delete_self(self, db, wb_super_admin):
        service = UserService()
        from apps.core.exceptions import ValidationError
        with pytest.raises(ValidationError, match='不能删除自己'):
            service.delete_user(wb_super_admin, wb_super_admin.id)
