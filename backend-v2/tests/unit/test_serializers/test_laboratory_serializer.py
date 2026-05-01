import pytest
from apps.laboratories.serializers.laboratory import (
    LaboratorySerializer,
    LaboratoryCreateSerializer,
    LaboratoryUpdateSerializer
)
from apps.laboratories.models import Laboratory
from apps.users.models import User


class TestLaboratoryUpdateSerializer:

    @pytest.fixture
    def lab_instance(self, test_laboratory):
        return test_laboratory

    @pytest.fixture
    def valid_user(self, lab_admin_user):
        return lab_admin_user

    def test_update_with_valid_data(self, lab_instance, valid_user):
        data = {
            'name': '更新后的实训室',
            'code': lab_instance.code,
            'capacity': 40,
            'status': 1,
            'admin': valid_user.id,
            'note': '更新备注'
        }
        serializer = LaboratoryUpdateSerializer(instance=lab_instance, data=data)
        assert serializer.is_valid(), f"验证应该通过，但错误: {serializer.errors}"
        assert serializer.validated_data['name'] == '更新后的实训室'

    def test_update_name_required(self, lab_instance):
        data = {
            'name': '',
            'code': lab_instance.code,
            'capacity': 30,
            'status': 1
        }
        serializer = LaboratoryUpdateSerializer(instance=lab_instance, data=data)
        assert not serializer.is_valid()
        assert 'name' in serializer.errors

    def test_update_code_required(self, lab_instance):
        data = {
            'name': '测试',
            'code': '',
            'capacity': 30,
            'status': 1
        }
        serializer = LaboratoryUpdateSerializer(instance=lab_instance, data=data)
        assert not serializer.is_valid()
        assert 'code' in serializer.errors

    def test_admin_none_should_pass(self, lab_instance):
        data = {
            'name': lab_instance.name,
            'code': lab_instance.code,
            'capacity': lab_instance.capacity,
            'status': lab_instance.status,
            'admin': None,
            'note': ''
        }
        serializer = LaboratoryUpdateSerializer(instance=lab_instance, data=data)
        assert serializer.is_valid(), f"admin=None 应该通过，但错误: {serializer.errors}"
        assert serializer.validated_data['admin'] is None

    def test_admin_zero_should_pass(self, lab_instance):
        data = {
            'name': lab_instance.name,
            'code': lab_instance.code,
            'capacity': lab_instance.capacity,
            'status': lab_instance.status,
            'admin': 0,
            'note': ''
        }
        serializer = LaboratoryUpdateSerializer(instance=lab_instance, data=data)
        assert serializer.is_valid(), f"admin=0 应该通过，但错误: {serializer.errors}"
        assert serializer.validated_data['admin'] is None

    def test_admin_empty_string_should_pass(self, lab_instance):
        data = {
            'name': lab_instance.name,
            'code': lab_instance.code,
            'capacity': lab_instance.capacity,
            'status': lab_instance.status,
            'admin': '',
            'note': '测试'
        }
        serializer = LaboratoryUpdateSerializer(instance=lab_instance, data=data)
        assert serializer.is_valid(), f"admin='' 应该通过，但错误: {serializer.errors}"
        assert serializer.validated_data['admin'] is None

    def test_admin_string_zero_should_pass(self, lab_instance):
        data = {
            'name': lab_instance.name,
            'code': lab_instance.code,
            'capacity': lab_instance.capacity,
            'status': lab_instance.status,
            'admin': '0',
            'note': ''
        }
        serializer = LaboratoryUpdateSerializer(instance=lab_instance, data=data)
        assert serializer.is_valid(), f"admin='0' 应该通过，但错误: {serializer.errors}"
        assert serializer.validated_data['admin'] is None

    def test_admin_valid_user_id(self, lab_instance, valid_user):
        data = {
            'name': lab_instance.name,
            'code': lab_instance.code,
            'capacity': lab_instance.capacity,
            'status': lab_instance.status,
            'admin': valid_user.id
        }
        serializer = LaboratoryUpdateSerializer(instance=lab_instance, data=data)
        assert serializer.is_valid(), f"有效用户ID应该通过，但错误: {serializer.errors}"

    def test_admin_invalid_user_id_should_fail(self, lab_instance):
        data = {
            'name': lab_instance.name,
            'code': lab_instance.code,
            'capacity': lab_instance.capacity,
            'status': lab_instance.status,
            'admin': 99999
        }
        serializer = LaboratoryUpdateSerializer(instance=lab_instance, data=data)
        assert not serializer.is_valid()
        assert 'admin' in serializer.errors

    def test_note_none_should_pass(self, lab_instance):
        data = {
            'name': lab_instance.name,
            'code': lab_instance.code,
            'status': lab_instance.status,
            'note': None
        }
        serializer = LaboratoryUpdateSerializer(instance=lab_instance, data=data)
        assert serializer.is_valid(), f"note=None 应该通过，但错误: {serializer.errors}"

    def test_note_empty_string_should_pass(self, lab_instance):
        data = {
            'name': lab_instance.name,
            'code': lab_instance.code,
            'status': lab_instance.status,
            'note': ''
        }
        serializer = LaboratoryUpdateSerializer(instance=lab_instance, data=data)
        assert serializer.is_valid(), f"note='' 应该通过，但错误: {serializer.errors}"

    def test_note_with_content(self, lab_instance):
        data = {
            'name': lab_instance.name,
            'code': lab_instance.code,
            'status': lab_instance.status,
            'note': '这是一条测试备注'
        }
        serializer = LaboratoryUpdateSerializer(instance=lab_instance, data=data)
        assert serializer.is_valid()
        assert serializer.validated_data['note'] == '这是一条测试备注'


