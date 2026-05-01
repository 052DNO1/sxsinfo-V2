import pytest
from apps.users.services.department_service import DepartmentService
from apps.users.models import Department, User
from apps.core.constants import UserRole
from apps.core.exceptions import PermissionDenied, ValidationError


class TestDepartmentFullWorkflow:
    def test_create_update_delete(self, db, wb_super_admin):
        service = DepartmentService()
        dept = service.create_department(
            requester=wb_super_admin,
            data={'name': '集成测试分院', 'code': 'INT_DEPT'},
        )
        assert dept.name == '集成测试分院'

        updated = service.update_department(
            requester=wb_super_admin,
            department_id=dept.id,
            data={'name': '更新后分院'},
        )
        assert updated.name == '更新后分院'

        result = service.delete_department(requester=wb_super_admin, department_id=dept.id)
        assert result is True

    def test_cascade_delete_with_users(self, db, wb_super_admin, wb_department):
        service = DepartmentService()
        result = service.delete_department(
            requester=wb_super_admin,
            department_id=wb_department.id,
            cascade=True,
        )
        assert result is True

    def test_non_cascade_delete_with_users_fails(self, db, wb_super_admin, wb_department):
        service = DepartmentService()
        with pytest.raises(ValidationError, match='用户'):
            service.delete_department(
                requester=wb_super_admin,
                department_id=wb_department.id,
                cascade=False,
            )

    def test_teacher_cannot_create(self, db, wb_teacher):
        service = DepartmentService()
        with pytest.raises(PermissionDenied):
            service.create_department(requester=wb_teacher, data={'name': 'test'})

    def test_duplicate_name_fails(self, db, wb_super_admin, wb_department):
        service = DepartmentService()
        with pytest.raises(ValidationError, match='已存在'):
            service.create_department(
                requester=wb_super_admin,
                data={'name': wb_department.name},
            )
