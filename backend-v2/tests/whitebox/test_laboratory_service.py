import pytest
from apps.laboratories.services.laboratory_service import LaboratoryService
from apps.laboratories.models import Laboratory
from apps.core.exceptions import ValidationError, NotFoundError, PermissionDenied
from apps.core.constants import UserRole, LaboratoryStatus


@pytest.fixture
def lab_service():
    return LaboratoryService()


class TestLaboratoryServiceCreate:
    def test_create_success(self, db, wb_super_admin, wb_department, wb_mock_request):
        service = LaboratoryService()
        lab = service.create_laboratory(
            requester=wb_super_admin,
            data={
                'name': '白盒创建实训室',
                'code': 'WB_CREATE_001',
                'building': '测试楼',
                'floor': 1,
                'capacity': 40,
                'laboratory_type': 'COMPUTER',
                'department_id': wb_department.id,
            },
            request=wb_mock_request,
        )
        assert lab.name == '白盒创建实训室'
        assert lab.code == 'WB_CREATE_001'

    def test_create_empty_code(self, db, wb_super_admin):
        service = LaboratoryService()
        with pytest.raises(ValidationError, match='不能为空'):
            service.create_laboratory(
                requester=wb_super_admin,
                data={'name': '测试', 'code': ''},
            )

    def test_create_empty_name(self, db, wb_super_admin):
        service = LaboratoryService()
        with pytest.raises(ValidationError, match='不能为空'):
            service.create_laboratory(
                requester=wb_super_admin,
                data={'name': '', 'code': 'CODE001'},
            )

    def test_create_duplicate_code(self, db, wb_super_admin, wb_laboratory):
        service = LaboratoryService()
        with pytest.raises(ValidationError, match='已存在'):
            service.create_laboratory(
                requester=wb_super_admin,
                data={'name': '新实训室', 'code': wb_laboratory.code},
            )

    def test_create_duplicate_code_soft_deleted(self, db, wb_super_admin, wb_laboratory, wb_department):
        wb_laboratory.is_deleted = True
        wb_laboratory.save()
        service = LaboratoryService()
        lab = service.create_laboratory(
            requester=wb_super_admin,
            data={'name': '新实训室', 'code': 'WB_LAB_001', 'department_id': wb_department.id},
        )
        wb_laboratory.refresh_from_db()
        assert wb_laboratory.code.startswith('del_')

    def test_create_no_permission(self, db, wb_teacher):
        service = LaboratoryService()
        with pytest.raises(PermissionDenied):
            service.create_laboratory(
                requester=wb_teacher,
                data={'name': '测试', 'code': 'CODE001'},
            )

    def test_create_dept_admin_forced_own_dept(self, db, wb_dept_admin, wb_department):
        service = LaboratoryService()
        lab = service.create_laboratory(
            requester=wb_dept_admin,
            data={
                'name': '分院管理员创建',
                'code': 'WB_DEPT_CREATE',
                'department_id': 999,
            },
        )
        assert lab.department_id == wb_department.id

    def test_create_admin_must_be_same_dept(self, db, wb_dept_admin, wb_department):
        from apps.users.models import User
        other_dept_user = User.objects.create_user(
            username='wb_other_dept_admin2',
            password='Test@123456',
            role=UserRole.LABORATORY_ADMIN,
            is_active=True,
        )
        service = LaboratoryService()
        with pytest.raises(ValidationError, match='只能分配本部门'):
            service.create_laboratory(
                requester=wb_dept_admin,
                data={
                    'name': '测试',
                    'code': 'WB_CROSS_DEPT',
                    'admin': other_dept_user.id,
                },
            )


class TestLaboratoryServiceUpdate:
    def test_update_name(self, db, wb_super_admin, wb_laboratory, wb_mock_request):
        service = LaboratoryService()
        lab = service.update_laboratory(
            requester=wb_super_admin,
            laboratory_id=wb_laboratory.id,
            data={'name': '更新后名称'},
            request=wb_mock_request,
        )
        assert lab.name == '更新后名称'

    def test_update_set_admin_to_none(self, db, wb_super_admin, wb_laboratory, wb_mock_request):
        service = LaboratoryService()
        lab = service.update_laboratory(
            requester=wb_super_admin,
            laboratory_id=wb_laboratory.id,
            data={'admin': None},
            request=wb_mock_request,
        )
        assert lab.admin is None

    def test_update_set_admin_to_zero(self, db, wb_super_admin, wb_laboratory, wb_mock_request):
        service = LaboratoryService()
        lab = service.update_laboratory(
            requester=wb_super_admin,
            laboratory_id=wb_laboratory.id,
            data={'admin': 0},
            request=wb_mock_request,
        )
        assert lab.admin is None

    def test_update_nonexistent(self, db, wb_super_admin):
        service = LaboratoryService()
        with pytest.raises(NotFoundError):
            service.update_laboratory(
                requester=wb_super_admin,
                laboratory_id=99999,
                data={'name': 'test'},
            )

    def test_update_status_links_availability(self, db, wb_super_admin, wb_laboratory, wb_mock_request):
        service = LaboratoryService()
        lab = service.update_laboratory(
            requester=wb_super_admin,
            laboratory_id=wb_laboratory.id,
            data={'status': LaboratoryStatus.MAINTENANCE},
            request=wb_mock_request,
        )
        assert lab.is_available is False

    def test_update_duplicate_code(self, db, wb_super_admin, wb_laboratory, wb_laboratory2):
        service = LaboratoryService()
        with pytest.raises(ValidationError, match='已存在'):
            service.update_laboratory(
                requester=wb_super_admin,
                laboratory_id=wb_laboratory.id,
                data={'code': wb_laboratory2.code},
            )


