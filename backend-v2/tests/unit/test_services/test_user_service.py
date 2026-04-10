"""
用户管理相关测试

测试目标：
1. 用户列表查询和过滤
2. 用户状态切换（启用/禁用）
3. 权限验证
4. 角色过滤

运行方式：pytest tests/unit/test_services/test_user_service.py -v
"""

import pytest
from apps.users.services.user_service import UserService
from apps.users.models import User


class TestUserServiceQueries:
    """用户查询服务测试"""
    
    @pytest.fixture
    def service(self):
        return UserService()
    
    def test_get_user_list_default_filter(self, service, super_admin_user, teacher_user, lab_admin_user):
        """
        测试默认过滤：只显示教师和实训室管理员 (role=1,2)
        
        这对应前端需求：用户列表只显示教师和实训室管理员
        """
        result = service.get_user_list(
            requester=super_admin_user,
            params={'role': '1,2'}  # 前端发送的参数格式
        )
        
        users = result.get('items', result.get('results', []))
        
        # 验证返回的用户角色只有 1（教师）或 2（实训室管理员）
        for user in users:
            if isinstance(user, dict):
                assert user['role'] in [1, 2], f"角色 {user['role']} 不在允许范围内"
            else:
                assert user.role in [1, 2]
    
    def test_get_user_list_with_role_filter(self, service, super_admin_user):
        """测试按角色过滤"""
        # 只获取教师
        result = service.get_user_list(
            requester=super_admin_user,
            params={'role': '1'}
        )
        
        users = result.get('items', result.get('results', []))
        for user in users:
            if isinstance(user, dict):
                assert user['role'] == 1
    
    def test_get_user_list_pagination_format(self, service, super_admin_user, teacher_user):
        """测试分页格式正确性"""
        result = service.get_user_list(
            requester=super_admin_user,
            params={'role': '1,2'},
            page=1,
            page_size=10
        )
        
        assert 'pagination' in result
        pagination = result['pagination']
        
        assert 'total' in pagination
        assert 'page' in pagination
        assert 'page_size' in pagination
        assert pagination['total'] >= 1
    
    def test_get_user_includes_managed_laboratories(
        self, service, super_admin_user, lab_admin_user, test_laboratory
    ):
        """测试用户列表包含"管理的实训室"字段"""
        # 确保实训室管理员有管理的实训室
        test_laboratory.admin = lab_admin_user
        test_laboratory.save()
        
        result = service.get_user_list(
            requester=super_admin_user,
            params={'role': '1,2'}
        )
        
        users = result.get('items', result.get('results', []))
        
        # 查找实训室管理员
        lab_admin_found = None
        for user in users:
            if isinstance(user, dict):
                if user['id'] == lab_admin_user.id:
                    lab_admin_found = user
                    break
        
        if lab_admin_found:
            assert 'managed_laboratories' in lab_admin_found
            assert isinstance(lab_admin_found['managed_laboratories'], list)


class TestUserStatusToggle:
    """用户状态切换测试"""
    
    @pytest.fixture
    def service(self):
        return UserService()
    
    def test_toggle_user_status_active_to_inactive(
        self, service, super_admin_user, teacher_user
    ):
        """测试将用户从激活状态切换到禁用状态"""
        assert teacher_user.is_active is True
        
        result = service.toggle_user_status(
            requester=super_admin_user,
            user_id=teacher_user.id
        )
        
        assert result is not None
        teacher_user.refresh_from_db()
        assert teacher_user.is_active is False
    
    def test_toggle_user_status_inactive_to_active(
        self, service, super_admin_user, teacher_user
    ):
        """测试将用户从禁用状态切换到激活状态"""
        # 先禁用
        teacher_user.is_active = False
        teacher_user.save()
        
        # 切换回激活
        result = service.toggle_user_status(
            requester=super_admin_user,
            user_id=teacher_user.id
        )
        
        teacher_user.refresh_from_db()
        assert teacher_user.is_active is True


class TestUserRoleDisplay:
    """用户角色显示测试"""
    
    @pytest.fixture
    def service(self):
        return UserService()
    
    def test_system_admin_role_display(self, service, system_admin_user):
        """测试系统管理员角色显示"""
        detail = service.get_user_detail(
            requester=system_admin_user,
            user_id=system_admin_user.id
        )
        
        assert 'role_display' in detail or 'role_name' in detail
    
    def test_super_admin_role_display(self, service, super_admin_user):
        """测试管理员-校长角色显示"""
        detail = service.get_user_detail(
            requester=super_admin_user,
            user_id=super_admin_user.id
        )
        
        assert detail is not None
    
    def test_department_admin_role_display(self, service, department_admin_user):
        """测试分院管理员角色显示"""
        detail = service.get_user_detail(
            requester=department_admin_user,
            user_id=department_admin_user.id
        )
        
        assert detail is not None
