import pytest
from apps.laboratories.serializers.laboratory import (
    LaboratorySerializer, LaboratoryCreateSerializer, LaboratoryUpdateSerializer,
    EquipmentSerializer, EquipmentCreateSerializer, EquipmentUpdateSerializer
)


class TestLaboratoryCreateSerializer:
    def test_valid_data(self, db, wb_department):
        data = {
            'name': '序列化器创建实训室',
            'code': 'SER_LAB_001',
            'department': wb_department.id,
            'capacity': 30,
        }
        serializer = LaboratoryCreateSerializer(data=data)
        assert serializer.is_valid(), serializer.errors

    def test_empty_name(self, db):
        data = {'name': '', 'code': 'CODE001'}
        serializer = LaboratoryCreateSerializer(data=data)
        assert not serializer.is_valid()
        assert 'name' in serializer.errors

    def test_empty_code(self, db):
        data = {'name': '测试', 'code': ''}
        serializer = LaboratoryCreateSerializer(data=data)
        assert not serializer.is_valid()
        assert 'code' in serializer.errors


class TestLaboratoryUpdateSerializer:
    def test_update_name(self, db, wb_laboratory):
        data = {'name': '更新名称', 'code': wb_laboratory.code}
        serializer = LaboratoryUpdateSerializer(instance=wb_laboratory, data=data, partial=True)
        assert serializer.is_valid(), serializer.errors

    def test_admin_none_should_pass(self, db, wb_laboratory):
        data = {'admin': None}
        serializer = LaboratoryUpdateSerializer(instance=wb_laboratory, data=data, partial=True)
        assert serializer.is_valid(), serializer.errors

    def test_admin_zero_should_pass(self, db, wb_laboratory):
        data = {'admin': 0}
        serializer = LaboratoryUpdateSerializer(instance=wb_laboratory, data=data, partial=True)
        assert serializer.is_valid(), serializer.errors

    def test_admin_empty_string_should_pass(self, db, wb_laboratory):
        data = {'admin': ''}
        serializer = LaboratoryUpdateSerializer(instance=wb_laboratory, data=data, partial=True)
        assert serializer.is_valid(), serializer.errors

    def test_admin_string_zero_should_pass(self, db, wb_laboratory):
        data = {'admin': '0'}
        serializer = LaboratoryUpdateSerializer(instance=wb_laboratory, data=data, partial=True)
        assert serializer.is_valid(), serializer.errors

    def test_admin_valid_user_id(self, db, wb_laboratory, wb_lab_admin):
        data = {'admin': wb_lab_admin.id}
        serializer = LaboratoryUpdateSerializer(instance=wb_laboratory, data=data, partial=True)
        assert serializer.is_valid(), serializer.errors

    def test_note_none_should_pass(self, db, wb_laboratory):
        data = {'note': None}
        serializer = LaboratoryUpdateSerializer(instance=wb_laboratory, data=data, partial=True)
        assert serializer.is_valid(), serializer.errors

    def test_note_empty_string_should_pass(self, db, wb_laboratory):
        data = {'note': ''}
        serializer = LaboratoryUpdateSerializer(instance=wb_laboratory, data=data, partial=True)
        assert serializer.is_valid(), serializer.errors


class TestLaboratorySerializer:
    def test_includes_all_fields(self, db, wb_laboratory):
        serializer = LaboratorySerializer(wb_laboratory)
        data = serializer.data
        assert 'id' in data
        assert 'name' in data
        assert 'code' in data
        assert 'department_name' in data
        assert 'admin_name' in data
        assert 'status' in data

    def test_admin_name_display(self, db, wb_laboratory):
        serializer = LaboratorySerializer(wb_laboratory)
        assert serializer.data['admin_name'] == wb_laboratory.admin.nickname

    def test_department_name_display(self, db, wb_laboratory):
        serializer = LaboratorySerializer(wb_laboratory)
        assert serializer.data['department_name'] == wb_laboratory.department.name


class TestEquipmentCreateSerializer:
    def test_valid_data(self, db, wb_laboratory):
        data = {
            'name': '新设备',
            'code': 'SER_EQ_001',
            'category': 'COMPUTER',
            'laboratory': wb_laboratory.id,
        }
        serializer = EquipmentCreateSerializer(data=data)
        assert serializer.is_valid(), serializer.errors

    def test_empty_name(self, db):
        data = {'name': '', 'code': 'CODE001', 'laboratory': 1}
        serializer = EquipmentCreateSerializer(data=data)
        assert not serializer.is_valid()
        assert 'name' in serializer.errors

    def test_empty_code(self, db):
        data = {'name': '设备', 'code': '', 'laboratory': 1}
        serializer = EquipmentCreateSerializer(data=data)
        assert not serializer.is_valid()
        assert 'code' in serializer.errors


class TestEquipmentUpdateSerializer:
    def test_update_name(self, db, wb_equipment):
        data = {'name': '更新设备名'}
        serializer = EquipmentUpdateSerializer(instance=wb_equipment, data=data, partial=True)
        assert serializer.is_valid(), serializer.errors

    def test_update_status(self, db, wb_equipment):
        data = {'status': 'MAINTENANCE'}
        serializer = EquipmentUpdateSerializer(instance=wb_equipment, data=data, partial=True)
        assert serializer.is_valid(), serializer.errors


class TestEquipmentSerializer:
    def test_includes_laboratory_info(self, db, wb_equipment):
        serializer = EquipmentSerializer(wb_equipment)
        assert 'laboratory_name' in serializer.data
