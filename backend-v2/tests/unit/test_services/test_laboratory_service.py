"""
实训室服务层单元测试

测试目标：
1. CRUD 操作的正确性
2. 权限控制（不同角色的访问范围）
3. 数据格式化（列表返回格式、分页等）
4. 边界情况处理

运行方式：pytest tests/unit/test_services/test_laboratory_service.py -v
"""

import pytest
from apps.laboratories.services.laboratory_service import LaboratoryService
from apps.laboratories.models import Laboratory
from apps.users.models import User


class TestLaboratoryServiceCRUD:
    """实训室 CRUD 操作测试"""
    
    @pytest.fixture
    def service(self):
        """创建服务实例"""
        return LaboratoryService()
    
    # ========== 创建操作测试 ==========
    
    def test_create_laboratory_success(self, service, super_admin_user, test_department):
        """测试成功创建实训室"""
        lab_data = service.create_laboratory(
            requester=super_admin_user,
            name='新实训室',
            code='SERVICE_TEST_001',
            building='测试楼',
            floor=2,
            room_number='201',
            capacity=35,
            laboratory_type='COMPUTER',
            department_id=test_department.id,
            description='通过服务层创建'
        )
        
        assert lab_data is not None
        assert lab_data['name'] == '新实训室'
        assert lab_data['code'] == 'SERVICE_TEST_001'
        
        # 验证数据库中确实创建了
        lab = Laboratory.objects.get(code='SERVICE_TEST_001')
        assert lab.name == '新实训室'
    
    def test_create_duplicate_code_should_fail(self, service, super_admin_user, test_department, test_laboratory):
        """测试重复编号应该失败"""
        with pytest.raises(Exception):  # 应该抛出验证错误或数据库唯一约束异常
            service.create_laboratory(
                requester=super_admin_user,
                name='重复编号',
                code=test_laboratory.code,  # 使用已存在的编号
                building='测试楼',
                floor=1,
                room_number='101',
                capacity=20,
                laboratory_type='COMPUTER',
                department_id=test_department.id
            )
    
    # ========== 更新操作测试 ==========
    
    def test_update_laboratory_success(self, service, super_admin_user, test_laboratory):
        """测试成功更新实训室"""
        result = service.update_laboratory(
            requester=super_admin_user,
            laboratory_id=test_laboratory.id,
            name='更新后的名称',
            capacity=50
        )
        
        assert result is not None
        assert result.name == '更新后的名称'
        assert result.capacity == 50
        
        # 刷新并验证
        test_laboratory.refresh_from_db()
        assert test_laboratory.name == '更新后的名称'
    
    def test_update_laboratory_set_admin_to_none(self, service, super_admin_user, test_laboratory, lab_admin_user):
        """
        测试将管理员设置为 None (未分配)
        
        这是修复 500 错误的核心业务逻辑测试！
        场景：分院管理员取消实训室的管理员分配
        """
        # 确认当前有管理员
        assert test_laboratory.admin is not None
        
        # 执行更新，将 admin 设为 None
        result = service.update_laboratory(
            requester=super_admin_user,
            laboratory_id=test_laboratory.id,
            admin=None  # 关键！设置为未分配
        )
        
        assert result is not None
        assert result.admin is None
        
        # 验证数据库
        test_laboratory.refresh_from_db()
        assert test_laboratory.admin is None
    
    def test_update_laboratory_change_admin(self, service, super_admin_user, test_laboratory):
        """测试更换管理员"""
        # 创建一个新管理员
        new_admin = User.objects.create_user(
            username='new_lab_admin',
            password='test123456',
            nickname='新管理员',
            role=2,
            is_active=True
        )
        
        result = service.update_laboratory(
            requester=super_admin_user,
            laboratory_id=test_laboratory.id,
            admin=new_admin.id
        )
        
        assert result.admin == new_admin
    
    def test_update_nonexistent_laboratory_should_fail(self, service, super_admin_user):
        """测试更新不存在的实训室应该失败"""
        with pytest.raises(Exception):
            service.update_laboratory(
                requester=super_admin_user,
                laboratory_id=99999,  # 不存在的ID
                name='不存在'
            )
    
    # ========== 查询操作测试 ==========
    
    def test_get_laboratory_list_pagination(self, service, super_admin_user, test_laboratory):
        """测试获取实训室列表（分页格式）"""
        result = service.get_laboratory_list(
            requester=super_admin_user,
            page=1,
            page_size=10
        )
        
        assert 'pagination' in result
        assert 'items' in result or 'results' in result or 'data' in result
        assert result['pagination']['total'] >= 1
    
    def test_get_laboratory_detail(self, service, super_admin_user, test_laboratory):
        """测试获取实训室详情"""
        result = service.get_laboratory_detail(
            requester=super_admin_user,
            laboratory_id=test_laboratory.id
        )
        
        assert result is not None
        assert result['id'] == test_laboratory.id
        assert result['name'] == test_laboratory.name
    
    # ========== 删除操作测试 ==========
    
    def test_delete_laboratory_success(self, service, super_admin_user, test_department):
        """测试软删除实训室"""
        # 先创建一个待删除的实训室
        lab = Laboratory.objects.create(
            name='待删除的实训室',
            code='TO_DELETE_001',
            building='测试楼',
            floor=1,
            room_number='101',
            capacity=20,
            laboratory_type='COMPUTER',
            department=test_department,
            status=1
        )
        
        lab_id = lab.id
        
        # 执行删除
        result = service.delete_laboratory(
            requester=super_admin_user,
            laboratory_id=lab_id
        )
        
        assert result is True
        
        # 验证软删除（is_deleted=True）
        lab.refresh_from_db()
        assert lab.is_deleted is True
    
    def test_delete_nonexistent_laboratory_should_fail(self, service, super_admin_user):
        """测试删除不存在的实训室应该失败"""
        with pytest.raises(Exception):
            service.delete_laboratory(
                requester=super_admin_user,
                laboratory_id=99999
            )