class TestLaboratoryCreateSerializer:

    @pytest.fixture
    def department(self, test_department):
        return test_department

    @pytest.fixture
    def admin_user(self, lab_admin_user):
        return lab_admin_user

    def test_create_with_valid_data(self, department, admin_user):
        data = {
            'name': '新实训室',
            'code': 'NEW_LAB_001',
            'building': '主楼',
            'floor': 5,
            'room_number': '501',
            'capacity': 40,
            'laboratory_type': 'COMPUTER',
            'department': department.id,
            'description': '测试创建'
        }
        serializer = LaboratoryCreateSerializer(data=data)
        assert serializer.is_valid(), f"验证应该通过，但错误: {serializer.errors}"

    def test_create_name_required(self, department):
        data = {
            'name': '',
            'code': 'TEST_001',
            'department': department.id
        }
        serializer = LaboratoryCreateSerializer(data=data)
        assert not serializer.is_valid()
        assert 'name' in serializer.errors

    def test_create_code_required(self, department):
        data = {
            'name': '测试',
            'code': '',
            'department': department.id
        }
        serializer = LaboratoryCreateSerializer(data=data)
        assert not serializer.is_valid()
        assert 'code' in serializer.errors


class TestLaboratorySerializer:

    def test_serialization_includes_all_fields(self, test_laboratory):
        serializer = LaboratorySerializer(test_laboratory)
        data = serializer.data
        expected_fields = [
            'id', 'name', 'code', 'building', 'floor', 'room_number',
            'location', 'capacity', 'area', 'laboratory_type',
            'department', 'department_name', 'admin', 'admin_name',
            'status', 'status_display', 'is_available', 'facilities',
            'description', 'note', 'equipment_count', 'schedule_count',
            'created_at', 'updated_at'
        ]
        for field in expected_fields:
            assert field in data, f"缺少字段: {field}"

    def test_admin_name_display(self, test_laboratory, lab_admin_user):
        serializer = LaboratorySerializer(test_laboratory)
        data = serializer.data
        assert data['admin_name'] == lab_admin_user.nickname

    def test_department_name_display(self, test_laboratory, test_department):
        serializer = LaboratorySerializer(test_laboratory)
        data = serializer.data
        assert data['department_name'] == test_department.name
