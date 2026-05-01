import pytest
from apps.users.services.department_service import DepartmentService
from apps.users.models import Department
from apps.core.exceptions import ValidationError, NotFoundError, PermissionDenied


@pytest.fixture
def dept_service():
    return DepartmentService()


class TestDepartmentServiceCheckManagerConflicts:
    def test_no_conflicts(self, db, wb_super_admin, wb_department):
        service = DepartmentService()
        result = service.check_manager_conflicts(
            requester=wb_super_admin,
            department_id=wb_department.id,
            manager_ids=[],
        )
        assert result['has_conflicts'] is False

    def test_non_admin_cannot_check(self, db, wb_teacher):
        service = DepartmentService()
        with pytest.raises(PermissionDenied, match='只有超级管理员'):
            service.check_manager_conflicts(
                requester=wb_teacher,
                department_id=1,
                manager_ids=[],
            )


class TestDepartmentServiceCreate:
    def test_create_success(self, db, wb_super_admin):
        service = DepartmentService()
        dept = service.create_department(
            requester=wb_super_admin,
            data={'name': '白盒新建分院', 'code': 'WB_NEW_DEPT'},
        )
        assert dept.name == '白盒新建分院'
        assert dept.code == 'WB_NEW_DEPT'

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

    def test_create_duplicate_code(self, db, wb_super_admin, wb_department):
        service = DepartmentService()
        with pytest.raises(ValidationError, match='已存在'):
            service.create_department(
                requester=wb_super_admin,
                data={'name': '唯一名称', 'code': wb_department.code},
            )


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
        with pytest.raises(NotFoundError):
            service.update_department(
                requester=wb_super_admin,
                department_id=99999,
                data={'name': 'test'},
            )


class TestDepartmentServiceDelete:
    def test_delete_empty_department(self, db, wb_super_admin):
        dept = Department.objects.create(name='空分院', code='WB_EMPTY')
        service = DepartmentService()
        result = service.delete_department(
            requester=wb_super_admin,
            department_id=dept.id,
        )
        assert result is True

    def test_delete_with_users_requires_cascade(self, db, wb_super_admin, wb_department):
        service = DepartmentService()
        with pytest.raises(ValidationError, match='用户'):
            service.delete_department(
                requester=wb_super_admin,
                department_id=wb_department.id,
            )

    def test_delete_no_permission(self, db, wb_teacher, wb_department):
        service = DepartmentService()
        with pytest.raises(PermissionDenied):
            service.delete_department(
                requester=wb_teacher,
                department_id=wb_department.id,
            )


class TestDepartmentServiceList:
    def test_list_as_super_admin(self, db, wb_super_admin):
        service = DepartmentService()
        result = service.get_department_list(requester=wb_super_admin)
        assert 'list' in result
        assert 'pagination' in result

    def test_list_no_permission(self, db, wb_teacher):
        service = DepartmentService()
        with pytest.raises(PermissionDenied):
            service.get_department_list(requester=wb_teacher)
