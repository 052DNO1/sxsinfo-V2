"""
实训室 API 端到端测试

测试目标：
1. 模拟真实的 HTTP 请求/响应
2. 测试 API 接口的完整流程
3. 验证权限控制（认证、授权）
4. 测试错误处理和异常响应

运行方式：pytest tests/e2e/test_laboratory_api.py -v
"""

import pytest
import json
from django.test import Client
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token


class TestLaboratoryAPIEndpoints:
    """实训室 API 端点测试"""
    
    @pytest.fixture
    def api_client(self):
        """创建 API 测试客户端"""
        return APIClient()
    
    @pytest.fixture
    def authenticated_client(self, api_client, super_admin_user):
        """创建已认证的客户端"""
        token, _ = Token.objects.get_or_create(user=super_admin_user)
        api_client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        return api_client
    
    # ========== 列表 API 测试 ==========
    
    def test_get_laboratory_list_success(self, authenticated_client, test_laboratory):
        """测试获取实训室列表 - 成功"""
        response = authenticated_client.get('/api/laboratories/')
        
        assert response.status_code == 200
        data = response.json()
        
        assert 'pagination' in data or 'results' in data or 'data' in data
        assert len(data.get('items', data.get('results', []))) >= 1
    
    def test_get_laboratory_list_with_pagination(self, authenticated_client):
        """测试分页参数"""
        response = authenticated_client.get('/api/laboratories/?page=1&page_size=10')
        
        assert response.status_code == 200
        data = response.json()
        
        if 'pagination' in data:
            assert 'total' in data['pagination']
            assert 'page' in data['pagination']
            assert 'page_size' in data['pagination']
    
    # ========== 详情 API 测试 ==========
    
    def test_get_laboratory_detail_success(self, authenticated_client, test_laboratory):
        """测试获取实训室详情 - 成功"""
        response = authenticated_client.get(f'/api/laboratories/{test_laboratory.id}/')
        
        assert response.status_code == 200
        data = response.json()
        
        assert data['id'] == test_laboratory.id
        assert data['name'] == test_laboratory.name
        assert 'admin_name' in data
        assert 'department_name' in data
    
    def test_get_laboratory_detail_not_found(self, authenticated_client):
        """测试获取不存在的实训室 - 404"""
        response = authenticated_client.get('/api/laboratories/99999/')
        
        assert response.status_code == 404
    
    # ========== 创建 API 测试 ==========
    
    def test_create_laboratory_success(self, authenticated_client, test_department, lab_admin_user):
        """测试创建实训室 - 成功"""
        data = {
            'name': 'API测试实训室',
            'code': 'API_TEST_001',
            'building': 'API楼',
            floor: 2,
            room_number: '201',
            capacity: 35,
            'laboratory_type': 'COMPUTER',
            'department': test_department.id,
            'admin': lab_admin_user.id,
            'description': '通过API创建'
        }
        
        response = authenticated_client.post('/api/laboratories/', data, format='json')
        
        assert response.status_code == 201
        result = response.json()
        
        assert result['name'] == 'API测试实训室'
        assert result['code'] == 'API_TEST_001'
        assert 'id' in result
    
    def test_create_laboratory_missing_required_field(self, authenticated_client):
        """测试创建时缺少必填字段 - 400"""
        data = {
            'name': '',  # 空名称
            'code': ''   # 空编号
        }
        
        response = authenticated_client.post('/api/laboratories/', data, format='json')
        
        assert response.status_code == 400
        errors = response.json()
        
        assert 'name' in errors or 'code' in errors
    
    # ========== 更新 API 测试（核心！）==========
    
    def test_update_laboratory_success(self, authenticated_client, test_laboratory):
        """测试更新实训室 - 成功"""
        data = {
            'name': 'API更新的名称',
            'capacity': 60,
            'note': '通过API更新'
        }
        
        response = authenticated_client.put(
            f'/api/laboratories/{test_laboratory.id}/',
            data,
            format='json'
        )
        
        assert response.status_code == 200
        result = response.json()
        
        assert result['name'] == 'API更新的名称'
        assert result['capacity'] == 60
    
    def test_update_laboratory_set_admin_to_none(
        self, authenticated_client, test_laboratory
    ):
        """
        测试通过 API 将管理员设置为 None (未分配)
        
        这是修复 500 错误的最终验证！
        完全模拟前端的真实操作
        """
        # 前端发送的数据格式（完全模拟）
        update_data = {
            'name': test_laboratory.name,
            'code': test_laboratory.code,
            'building': test_laboratory.building,
            'floor': test_laboratory.floor,
            'room_number': test_laboratory.room_number,
            'capacity': test_laboratory.capacity,
            'status': test_laboratory.status,
            'admin': None,  # 关键！前端选择"未分配"
            'note': ''
        }
        
        # 发送 PUT 请求（完全模拟前端操作）
        response = authenticated_client.put(
            f'/api/laboratories/{test_laboratory.id}/',
            update_data,
            format='json'
        )
        
        # 断言：不应该再是 500 错误了！
        assert response.status_code == 200, f"期望200，实际{response.status_code}，响应：{response.content}"
        
        result = response.json()
        assert result['admin'] is None or result.get('admin_name') in [None, '', '未分配']
    
    def test_update_laboratory_set_admin_to_zero(
        self, authenticated_client, test_laboratory
    ):
        """
        测试通过 API 发送 admin=0 (未分配的另一种形式)
        """
        update_data = {
            'name': test_laboratory.name,
            'code': test_laboratory.code,
            'capacity': test_laboratory.capacity,
            'status': test_laboratory.status,
            'admin': 0,  # 前端可能发送 0 而不是 None
            'note': None
        }
        
        response = authenticated_client.put(
            f'/api/laboratories/{test_laboratory.id}/',
            update_data,
            format='json'
        )
        
        # 应该成功，不再是 500 错误！
        assert response.status_code == 200, f"期望200，实际{response.status_code}，错误：{response.json()}"
    
    def test_update_laboratory_invalid_admin_id(
        self, authenticated_client, test_laboratory
    ):
        """测试发送无效的管理员ID - 应该返回400而非500"""
        update_data = {
            'name': test_laboratory.name,
            'code': test_laboratory.code,
            'admin': 99999  # 无效的用户ID
        }
        
        response = authenticated_client.put(
            f'/api/laboratories/{test_laboratory.id}/',
            update_data,
            format='json'
        )
        
        # 应该是 400（验证错误），而不是 500（服务器错误）
        assert response.status_code == 400
        errors = response.json()
        assert 'admin' in errors
    
    # ========== 删除 API 测试 ==========
    
    def test_delete_laboratory_success(self, authenticated_client, test_department):
        """测试删除实训室 - 成功"""
        from apps.laboratories.models import Laboratory
        
        # 先创建一个待删除的
        lab = Laboratory.objects.create(
            name='待删除API',
            code='DEL_API_001',
            building='测试楼',
            floor=1,
            room_number='101',
            capacity=20,
            laboratory_type='COMPUTER',
            department=test_department,
            status=1
        )
        
        response = authenticated_client.delete(f'/api/laboratories/{lab.id}/')
        
        assert response.status_code == 200 or response.status_code == 204
    
    # ========== 权限测试 ==========
    
    def test_unauthenticated_access_denied(self, api_client):
        """测试未认证访问被拒绝"""
        response = api_client.get('/api/laboratories/')
        
        assert response.status_code == 401 or response.status_code == 403
    
    def test_admin_options_endpoint(self, authenticated_client, lab_admin_user):
        """测试管理员选项接口"""
        response = authenticated_client.get('/api/laboratories/admin_options/')
        
        assert response.status_code == 200
        data = response.json()
        
        admins = data.get('admins', data.get('admin_choices', []))
        assert len(admins) >= 1
        
        # 应该包含"未分配"选项
        admin_ids = [a.get('id') for a in admins]
        assert 0 in admin_ids  # id=0 表示"未分配"


