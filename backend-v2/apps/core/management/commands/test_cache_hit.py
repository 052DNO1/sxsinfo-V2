"""
测试缓存命中率的命令
用法: python manage.py test_cache_hit
"""

from django.core.management.base import BaseCommand
from django.core.cache import cache
from apps.cache_config.services.cache_config_service import ApiStatsService
from common.decorators import set_cache_hit, is_cache_hit, clear_cache_hit
import time


class Command(BaseCommand):
    help = '测试缓存命中率统计功能'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('=== 缓存命中率测试 ===\n'))
        
        self.test_thread_local_storage()
        
        self.test_cache_decorator()
        
        self.test_api_stats()
        
        self.stdout.write(self.style.SUCCESS('\n=== 测试完成 ==='))

    def test_thread_local_storage(self):
        """测试线程本地存储功能"""
        self.stdout.write('\n1. 测试线程本地存储...')
        
        clear_cache_hit()
        self.assertEqual(is_cache_hit(), False, '初始状态应为 False')
        
        set_cache_hit(True)
        self.assertEqual(is_cache_hit(), True, '设置后应为 True')
        
        set_cache_hit(False)
        self.assertEqual(is_cache_hit(), False, '设置 False 后应为 False')
        
        clear_cache_hit()
        self.assertEqual(is_cache_hit(), False, '清除后应为 False')
        
        self.stdout.write(self.style.SUCCESS('   [OK] 线程本地存储测试通过'))

    def test_cache_decorator(self):
        """测试缓存装饰器"""
        self.stdout.write('\n2. 测试缓存装饰器...')
        
        from common.decorators import cached_method
        
        test_key = 'test:cache:hit:test_method'
        cache.delete(test_key)
        
        call_count = 0
        
        class TestService:
            @cached_method(timeout=60, key_prefix='test:cache:hit')
            def get_data(self, user_id):
                nonlocal call_count
                call_count += 1
                return {'user_id': user_id, 'call_count': call_count}
        
        service = TestService()
        
        clear_cache_hit()
        result1 = service.get_data(user_id=1)
        self.assertEqual(is_cache_hit(), False, '第一次调用应未命中缓存')
        self.assertEqual(result1['call_count'], 1, '第一次调用计数应为 1')
        
        clear_cache_hit()
        result2 = service.get_data(user_id=1)
        self.assertEqual(is_cache_hit(), True, '第二次调用应命中缓存')
        self.assertEqual(result2['call_count'], 1, '缓存命中时不应重新执行方法')
        
        cache.delete(test_key)
        
        self.stdout.write(self.style.SUCCESS('   [OK] 缓存装饰器测试通过'))

    def test_api_stats(self):
        """测试 API 统计服务"""
        self.stdout.write('\n3. 测试 API 统计服务...')
        
        test_api = 'test/api/endpoint'
        
        ApiStatsService.record_request(
            api_path=test_api,
            response_time=100.5,
            is_cache_hit=True,
            is_error=False
        )
        
        ApiStatsService.record_request(
            api_path=test_api,
            response_time=50.0,
            is_cache_hit=False,
            is_error=False
        )
        
        stats = ApiStatsService.get_today_stats(test_api)
        
        self.stdout.write(f'   API 路径: {stats.get("api_path")}')
        self.stdout.write(f'   请求次数: {stats.get("request_count")}')
        self.stdout.write(f'   缓存命中次数: {stats.get("cache_hit_count")}')
        self.stdout.write(f'   缓存命中率: {stats.get("cache_hit_rate")}%')
        
        self.assertEqual(stats.get('request_count'), 2, '请求次数应为 2')
        self.assertEqual(stats.get('cache_hit_count'), 1, '缓存命中次数应为 1')
        self.assertEqual(stats.get('cache_hit_rate'), 50.0, '缓存命中率应为 50%')
        
        self.stdout.write(self.style.SUCCESS('   [OK] API 统计服务测试通过'))

    def assertEqual(self, actual, expected, message=''):
        if actual != expected:
            raise AssertionError(f'{message}\n期望: {expected}\n实际: {actual}')
