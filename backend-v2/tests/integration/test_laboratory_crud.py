"""
实训室集成测试

测试目标：
1. 完整的 CRUD 工作流（创建→查询→更新→删除）
2. 多个组件协作（Serializer + Service + Model）
3. 真实业务场景模拟
4. 数据一致性验证

运行方式：pytest tests/integration/test_laboratory_crud.py -v
"""

import pytest
from apps.laboratories.services.laboratory_service import LaboratoryService
from apps.laboratories.models import Laboratory
from apps.users.models import User


class TestLaboratoryFullCRUDWorkflow:
    """实训室完整 CRUD 工作流测试"""
    
    @pytest.fixture
    def service(self):
        return LaboratoryService()
    
    def test_complete_create_read_update_delete_workflow(
        self, service, super_admin_user, test_department, lab_admin_user
    ):
        """
        测试完整的生命周期：创建 → 读取 → 更新 → 删除
        
        这是最重要的集成测试！确保整个流程没有问题
        """
        
        # ========== Step 1: 创建 ==========
        lab_data = service.create_laboratory(
            requester=super_admin_user,
            name='集成测试实训室',
            code='INT_TEST_001',
            building='主楼',
            floor=3,
            room_number='301',
            capacity=40,
            laboratory_type='COMPUTER',
            department_id=test_department.id,
            admin_id=lab_admin_user.id,
            description='用于集成测试'
        )
        
        assert lab_data is not None
        lab_id = lab_data['id']
        
        # 验证创建成功
        lab = Laboratory.objects.get(id=lab_id)
        assert lab.is_deleted is False
        assert lab.name == '集成测试实训室'
        assert lab.admin == lab_admin_user
        
        # ========== Step 2: 读取 ==========
        detail = service.get_laboratory_detail(
            requester=super_admin_user,
            laboratory_id=lab_id
        )
        
        assert detail['id'] == lab_id
        assert detail['name'] == '集成测试实训室'
        assert detail['code'] == 'INT_TEST_001'
        assert detail['admin_name'] == lab_admin_user.nickname
        
        # ========== Step 3: 更新（包括取消管理员分配）==========
        updated_lab = service.update_laboratory(
            requester=super_admin_user,
            laboratory_id=lab_id,
            name='更新后的名称',
            capacity=50,
            admin=None,  # 关键：取消管理员分配！
            note='更新备注'
        )
        
        assert updated_lab.name == '更新后的名称'
        assert updated_lab.capacity == 50
        assert updated_lab.admin is None  # 验证管理员已取消
        
        # 再次读取验证
        detail_after_update = service.get_laboratory_detail(
            requester=super_admin_user,
            laboratory_id=lab_id
        )
        
        assert detail_after_update['name'] == '更新后的名称'
        assert detail_after_update['admin_name'] is None or detail_after_update['admin_name'] == ''
        
        # ========== Step 4: 重新分配管理员 ==========
        updated_lab2 = service.update_laboratory(
            requester=super_admin_user,
            laboratory_id=lab_id,
            admin=lab_admin_user.id  # 重新分配
        )
        
        assert updated_lab2.admin == lab_admin_user
        
        # ========== Step 5: 删除 ==========
        delete_result = service.delete_laboratory(
            requester=super_admin_user,
            laboratory_id=lab_id
        )
        
        assert delete_result is True
        
        # 验证软删除
        lab.refresh_from_db()
        assert lab.is_deleted is True
        
        # 验证删除后无法读取
        with pytest.raises(Exception):
            service.get_laboratory_detail(
                requester=super_admin_user,
                laboratory_id=lab_id
            )


