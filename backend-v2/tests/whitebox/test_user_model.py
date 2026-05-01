import pytest
from apps.core.constants import UserRole
from django.contrib.auth import get_user_model

User = get_user_model()


class TestUserRoleBitOperations:
    def test_teacher_role_property(self, db, wb_teacher):
        assert wb_teacher.role == UserRole.TEACHER
        assert wb_teacher.is_teacher is True
        assert wb_teacher.is_laboratory_admin is False
        assert wb_teacher.is_department_admin is False
        assert wb_teacher.is_super_admin is False
        assert wb_teacher.is_system_admin is False

    def test_lab_admin_role_property(self, db, wb_lab_admin):
        assert wb_lab_admin.role == UserRole.LABORATORY_ADMIN
        assert wb_lab_admin.is_teacher is False
        assert wb_lab_admin.is_laboratory_admin is True

    def test_dept_admin_role_property(self, db, wb_dept_admin):
        assert wb_dept_admin.role == UserRole.DEPARTMENT_ADMIN
        assert wb_dept_admin.is_department_admin is True

    def test_super_admin_role_property(self, db, wb_super_admin):
        assert wb_super_admin.role == UserRole.SUPER_ADMIN
        assert wb_super_admin.is_super_admin is True

    def test_system_admin_role_property(self, db, wb_system_admin):
        assert wb_system_admin.role == UserRole.SYSTEM_ADMIN
        assert wb_system_admin.is_system_admin is True

    def test_superuser_overrides_role(self, db):
        user = User.objects.create_user(
            username='wb_test_superuser',
            password='Test@123456',
            is_superuser=True,
            role=UserRole.TEACHER,
        )
        assert user.is_super_admin is True
        assert user.is_system_admin is True
        assert user.is_teacher is True

    def test_has_role(self, db, wb_teacher):
        assert wb_teacher.has_role(UserRole.TEACHER) is True
        assert wb_teacher.has_role(UserRole.LABORATORY_ADMIN) is False
        assert wb_teacher.has_role(UserRole.DEPARTMENT_ADMIN) is False

    def test_has_role_with_zero_role(self, db):
        user = User.objects.create_user(
            username='wb_zero_role',
            password='Test@123456',
            role=0,
        )
        assert user.has_role(UserRole.TEACHER) is False

    def test_add_role(self, db, wb_teacher):
        wb_teacher.add_role(UserRole.LABORATORY_ADMIN)
        assert wb_teacher.role == UserRole.TEACHER | UserRole.LABORATORY_ADMIN
        assert wb_teacher.is_teacher is True
        assert wb_teacher.is_laboratory_admin is True

    def test_add_role_from_zero(self, db):
        user = User.objects.create_user(
            username='wb_add_from_zero',
            password='Test@123456',
            role=0,
        )
        user.add_role(UserRole.TEACHER)
        assert user.role == UserRole.TEACHER
        assert user.is_teacher is True

    def test_remove_role(self, db, wb_teacher):
        wb_teacher.add_role(UserRole.LABORATORY_ADMIN)
        wb_teacher.remove_role(UserRole.LABORATORY_ADMIN)
        assert wb_teacher.is_teacher is True
        assert wb_teacher.is_laboratory_admin is False

    def test_remove_role_to_zero(self, db):
        user = User.objects.create_user(
            username='wb_remove_to_zero',
            password='Test@123456',
            role=UserRole.TEACHER,
        )
        user.remove_role(UserRole.TEACHER)
        assert user.role == 0
        assert user.is_teacher is False

    def test_remove_role_already_zero(self, db):
        user = User.objects.create_user(
            username='wb_remove_zero',
            password='Test@123456',
            role=0,
        )
        user.remove_role(UserRole.TEACHER)
        assert user.role == 0

    def test_combined_roles(self, db):
        user = User.objects.create_user(
            username='wb_combined',
            password='Test@123456',
            role=UserRole.TEACHER | UserRole.LABORATORY_ADMIN,
        )
        assert user.is_teacher is True
        assert user.is_laboratory_admin is True
        assert user.is_department_admin is False

    def test_triple_role(self, db):
        user = User.objects.create_user(
            username='wb_triple',
            password='Test@123456',
            role=UserRole.TEACHER | UserRole.LABORATORY_ADMIN | UserRole.DEPARTMENT_ADMIN,
        )
        assert user.is_teacher is True
        assert user.is_laboratory_admin is True
        assert user.is_department_admin is True

    def test_get_roles_single(self, db, wb_teacher):
        roles = wb_teacher.get_roles()
        assert len(roles) == 1
        assert roles[0]['value'] == UserRole.TEACHER

    def test_get_roles_multiple(self, db):
        user = User.objects.create_user(
            username='wb_multi_role',
            password='Test@123456',
            role=UserRole.TEACHER | UserRole.LABORATORY_ADMIN,
        )
        roles = user.get_roles()
        assert len(roles) == 2
        role_values = [r['value'] for r in roles]
        assert UserRole.TEACHER in role_values
        assert UserRole.LABORATORY_ADMIN in role_values

    def test_get_roles_zero(self, db):
        user = User.objects.create_user(
            username='wb_no_role',
            password='Test@123456',
            role=0,
        )
        roles = user.get_roles()
        assert roles == []

    def test_role_bit_values(self):
        assert UserRole.TEACHER == 1
        assert UserRole.LABORATORY_ADMIN == 2
        assert UserRole.DEPARTMENT_ADMIN == 4
        assert UserRole.SUPER_ADMIN == 16
        assert UserRole.SYSTEM_ADMIN == 32

    def test_role_bit_independence(self):
        for role_a in UserRole:
            for role_b in UserRole:
                if role_a != role_b:
                    assert role_a & role_b == 0

    def test_add_then_remove_restores(self, db, wb_teacher):
        original_role = wb_teacher.role
        wb_teacher.add_role(UserRole.LABORATORY_ADMIN)
        wb_teacher.remove_role(UserRole.LABORATORY_ADMIN)
        assert wb_teacher.role == original_role