class TestLaboratoryServicePermissions:
    """权限控制测试"""
    
    @pytest.fixture
    def service(self):
        return LaboratoryService()
    
    def test_super_admin_can_access_all_labs(self, service, super_admin_user, test_laboratory):
        """测试管理员-校长可以访问所有实训室"""
        result = service.get_laboratory_list(requester=super_admin_user)
        assert result['pagination']['total'] >= 1
    
    def test_department_admin_can_only_access_own_dept(self, service, department_admin_user, test_laboratory):
        """测试分院管理员只能访问自己分院的实训室"""
        # 将测试实训室分配到分院管理员的部门
        test_laboratory.department = department_admin_user.department
        test_laboratory.save()
        
        result = service.get_laboratory_list(requester=department_admin_user)
        
        for lab in result.get('items', result.get('results', [])):
            if isinstance(lab, dict):
                assert lab['department'] == department_admin_user.department.id
            else:
                assert lab.department == department_admin_user.department
    
    def test_lab_admin_can_only_access_own_labs(self, service, lab_admin_user, test_laboratory):
        """测试实训室管理员只能访问自己管理的实训室"""
        test_laboratory.admin = lab_admin_user
        test_laboratory.save()
        
        result = service.get_laboratory_list(requester=lab_admin_user)
        
        for lab in result.get('items', result.get('results', [])):
            if isinstance(lab, dict):
                assert lab['admin'] == lab_admin_user.id
            else:
                assert lab.admin == lab_admin_user


class TestLaboratoryServiceFormatting:
    """数据格式化测试"""
    
    @pytest.fixture
    def service(self):
        return LaboratoryService()
    
    def test_format_includes_status_display(self, service, test_laboratory):
        """测试格式化数据包含状态显示文本"""
        detail = service.get_laboratory_detail(
            requester=User.objects.filter(is_superuser=True).first(),
            laboratory_id=test_laboratory.id
        )
        
        assert 'status_display' in detail
        assert detail['status_display'] in ['可用', '使用中', '维护中', '不可用']
    
    def test_format_includes_schedule_count(self, service, test_laboratory):
        """测试格式化数据包含课程数统计"""
        detail = service.get_laboratory_detail(
            requester=User.objects.filter(is_superuser=True).first(),
            laboratory_id=test_laboratory.id
        )
        
        assert 'schedule_count' in detail
        assert isinstance(detail['schedule_count'], int)
    
    def test_format_handles_none_note(self, service, test_laboratory):
        """测试备注为 None 时正确处理"""
        test_laboratory.note = None
        test_laboratory.save()
        
        detail = service.get_laboratory_detail(
            requester=User.objects.filter(is_superuser=True).first(),
            laboratory_id=test_laboratory.id
        )
        
        # note 应该是空字符串或 None，不能报错
        assert 'note' in detail
