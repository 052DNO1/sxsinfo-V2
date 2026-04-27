"""
缓存用户隔离测试

测试场景：
1. 分院管理员和实训室管理员同时请求实训室列表
2. 验证两个用户的缓存数据不会互相污染
3. 模拟疯狂刷新场景
"""

import pytest
from unittest.mock import MagicMock, patch
from django.core.cache import cache

from apps.laboratories.services import LaboratoryService
from apps.laboratories.models import Laboratory
from apps.users.models import User, Department
from common.decorators import generate_cache_key, cached_method, clear_cache_hit


class TestCacheUserIsolation:
    """缓存用户隔离测试"""
    
    @pytest.fixture(autouse=True)
    def setup(self, db):
        """测试前准备"""
        cache.clear()
        
        self.dept1 = Department.objects.create(
            name='计算机学院',
            code='CS_DEPT'
        )
        self.dept2 = Department.objects.create(
            name='机械学院',
            code='ME_DEPT'
        )
        
        self.dept_admin = User.objects.create_user(
            username='dept_admin',
            password='test123456',
            nickname='分院管理员',
            role=4,
            department=self.dept1,
            is_active=True
        )
        
        self.lab_admin1 = User.objects.create_user(
            username='lab_admin1',
            password='test123456',
            nickname='实训室管理员1',
            role=2,
            department=self.dept1,
            is_active=True
        )
        
        self.lab_admin2 = User.objects.create_user(
            username='lab_admin2',
            password='test123456',
            nickname='实训室管理员2',
            role=2,
            department=self.dept1,
            is_active=True
        )
        
        self.lab1 = Laboratory.objects.create(
            name='计算机实训室1',
            code='CS_LAB_001',
            building='教学楼A',
            floor=3,
            room_number='301',
            capacity=40,
            department=self.dept1,
            admin=self.lab_admin1,
            status=1
        )
        
        self.lab2 = Laboratory.objects.create(
            name='计算机实训室2',
            code='CS_LAB_002',
            building='教学楼A',
            floor=3,
            room_number='302',
            department=self.dept1,
            admin=self.lab_admin2,
            status=1
        )
        
        self.lab3 = Laboratory.objects.create(
            name='机械实训室',
            code='ME_LAB_001',
            building='教学楼B',
            floor=2,
            room_number='201',
            department=self.dept2,
            admin=self.lab_admin1,
            status=1
        )
    
    def test_cache_key_generation_with_user_id(self):
        """测试缓存键生成是否包含用户ID"""
        key1 = generate_cache_key('lab:list', _uid=1, page=1, page_size=20)
        key2 = generate_cache_key('lab:list', _uid=2, page=1, page_size=20)
        
        assert key1 != key2, "不同用户的缓存键应该不同"
        assert '_uid:1' in key1, "缓存键应包含用户ID"
        assert '_uid:2' in key2, "缓存键应包含用户ID"
    
    def test_cache_key_no_user_object(self):
        """测试缓存键不包含用户对象（只包含ID）"""
        mock_user = MagicMock()
        mock_user.id = 5
        mock_user.username = '测试用户名'
        
        key = generate_cache_key('test', user=mock_user, page=1)
        
        assert ':5' in key, "缓存键应包含用户ID"
        assert '测试用户名' not in key, "缓存键不应包含用户名"
    
    def test_different_users_get_different_data(self):
        """测试不同用户获取不同的数据"""
        service = LaboratoryService()
        
        dept_result = service.get_laboratory_list(
            requester=self.dept_admin,
            page=1,
            page_size=20
        )
        
        lab_result = service.get_laboratory_list(
            requester=self.lab_admin1,
            page=1,
            page_size=20
        )
        
        assert dept_result is not None
        assert lab_result is not None
        
        dept_lab_ids = [lab['id'] for lab in dept_result['list']]
        lab_lab_ids = [lab['id'] for lab in lab_result['list']]
        
        assert set(dept_lab_ids) != set(lab_lab_ids), \
            f"分院管理员看到: {dept_lab_ids}, 实训室管理员看到: {lab_lab_ids}"
    
    def test_cache_isolation_rapid_refresh(self):
        """测试疯狂刷新场景下的缓存隔离"""
        service = LaboratoryService()
        
        results_dept = []
        for i in range(10):
            clear_cache_hit()
            result = service.get_laboratory_list(
                requester=self.dept_admin,
                page=1,
                page_size=20
            )
            results_dept.append({
                'iteration': i,
                'count': len(result['list']),
                'lab_ids': [lab['id'] for lab in result['list']]
            })
        
        results_lab = []
        for i in range(10):
            clear_cache_hit()
            result = service.get_laboratory_list(
                requester=self.lab_admin1,
                page=1,
                page_size=20
            )
            results_lab.append({
                'iteration': i,
                'count': len(result['list']),
                'lab_ids': [lab['id'] for lab in result['list']]
            })
        
        for r in results_dept:
            assert r['count'] == results_dept[0]['count'], \
                f"分院管理员第{r['iteration']}次结果不一致"
        
        for r in results_lab:
            assert r['count'] == results_lab[0]['count'], \
                f"实训室管理员第{r['iteration']}次结果不一致"
        
        assert results_dept[0]['count'] != results_lab[0]['count'], \
            "分院管理员和实训室管理员应该看到不同数量的实训室"
    
    def test_cache_isolation_alternating_requests(self):
        """测试交替请求场景"""
        service = LaboratoryService()
        
        for i in range(5):
            clear_cache_hit()
            dept_result = service.get_laboratory_list(
                requester=self.dept_admin,
                page=1,
                page_size=20
            )
            dept_ids = set(lab['id'] for lab in dept_result['list'])
            
            clear_cache_hit()
            lab_result = service.get_laboratory_list(
                requester=self.lab_admin1,
                page=1,
                page_size=20
            )
            lab_ids = set(lab['id'] for lab in lab_result['list'])
            
            assert dept_ids != lab_ids, \
                f"第{i+1}轮: 数据污染! 分院管理员看到{dept_ids}, 实训室管理员看到{lab_ids}"
            
            assert self.lab3.id in dept_ids, \
                f"第{i+1}轮: 分院管理员应该看到机械实训室"
            
            assert self.lab3.id not in lab_ids, \
                f"第{i+1}轮: 实训室管理员不应该看到机械实训室"
    
    def test_cache_key_consistency(self):
        """测试缓存键一致性"""
        service = LaboratoryService()
        
        with patch('common.decorators.generate_cache_key', wraps=generate_cache_key) as mock_gen:
            for _ in range(3):
                service.get_laboratory_list(
                    requester=self.dept_admin,
                    page=1,
                    page_size=20
                )
            
            keys = [call.args for call in mock_gen.call_args_list]
            first_key = keys[0]
            
            for key in keys[1:]:
                assert key == first_key, "相同参数应生成相同的缓存键"
    
    def test_no_cross_user_cache_pollution(self):
        """测试无跨用户缓存污染"""
        service = LaboratoryService()
        
        result1 = service.get_laboratory_list(
            requester=self.dept_admin,
            page=1,
            page_size=20
        )
        dept_admin_data_ids = set(lab['id'] for lab in result1['list'])
        
        for _ in range(20):
            service.get_laboratory_list(
                requester=self.lab_admin1,
                page=1,
                page_size=20
            )
            service.get_laboratory_list(
                requester=self.lab_admin2,
                page=1,
                page_size=20
            )
        
        result2 = service.get_laboratory_list(
            requester=self.dept_admin,
            page=1,
            page_size=20
        )
        dept_admin_data_ids_after = set(lab['id'] for lab in result2['list'])
        
        assert dept_admin_data_ids == dept_admin_data_ids_after, \
            f"分院管理员数据被污染! 之前: {dept_admin_data_ids}, 之后: {dept_admin_data_ids_after}"


class TestCacheKeyEdgeCases:
    """缓存键边界情况测试"""
    
    def test_cache_key_with_none_value(self):
        """测试缓存键处理None值"""
        key1 = generate_cache_key('test', page=1, search=None)
        key2 = generate_cache_key('test', page=1)
        
        assert key1 == key2, "None值应该被忽略"
    
    def test_cache_key_with_list_value(self):
        """测试缓存键处理列表值"""
        key = generate_cache_key('test', ids=[1, 2, 3])
        
        assert 'ids:1,2,3' in key, "列表值应该被正确处理"
    
    def test_cache_key_with_dict_value(self):
        """测试缓存键处理字典值"""
        key = generate_cache_key('test', filters={'status': 1, 'type': 'A'})
        
        assert 'filters:' in key, "字典值应该被正确处理"
    
    def test_cache_key_with_object(self):
        """测试缓存键处理对象"""
        mock_obj = MagicMock()
        mock_obj.id = 123
        
        key = generate_cache_key('test', obj=mock_obj)
        
        assert 'obj:123' in key, "对象应该使用其ID"
