import pytest
from apps.laboratories.services.equipment_service import EquipmentService
from apps.laboratories.models import Equipment
from apps.core.exceptions import ValidationError, NotFoundError, PermissionDenied


@pytest.fixture
def eq_service():
    return EquipmentService()


class TestEquipmentServiceCreate:
    def test_create_success(self, db, wb_super_admin, wb_laboratory):
        service = EquipmentService()
        eq = service.create_equipment(
            requester=wb_super_admin,
            data={
                'name': '白盒新设备',
                'code': 'WB_EQ_NEW',
                'category': 'COMPUTER',
                'laboratory': wb_laboratory,
            },
        )
        assert eq.name == '白盒新设备'
        assert eq.code == 'WB_EQ_NEW'

    def test_create_no_name(self, db, wb_super_admin, wb_laboratory):
        service = EquipmentService()
        with pytest.raises(ValidationError, match='设备名称不能为空'):
            service.create_equipment(
                requester=wb_super_admin,
                data={
                    'code': 'WB_EQ_CODE',
                    'laboratory': wb_laboratory,
                },
            )

    def test_create_no_code(self, db, wb_super_admin, wb_laboratory):
        service = EquipmentService()
        with pytest.raises(ValidationError, match='设备编号不能为空'):
            service.create_equipment(
                requester=wb_super_admin,
                data={
                    'name': '测试设备',
                    'laboratory': wb_laboratory,
                },
            )

    def test_create_duplicate_code(self, db, wb_super_admin, wb_equipment, wb_laboratory):
        service = EquipmentService()
        with pytest.raises(ValidationError, match='已存在'):
            service.create_equipment(
                requester=wb_super_admin,
                data={
                    'name': '新设备',
                    'code': wb_equipment.code,
                    'laboratory': wb_laboratory,
                },
            )

    def test_create_no_permission(self, db, wb_teacher, wb_laboratory):
        service = EquipmentService()
        with pytest.raises(PermissionDenied):
            service.create_equipment(
                requester=wb_teacher,
                data={
                    'name': '测试',
                    'code': 'CODE',
                    'laboratory': wb_laboratory,
                },
            )


class TestEquipmentServiceUpdate:
    def test_update_name(self, db, wb_super_admin, wb_equipment):
        service = EquipmentService()
        eq = service.update_equipment(
            requester=wb_super_admin,
            equipment_id=wb_equipment.id,
            data={'name': '更新后设备名'},
        )
        assert eq.name == '更新后设备名'

    def test_update_nonexistent(self, db, wb_super_admin):
        service = EquipmentService()
        with pytest.raises(NotFoundError):
            service.update_equipment(
                requester=wb_super_admin,
                equipment_id=99999,
                data={'name': 'test'},
            )


class TestEquipmentServiceDelete:
    def test_delete_success(self, db, wb_super_admin, wb_equipment):
        service = EquipmentService()
        eq_id = wb_equipment.id
        result = service.delete_equipment(
            requester=wb_super_admin,
            equipment_id=eq_id,
        )
        assert result is True
        assert not Equipment.objects.filter(id=eq_id).exists()

    def test_delete_nonexistent(self, db, wb_super_admin):
        service = EquipmentService()
        with pytest.raises(NotFoundError):
            service.delete_equipment(
                requester=wb_super_admin,
                equipment_id=99999,
            )


class TestEquipmentServiceList:
    def test_list_default(self, db, wb_super_admin):
        service = EquipmentService()
        result = service.get_equipment_list(requester=wb_super_admin)
        assert 'list' in result
        assert 'total' in result

    def test_list_dept_admin(self, db, wb_dept_admin):
        service = EquipmentService()
        result = service.get_equipment_list(requester=wb_dept_admin)
        assert 'list' in result

    def test_list_lab_admin(self, db, wb_lab_admin):
        service = EquipmentService()
        result = service.get_equipment_list(requester=wb_lab_admin)
        assert 'list' in result