class TestLaboratoryServiceDelete:
    def test_delete_no_related_data_hard_delete(self, db, wb_super_admin, wb_laboratory, wb_mock_request):
        service = LaboratoryService()
        lab_id = wb_laboratory.id
        result = service.delete_laboratory(
            requester=wb_super_admin,
            laboratory_id=lab_id,
            request=wb_mock_request,
        )
        assert result['success'] is True
        assert not Laboratory.objects.filter(id=lab_id).exists()

    def test_delete_with_records_soft_delete(self, db, wb_super_admin, wb_laboratory, wb_usage_record, wb_mock_request):
        service = LaboratoryService()
        lab_id = wb_laboratory.id
        result = service.delete_laboratory(
            requester=wb_super_admin,
            laboratory_id=lab_id,
            request=wb_mock_request,
        )
        assert result['success'] is True
        assert result['preserved_counts']['usage_records'] > 0
        wb_usage_record.refresh_from_db()
        assert wb_usage_record.laboratory is None
        assert wb_usage_record.laboratory_name == '白盒测试实训室'

    def test_delete_with_work_orders_preserves(self, db, wb_super_admin, wb_laboratory, wb_work_order, wb_mock_request):
        service = LaboratoryService()
        result = service.delete_laboratory(
            requester=wb_super_admin,
            laboratory_id=wb_laboratory.id,
            request=wb_mock_request,
        )
        assert result['preserved_counts']['work_orders'] > 0
        wb_work_order.refresh_from_db()
        assert wb_work_order.laboratory is None

    def test_delete_nonexistent(self, db, wb_super_admin):
        service = LaboratoryService()
        with pytest.raises(NotFoundError):
            service.delete_laboratory(
                requester=wb_super_admin,
                laboratory_id=99999,
            )

    def test_delete_teacher_no_permission(self, db, wb_teacher, wb_laboratory):
        service = LaboratoryService()
        with pytest.raises(PermissionDenied):
            service.delete_laboratory(
                requester=wb_teacher,
                laboratory_id=wb_laboratory.id,
            )


class TestLaboratoryServicePermissions:
    def test_super_admin_can_view_all(self, db, wb_super_admin, wb_laboratory):
        service = LaboratoryService()
        result = service.get_laboratory_list(requester=wb_super_admin)
        assert result['pagination']['total'] >= 1
        lab_ids = [lab['id'] for lab in result['list']]
        assert wb_laboratory.id in lab_ids

    def test_dept_admin_sees_own_dept_labs(self, db, wb_dept_admin, wb_laboratory):
        service = LaboratoryService()
        result = service.get_laboratory_list(requester=wb_dept_admin)
        lab_ids = [lab['id'] for lab in result['list']]
        assert wb_laboratory.id in lab_ids

    def test_lab_admin_sees_own_labs(self, db, wb_lab_admin, wb_laboratory):
        service = LaboratoryService()
        result = service.get_laboratory_list(requester=wb_lab_admin)
        lab_ids = [lab['id'] for lab in result['list']]
        assert wb_laboratory.id in lab_ids


class TestLaboratoryServiceCheckDeleteImpact:
    def test_check_impact_with_data(self, db, wb_super_admin, wb_laboratory, wb_usage_record):
        service = LaboratoryService()
        result = service.check_delete_impact(
            requester=wb_super_admin,
            laboratory_ids=[wb_laboratory.id],
        )
        assert result['has_related_data'] is True

    def test_check_impact_empty(self, db, wb_super_admin, wb_laboratory):
        service = LaboratoryService()
        result = service.check_delete_impact(
            requester=wb_super_admin,
            laboratory_ids=[wb_laboratory.id],
        )
        assert result['has_related_data'] is False
