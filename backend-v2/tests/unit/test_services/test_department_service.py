import pytest
from apps.users.services.department_service import DepartmentService
from apps.users.models import Department
from apps.core.exceptions import PermissionDenied, ValidationError


@pytest.fixture
def dept_service():
    return DepartmentService()


class TestDepartmentServiceCreate:
    def test_create_success(self, db, wb_super_admin):
        service = DepartmentService()
        dept = service.create_department(
            requester=wb_super_admin,
            data={'name': '单元测试分院', 'code': 'UT_DEPT'},
        )
        assert dept.name == '单元测试分院'

    def test_create_no_permission(self, db, wb_teacher):
        service = DepartmentService()
        with pytest.raises(PermissionDenied):
            service.create_department(requester=wb_teacher, data={})

    def test_create_empty_name(self, db, wb_super_admin):
        service = DepartmentService()
        with pytest.raises(ValidationError, match='不能为空'):
            service.create_department(requester=wb_super_admin, data={'name': ''})

    def test_create_duplicate_name(self, db, wb_super_admin, wb_department):
        service = DepartmentService()
        with pytest.raises(ValidationError, match='已存在'):
            service.create_department(
                requester=wb_super_admin,
                data={'name': wb_department.name},
            )

    def test_create_auto_generate_code(self, db, wb_super_admin):
        service = DepartmentService()
        dept = service.create_department(
            requester=wb_super_admin,
            data={'name': '自动编码分院'},
        )
        assert dept.code != ''


class TestDepartmentServiceUpdate:
    def test_update_name(self, db, wb_super_admin, wb_department):
        service = DepartmentService()
        dept = service.update_department(
            requester=wb_super_admin,
            department_id=wb_department.id,
            data={'name': '更新后分院'},
        )
        assert dept.name == '更新后分院'

    def test_update_no_permission(self, db, wb_teacher, wb_department):
        service = DepartmentService()
        with pytest.raises(PermissionDenied):
            service.update_department(
                requester=wb_teacher,
                department_id=wb_department.id,
                data={'name': 'test'},
            )

    def test_update_nonexistent(self, db, wb_super_admin):
        service = DepartmentService()
        from apps.core.exceptions import NotFoundError
        with pytest.raises(NotFoundError):
            service.update_department(
                requester=wb_super_admin,
                department_id=99999,
                data={'name': 'test'},
            )


class TestDepartmentServiceDelete:
    def test_delete_empty_department(self, db, wb_super_admin):
        dept = Department.objects.create(name='空分院', code='UT_EMPTY')
        service = DepartmentService()
        result = service.delete_department(requester=wb_super_admin, department_id=dept.id)
        assert result is True

    def test_delete_with_users_requires_cascade(self, db, wb_super_admin, wb_department):
        service = DepartmentService()
        with pytest.raises(ValidationError, match='用户'):
            service.delete_department(
                requester=wb_super_admin,
                department_id=wb_department.id,
            )

    def test_delete_cascade(self, db, wb_super_admin, wb_department):
        service = DepartmentService()
        result = service.delete_department(
            requester=wb_super_admin,
            department_id=wb_department.id,
            cascade=True,
        )
        assert result is True

    def test_delete_no_permission(self, db, wb_teacher, wb_department):
        service = DepartmentService()
        with pytest.raises(PermissionDenied):
            service.delete_department(
                requester=wb_teacher,
                department_id=wb_department.id,
            )