class TestLaboratoryAdminAssignmentScenarios:
    """管理员分配场景测试"""
    
    @pytest.fixture
    def service(self):
        return LaboratoryService()
    
    def test_assign_admin_to_unassigned_lab(
        self, service, super_admin_user, test_department, lab_admin_user
    ):
        """测试为未分配管理员的实训室分配管理员"""
        # 创建无管理员的实训室
        lab = Laboratory.objects.create(
            name='无管理员实训室',
            code='NO_ADMIN_LAB',
            building='测试楼',
            floor=1,
            room_number='101',
            capacity=30,
            laboratory_type='COMPUTER',
            department=test_department,
            admin=None,  # 无管理员
            status=1
        )
        
        # 分配管理员
        result = service.update_laboratory(
            requester=super_admin_user,
            laboratory_id=lab.id,
            admin=lab_admin_user.id
        )
        
        assert result.admin == lab_admin_user
        lab.refresh_from_db()
        assert lab.admin == lab_admin_user
    
    def test_reassign_admin_to_different_user(
        self, service, super_admin_user, test_laboratory
    ):
        """测试将管理员更换为另一个用户"""
        original_admin = test_laboratory.admin
        
        # 创建新管理员
        new_admin = User.objects.create_user(
            username='replacement_admin',
            password='test123456',
            nickname='替换管理员',
            role=2,
            is_active=True
        )
        
        # 更换管理员
        result = service.update_laboratory(
            requester=super_admin_user,
            laboratory_id=test_laboratory.id,
            admin=new_admin.id
        )
        
        assert result.admin == new_admin
        assert result.admin != original_admin
    
    def test_batch_operations_consistency(
        self, service, super_admin_user, test_department
    ):
        """测试批量操作的数据一致性"""
        labs = []
        
        # 批量创建 5 个实训室
        for i in range(5):
            lab_data = service.create_laboratory(
                requester=super_admin_user,
                name=f'批量测试实训室_{i}',
                code=f'BATCH_{i:03d}',
                building='批量楼',
                floor=i+1,
                room_number=f'{i+01}01',
                capacity=30+i*5,
                laboratory_type='COMPUTER',
                department_id=test_department.id
            )
            labs.append(lab_data)
        
        # 查询列表验证数量
        list_result = service.get_laboratory_list(
            requester=super_admin_user,
            page=1,
            page_size=20
        )
        
        assert list_result['pagination']['total'] >= 5
        
        # 批量更新
        for lab_data in labs:
            service.update_laboratory(
                requester=super_admin_user,
                laboratory_id=lab_data['id'],
                note=f'批量更新备注_{lab_data["id"]}'
            )
        
        # 验证所有更新都成功
        for lab_data in labs:
            detail = service.get_laboratory_detail(
                requester=super_admin_user,
                laboratory_id=lab_data['id']
            )
            assert f'批量更新备注_{lab_data["id"]}' in detail.get('note', '')


class TestLaboratoryEdgeCases:
    """边界情况集成测试"""
    
    @pytest.fixture
    def service(self):
        return LaboratoryService()
    
    def test_concurrent_updates(self, service, super_admin_user, test_laboratory):
        """测试并发更新场景"""
        # 模拟两次快速连续更新
        result1 = service.update_laboratory(
            requester=super_admin_user,
            laboratory_id=test_laboratory.id,
            name='第一次更新'
        )
        
        result2 = service.update_laboratory(
            requester=super_admin_user,
            laboratory_id=test_laboratory.id,
            capacity=100
        )
        
        # 最终状态应该包含两次更新的内容
        test_laboratory.refresh_from_db()
        assert test_laboratory.name == '第一次更新'
        assert test_laboratory.capacity == 100
    
    def test_unicode_and_special_characters(
        self, service, super_admin_user, test_department
    ):
        """测试 Unicode 和特殊字符处理"""
        lab_data = service.create_laboratory(
            requester=super_admin_user,
            name='中文实训室名称 🎓',
            code='UNICODE_001',
            building='测试楼 αβγ',
            floor=1,
            room_number='101',
            capacity=30,
            laboratory_type='COMPUTER',
            department_id=test_department.id,
            description='特殊字符测试：<>&"\''
        )
        
        assert lab_data is not None
        assert '🎓' in lab_data['name']
        
        # 读取并验证
        detail = service.get_laboratory_detail(
            requester=super_admin_user,
            laboratory_id=lab_data['id']
        )
        
        assert detail['name'] == '中文实训室名称 🎓'
