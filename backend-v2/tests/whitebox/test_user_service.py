import pytest
from apps.users.services.user_service import UserService
from apps.users.models import User, Department
from apps.core.exceptions import ValidationError, NotFoundError, PermissionDenied
from apps.core.constants import UserRole


@pytest.fixture
def user_service():
    return UserService()


class TestUserServiceCreate:
    def test_create_success(self, db, wb_super_admin, wb_department, wb_mock_request):
        service = UserService()
        user = service.create_user(
            requester=wb_super_admin,
            data={
                'username': 'wb_new_user',
                'nickname': '白盒新用户',
                'role': UserRole.TEACHER,
                'department': wb_department,
            },
            request=wb_mock_request,
        )
        assert user.username == 'wb_new_user'
        assert user.role == UserRole.TEACHER

    def test_create_no_permission(self, db, wb_teacher):
        service = UserService()
        with pytest.raises(PermissionDenied):
            service.create_user(
                requester=wb_teacher,
                data={'username': 'test'},
            )

    def test_create_empty_username(self, db, wb_super_admin):
        service = UserService()
        with pytest.raises(ValidationError, match='用户名不能为空'):
            service.create_user(
                requester=wb_super_admin,
                data={'username': ''},
            )

    def test_create_duplicate_username(self, db, wb_super_admin, wb_teacher):
        service = UserService()
        with pytest.raises(ValidationError, match='已存在'):
            service.create_user(
                requester=wb_super_admin,
                data={'username': wb_teacher.username},
            )

    def test_create_dept_admin_without_department(self, db, wb_super_admin):
        service = UserService()
        with pytest.raises(ValidationError, match='分院管理员必须指定所属部门'):
            service.create_user(
                requester=wb_super_admin,
                data={
                    'username': 'wb_dept_no_dept',
                    'role': UserRole.DEPARTMENT_ADMIN,
                },
            )

    def test_create_default_password(self, db, wb_super_admin, wb_department):
        service = UserService()
        user = service.create_user(
            requester=wb_super_admin,
            data={
                'username': 'wb_default_pwd',
                'department': wb_department,
            },
        )
        # 默认密码应为随机强口令（不再使用 username[:6] 弱口令），且需首登改密
        assert not user.check_password('wb_def')
        assert not user.check_password('wb_default_pwd')
        assert user.first_login is True

    def test_create_dept_admin_forced_own_dept(self, db, wb_dept_admin):
        service = UserService()
        user = service.create_user(
            requester=wb_dept_admin,
            data={
                'username': 'wb_dept_forced',
                'department': wb_dept_admin.department,
            },
        )
        assert user.department_id == wb_dept_admin.department_id


class TestUserServiceUpdate:
    def test_update_nickname(self, db, wb_super_admin, wb_teacher, wb_mock_request):
        service = UserService()
        user = service.update_user(
            requester=wb_super_admin,
            user_id=wb_teacher.id,
            data={'nickname': '更新昵称'},
            request=wb_mock_request,
        )
        assert user.nickname == '更新昵称'

    def test_update_nonexistent(self, db, wb_super_admin):
        service = UserService()
        with pytest.raises(NotFoundError):
            service.update_user(
                requester=wb_super_admin,
                user_id=99999,
                data={'nickname': 'test'},
            )

    def test_update_no_permission(self, db, wb_teacher, wb_lab_admin):
        service = UserService()
        with pytest.raises(PermissionDenied):
            service.update_user(
                requester=wb_teacher,
                user_id=wb_lab_admin.id,
                data={'nickname': 'test'},
            )


class TestUserServiceDelete:
    def test_delete_success(self, db, wb_super_admin, wb_teacher, wb_mock_request):
        service = UserService()
        result = service.delete_user(
            requester=wb_super_admin,
            user_id=wb_teacher.id,
            request=wb_mock_request,
        )
        assert result is True

    def test_delete_self_fails(self, db, wb_super_admin):
        service = UserService()
        with pytest.raises(ValidationError, match='不能删除自己'):
            service.delete_user(
                requester=wb_super_admin,
                user_id=wb_super_admin.id,
            )

    def test_delete_nonexistent(self, db, wb_super_admin):
        service = UserService()
        with pytest.raises(NotFoundError):
            service.delete_user(
                requester=wb_super_admin,
                user_id=99999,
            )


class TestUserServiceActivate:
    def test_activate_user(self, db, wb_super_admin, wb_inactive_user, wb_mock_request):
        service = UserService()
        user = service.activate_user(
            requester=wb_super_admin,
            user_id=wb_inactive_user.id,
            is_active=True,
            request=wb_mock_request,
        )
        assert user.is_active is True

    def test_deactivate_user(self, db, wb_super_admin, wb_teacher, wb_mock_request):
        service = UserService()
        user = service.activate_user(
            requester=wb_super_admin,
            user_id=wb_teacher.id,
            is_active=False,
            request=wb_mock_request,
        )
        assert user.is_active is False


class TestUserServiceList:
    def test_list_default(self, db, wb_super_admin):
        service = UserService()
        result = service.get_user_list(requester=wb_super_admin)
        assert 'list' in result
        assert 'pagination' in result

    def test_list_dept_admin_filtered(self, db, wb_dept_admin):
        service = UserService()
        result = service.get_user_list(requester=wb_dept_admin)
        assert 'list' in result

    def test_list_with_search(self, db, wb_super_admin, wb_teacher):
        service = UserService()
        result = service.get_user_list(
            requester=wb_super_admin,
            search='wb_teacher',
        )
        assert result['pagination']['total'] >= 1

    def test_list_no_page(self, db, wb_super_admin):
        service = UserService()
        result = service.get_user_list(requester=wb_super_admin, no_page=True)
        assert 'list' in result
        assert 'pagination' in result
        assert 'total_pages' not in result['pagination']


class TestUserServiceCleanup:
    def test_cleanup_no_permission(self, db, wb_teacher):
        service = UserService()
        with pytest.raises(PermissionDenied):
            service.cleanup_user_data(requester=wb_teacher, user_id=1)

    def test_cleanup_success(self, db, wb_super_admin, wb_teacher, wb_schedule):
        service = UserService()
        result = service.cleanup_user_data(
            requester=wb_super_admin,
            user_id=wb_teacher.id,
        )
        assert 'schedules' in result
        assert 'records' in result