class TestLaboratoryAPIErrorHandling:
    """API 错误处理测试"""
    
    @pytest.fixture
    def authenticated_client(self, api_client, super_admin_user):
        token, _ = Token.objects.get_or_create(user=super_admin_user)
        api_client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        return api_client
    
    def test_validation_error_returns_400_not_500(
        self, authenticated_client, test_laboratory
    ):
        """
        测试验证错误返回 400 而非 500
        
        这是质量保证的关键测试！确保所有业务逻辑错误都是 400，
        只有真正的服务器错误才是 500
        """
        invalid_data = {
            'name': '',  # 无效：空名称
            'code': '',  # 无效：空编号
            'admin': 'invalid',  # 无效：非数字
            'status': 999  # 无效：超出范围
        }
        
        response = authenticated_client.put(
            f'/api/laboratories/{test_laboratory.id}/',
            invalid_data,
            format='json'
        )
        
        # 必须是 400，绝对不能是 500！
        assert response.status_code == 400, \
            f"验证错误应该返回400，但返回了{response.status_code}。这可能导致前端无法正确处理错误！"
    
    def test_method_not_allowed(self, authenticated_client):
        """测试不允许的 HTTP 方法"""
        response = authenticated_client.patch('/api/laboratories/')
        
        assert response.status_code == 405
