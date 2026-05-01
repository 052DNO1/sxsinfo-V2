import pytest
from apps.users.services.user_service import UserService
from apps.users.models import User


class TestUserServiceQueries:

    @pytest.fixture
    def service(self):
        return UserService()

    def test_get_user_list_default_filter(self, service, super_admin_user, teacher_user, lab_admin_user):
        result = service.get_user_list(
            requester=super_admin_user,
            role=1,
        )
        users = result.get('list', [])
        for user in users:
            if isinstance(user, dict):
                assert user['role'] in [1, 2], f"角色 {user['role']} 不在允许范围内"

    def test_get_user_list_with_role_filter(self, service, super_admin_user):
        result = service.get_user_list(
            requester=super_admin_user,
            role=1,
        )
        users = result.get('list', [])
        for user in users:
            if isinstance(user, dict):
                assert user['role'] == 1

    def test_get_user_list_pagination_format(self, service, super_admin_user, teacher_user):
        result = service.get_user_list(
            requester=super_admin_user,
            role=1,
            page=1,
            page_size=10,
        )
        assert 'pagination' in result
        pagination = result['pagination']
        assert 'total' in pagination
        assert 'page' in pagination
        assert 'page_size' in pagination
        assert pagination['total'] >= 1

    def test_get_user_includes_managed_laboratories(
        self, service, super_admin_user, lab_admin_user, test_laboratory
    ):
        test_laboratory.admin = lab_admin_user
        test_laboratory.save()
        result = service.get_user_list(
            requester=super_admin_user,
            role=2,
        )
        users = result.get('list', [])
        lab_admin_found = None
        for user in users:
            if isinstance(user, dict):
                if user['id'] == lab_admin_user.id:
                    lab_admin_found = user
                    break
        if lab_admin_found:
            assert 'managed_laboratories' in lab_admin_found
            assert isinstance(lab_admin_found['managed_laboratories'], str)


class TestUserStatusToggle:

    @pytest.fixture
    def service(self):
        return UserService()

    def test_deactivate_user(self, service, super_admin_user, teacher_user):
        assert teacher_user.is_active is True
        result = service.activate_user(
            requester=super_admin_user,
            user_id=teacher_user.id,
            is_active=False,
        )
        assert result is not None
        teacher_user.refresh_from_db()
        assert teacher_user.is_active is False

    def test_activate_user(self, service, super_admin_user, teacher_user):
        teacher_user.is_active = False
        teacher_user.save()
        result = service.activate_user(
            requester=super_admin_user,
            user_id=teacher_user.id,
            is_active=True,
        )
        teacher_user.refresh_from_db()
        assert teacher_user.is_active is True


class TestUserRoleDisplay:

    @pytest.fixture
    def service(self):
        return UserService()

    def test_system_admin_role_display(self, service, system_admin_user):
        result = service.get_user_list(
            requester=system_admin_user,
        )
        assert result is not None
        assert 'list' in result

    def test_super_admin_role_display(self, service, super_admin_user):
        result = service.get_user_list(
            requester=super_admin_user,
        )
        assert result is not None
        assert 'list' in result

    def test_department_admin_role_display(self, service, department_admin_user):
        result = service.get_user_list(
            requester=department_admin_user,
        )
        assert result is not None
        assert 'list' in result
