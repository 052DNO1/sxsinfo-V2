"""
实训室序列化器单元测试

测试目标：
1. 验证字段验证逻辑是否正确
2. 测试边界情况（空值、无效值等）
3. 确保"未分配"状态能正确处理
4. 测试必填字段的验证

运行方式：pytest tests/unit/test_serializers/test_laboratory_serializer.py -v
"""

import pytest
from apps.laboratories.serializers.laboratory import (
    LaboratorySerializer,
    LaboratoryCreateSerializer,
    LaboratoryUpdateSerializer
)
from apps.laboratories.models import Laboratory
from apps.users.models import User


class TestLaboratoryUpdateSerializer:
    """实训室更新序列化器测试"""
    
    @pytest.fixture
    def lab_instance(self, test_laboratory):
        """获取测试用的实训室实例"""
        return test_laboratory
    
    @pytest.fixture
    def valid_user(self, lab_admin_user):
        """获取有效的管理员用户"""
        return lab_admin_user
    
    # ========== 基本功能测试 ==========
    
    def test_update_with_valid_data(self, lab_instance, valid_user):
        """测试使用有效数据更新实训室 - 应该通过"""
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
        assert serializer.validated_data['admin'] == valid_user.id
    
    def test_update_name_required(self, lab_instance):
        """测试名称为空时应该失败"""
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
        """测试编号为空时应该失败"""
        data = {
            'name': '测试',
            'code': '',
            'capacity': 30,
            'status': 1
        }
        
        serializer = LaboratoryUpdateSerializer(instance=lab_instance, data=data)
        assert not serializer.is_valid()
        assert 'code' in serializer.errors
    
    # ========== 管理员字段核心测试（关键！）==========
    
    def test_admin_none_should_pass(self, lab_instance):
        """
        测试 admin=None (未分配) - 应该通过
        
        这是修复 500 错误的核心测试！
        场景：前端发送 admin: null 表示取消管理员分配
        """
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
        """
        测试 admin=0 (未分配) - 应该通过
        
        这是修复 500 错误的核心测试！
        场景：前端下拉框选择"未分配"(value=0)
        """
        data = {
            'name': lab_instance.name,
            'code': lab_instance.code,
            'capacity': lab_instance.capacity,
            'status': lab_instance.status,
            'admin': 0,
            'note': None
        }
        
        serializer = LaboratoryUpdateSerializer(instance=lab_instance, data=data)
        assert serializer.is_valid(), f"admin=0 应该通过，但错误: {serializer.errors}"
        assert serializer.validated_data['admin'] is None
    
    def test_admin_empty_string_should_pass(self, lab_instance):
        """
        测试 admin='' (空字符串) - 应该通过
        
        边界情况：某些前端框架可能发送空字符串而非 null/0
        """
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
        """
        测试 admin='0' (字符串零) - 应该通过
        
        边界情况：前端可能将数字转为字符串传输
        """
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
        """测试有效的用户ID - 应该通过并返回用户ID"""
        data = {
            'name': lab_instance.name,
            'code': lab_instance.code,
            'capacity': lab_instance.capacity,
            'status': lab_instance.status,
            'admin': valid_user.id
        }
        
        serializer = LaboratoryUpdateSerializer(instance=lab_instance, data=data)
        assert serializer.is_valid(), f"有效用户ID应该通过，但错误: {serializer.errors}"
        assert serializer.validated_data['admin'] == valid_user.id
    
    def test_admin_invalid_user_id_should_fail(self, lab_instance):
        """测试无效的用户ID - 应该失败"""
        data = {
            'name': lab_instance.name,
            'code': lab_instance.code,
            'capacity': lab_instance.capacity,
            'status': lab_instance.status,
            'admin': 99999  # 不存在的用户ID
        }
        
        serializer = LaboratoryUpdateSerializer(instance=lab_instance, data=data)
        assert not serializer.is_valid()
        assert 'admin' in serializer.errors
    
    # ========== 备注字段测试 ==========
    
    def test_note_none_should_pass(self, lab_instance):
        """测试 note=None - 应该通过"""
        data = {
            'name': lab_instance.name,
            'code': lab_instance.code,
            'status': lab_instance.status,
            'note': None
        }
        
        serializer = LaboratoryUpdateSerializer(instance=lab_instance, data=data)
        assert serializer.is_valid(), f"note=None 应该通过，但错误: {serializer.errors}"
    
    def test_note_empty_string_should_pass(self, lab_instance):
        """测试 note='' - 应该通过"""
        data = {
            'name': lab_instance.name,
            'code': lab_instance.code,
            'status': lab_instance.status,
            'note': ''
        }
        
        serializer = LaboratoryUpdateSerializer(instance=lab_instance, data=data)
        assert serializer.is_valid(), f"note='' 应该通过，但错误: {serializer.errors}"
    
    def test_note_with_content(self, lab_instance):
        """测试有内容的备注 - 应该通过"""
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
    """实训室创建序列化器测试"""
    
    @pytest.fixture
    def department(self, test_department):
        return test_department
    
    @pytest.fixture
    def admin_user(self, lab_admin_user):
        return lab_admin_user
    
    def test_create_with_valid_data(self, department, admin_user):
        """测试使用有效数据创建实训室"""
        data = {
            'name': '新实训室',
            'code': 'NEW_LAB_001',
            'building': '主楼',
            'floor': 5,
            'room_number': '501',
            'capacity': 40,
            'laboratory_type': 'COMPUTER',
            'department': department.id,
            'admin': admin_user.id,
            'description': '测试创建'
        }
        
        serializer = LaboratoryCreateSerializer(data=data)
        assert serializer.is_valid(), f"验证应该通过，但错误: {serializer.errors}"
        
        lab = serializer.save()
        assert lab.name == '新实训室'
        assert lab.code == 'NEW_LAB_001'
        assert lab.admin == admin_user
    
    def test_create_name_required(self, department):
        """测试创建时名称必填"""
        data = {
            'name': '',
            'code': 'TEST_001',
            'department': department.id
        }
        
        serializer = LaboratoryCreateSerializer(data=data)
        assert not serializer.is_valid()
        assert 'name' in serializer.errors
    
    def test_create_code_required(self, department):
        """测试创建时编号必填"""
        data = {
            'name': '测试',
            'code': '',
            'department': department.id
        }
        
        serializer = LaboratoryCreateSerializer(data=data)
        assert not serializer.is_valid()
        assert 'code' in serializer.errors


class TestLaboratorySerializer:
    """实训室序列化器测试（用于API响应）"""
    
    def test_serialization_includes_all_fields(self, test_laboratory):
        """测试序列化包含所有必要字段"""
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
        """测试管理员名称的正确显示"""
        serializer = LaboratorySerializer(test_laboratory)
        data = serializer.data
        
        assert data['admin_name'] == lab_admin_user.nickname
    
    def test_department_name_display(self, test_laboratory, test_department):
        """测试分院名称的正确显示"""
        serializer = LaboratorySerializer(test_laboratory)
        data = serializer.data
        
        assert data['department_name'] == test_department.name
