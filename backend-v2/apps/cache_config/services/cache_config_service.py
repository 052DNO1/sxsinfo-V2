"""
缓存配置服务层
提供缓存配置管理、API统计、操作日志等功能
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from django.core.cache import cache
from django.db import transaction
from django.utils import timezone
from django.db.models import Sum, Avg, Count

from apps.cache_config.models import CacheConfig, ApiStats, CacheOperationLog
from common.services.cache_service import CacheManager

logger = logging.getLogger(__name__)


class CacheConfigService:
    """缓存配置服务"""
    
    CACHE_CONFIG_KEY = 'lims:cache:config:{api_path}'
    ALL_CONFIGS_KEY = 'lims:cache:config:all'
    
    @classmethod
    def get_config(cls, api_path: str) -> Optional[Dict]:
        """
        获取API缓存配置
        优先从Redis缓存读取，缓存未命中则从数据库读取
        """
        cache_key = cls.CACHE_CONFIG_KEY.format(api_path=api_path)
        config = cache.get(cache_key)
        
        if config is not None:
            return config
        
        config_obj = CacheConfig.get_config(api_path)
        if config_obj:
            config = {
                'api_path': config_obj.api_path,
                'frontend_ttl': config_obj.frontend_ttl,
                'backend_ttl': config_obj.backend_ttl,
                'enabled': config_obj.enabled,
            }
            cache.set(cache_key, config, timeout=300)
            return config
        
        return None
    
    @classmethod
    def get_all_configs(cls) -> Dict[str, Dict]:
        """获取所有缓存配置"""
        cache_key = cls.ALL_CONFIGS_KEY
        configs = cache.get(cache_key)
        
        if configs is not None:
            return configs
        
        config_objs = CacheConfig.get_all_configs()
        configs = {}
        for obj in config_objs:
            configs[obj.api_path] = {
                'api_path': obj.api_path,
                'frontend_ttl': obj.frontend_ttl,
                'backend_ttl': obj.backend_ttl,
                'enabled': obj.enabled,
            }
        
        cache.set(cache_key, configs, timeout=300)
        return configs
    
    @classmethod
    def create_config(cls, request, data: Dict) -> CacheConfig:
        """创建缓存配置"""
        with transaction.atomic():
            config = CacheConfig.objects.create(
                api_path=data['api_path'],
                frontend_ttl=data.get('frontend_ttl', 60),
                backend_ttl=data.get('backend_ttl', 300),
                enabled=data.get('enabled', True),
                description=data.get('description', ''),
                updated_by=request.user if request.user.is_authenticated else None
            )
            
            CacheOperationLog.create_log(
                request=request,
                operation_type='config_create',
                api_path=config.api_path,
                new_value={
                    'frontend_ttl': config.frontend_ttl,
                    'backend_ttl': config.backend_ttl,
                    'enabled': config.enabled,
                },
                reason=data.get('reason', '')
            )
            
            cls._invalidate_config_cache(config.api_path)
            
            logger.info(f"Cache config created: {config.api_path}")
            return config
    
    @classmethod
    def update_config(cls, request, config_id: int, data: Dict) -> CacheConfig:
        """更新缓存配置"""
        try:
            config = CacheConfig.objects.get(id=config_id)
        except CacheConfig.DoesNotExist:
            raise ValueError(f"Cache config not found: {config_id}")
        
        old_value = {
            'frontend_ttl': config.frontend_ttl,
            'backend_ttl': config.backend_ttl,
            'enabled': config.enabled,
            'description': config.description,
        }
        
        with transaction.atomic():
            config.frontend_ttl = data.get('frontend_ttl', config.frontend_ttl)
            config.backend_ttl = data.get('backend_ttl', config.backend_ttl)
            config.enabled = data.get('enabled', config.enabled)
            config.description = data.get('description', config.description)
            config.updated_by = request.user if request.user.is_authenticated else None
            config.save()
            
            CacheOperationLog.create_log(
                request=request,
                operation_type='config_update',
                api_path=config.api_path,
                old_value=old_value,
                new_value={
                    'frontend_ttl': config.frontend_ttl,
                    'backend_ttl': config.backend_ttl,
                    'enabled': config.enabled,
                },
                reason=data.get('reason', '')
            )
            
            cls._invalidate_config_cache(config.api_path)
            
            logger.info(f"Cache config updated: {config.api_path}")
            return config
    
    @classmethod
    def delete_config(cls, request, config_id: int) -> bool:
        """删除缓存配置"""
        try:
            config = CacheConfig.objects.get(id=config_id)
        except CacheConfig.DoesNotExist:
            raise ValueError(f"Cache config not found: {config_id}")
        
        old_value = {
            'frontend_ttl': config.frontend_ttl,
            'backend_ttl': config.backend_ttl,
            'enabled': config.enabled,
        }
        
        with transaction.atomic():
            api_path = config.api_path
            config.delete()
            
            CacheOperationLog.create_log(
                request=request,
                operation_type='config_delete',
                api_path=api_path,
                old_value=old_value,
                reason=request.data.get('reason', '')
            )
            
            cls._invalidate_config_cache(api_path)
            
            logger.info(f"Cache config deleted: {api_path}")
            return True
    
    @classmethod
    def clear_cache(cls, request, api_path: str = '', reason: str = '') -> int:
        """
        清除缓存
        返回清除的缓存数量
        """
        cleared_count = 0
        
        if api_path:
            pattern = f"*{api_path}*"
            cleared_count = CacheManager.delete_pattern(pattern)
            
            CacheOperationLog.create_log(
                request=request,
                operation_type='cache_clear',
                api_path=api_path,
                reason=reason
            )
        else:
            cleared_count = CacheManager.delete_pattern('*')
            
            CacheOperationLog.create_log(
                request=request,
                operation_type='cache_clear_all',
                reason=reason
            )
        
        logger.info(f"Cache cleared: {api_path or 'all'}, count: {cleared_count}")
        return cleared_count
    
    @classmethod
    def _invalidate_config_cache(cls, api_path: str):
        """使配置缓存失效"""
        cache_key = cls.CACHE_CONFIG_KEY.format(api_path=api_path)
        cache.delete(cache_key)
        cache.delete(cls.ALL_CONFIGS_KEY)
    
    @classmethod
    def auto_discover_apis(cls, request=None):
        """
        自动扫描系统中所有API路由，生成默认缓存配置
        """
        from api.v1 import urls as api_urls
        
        DEFAULT_FRONTEND_TTL = 60
        DEFAULT_BACKEND_TTL = 300
        
        EXCLUDED_PATTERNS = ['auth/', 'cache-config/']
        
        API_BASE_PREFIX = '/api/v1/'
        
        discovered_apis = []
        
        def collect_from_urlpatterns(urlpatterns, current_path=''):
            for pattern in urlpatterns:
                route_str = str(pattern.pattern).strip('^').strip('$')
                
                if hasattr(pattern, 'url_patterns'):
                    new_path = f"{current_path}{route_str}"
                    collect_from_urlpatterns(pattern.url_patterns, new_path)
                else:
                    if not route_str or '{' in route_str:
                        continue
                    
                    full_api_path = f"{API_BASE_PREFIX}{current_path}{route_str}"
                    if not full_api_path.endswith('/'):
                        full_api_path += '/'
                    
                    if any(excluded in full_api_path for excluded in EXCLUDED_PATTERNS):
                        continue
                    
                    discovered_apis.append(full_api_path)
        
        try:
            collect_from_urlpatterns(api_urls.urlpatterns)
        except Exception as e:
            logger.warning(f"Failed to scan URLs: {e}")
        
        default_descriptions = {
            '/schedules/': '日程管理相关接口',
            '/laboratories/': '实训室管理相关接口',
            '/equipments/': '设备管理相关接口',
            '/records/': '使用记录相关接口',
            '/work-orders/': '工单管理相关接口',
            '/users/': '用户管理相关接口',
            '/departments/': '部门管理相关接口',
            '/semesters/': '学期管理相关接口',
            '/notifications/': '通知管理相关接口',
            '/ai/': 'AI助手相关接口',
            '/backups/': '数据备份相关接口',
            '/statistics/': '统计分析相关接口',
            '/common/': '公共功能相关接口',
        }
        
        created_count = 0
        
        for api_path in discovered_apis:
            existing = CacheConfig.objects.filter(api_path=api_path).first()
            
            if existing:
                continue
            
            description = ''
            for key, desc in default_descriptions.items():
                if key in api_path:
                    description = desc
                    break
            
            CacheConfig.objects.create(
                api_path=api_path,
                frontend_ttl=DEFAULT_FRONTEND_TTL,
                backend_ttl=DEFAULT_BACKEND_TTL,
                enabled=True,
                description=description or f'{api_path} 缓存配置'
            )
            created_count += 1
        
        result = {
            'total_discovered': len(discovered_apis),
            'created': created_count,
            'existed': len(discovered_apis) - created_count,
            'apis': discovered_apis
        }
        
        logger.info(f"Auto-discovered APIs: {result}")
        
        cls._invalidate_config_cache('')
        
        if request and created_count > 0:
            CacheOperationLog.create_log(
                request=request,
                operation_type='config_create',
                api_path='*',
                old_value=None,
                new_value=result,
                reason=f'自动发现并初始化 {created_count} 个API缓存配置'
            )
        
        return result


class ApiStatsService:
    """API统计服务"""
    
    STATS_KEY_PREFIX = 'lims:api:stats'
    STATS_TTL = 7 * 24 * 3600
    
    @classmethod
    def record_request(cls, api_path: str, response_time: float, 
                       is_cache_hit: bool = False, is_error: bool = False):
        """
        记录API请求统计
        使用Redis实时统计，定时任务聚合到数据库
        """
        today = timezone.now().strftime('%Y-%m-%d')
        
        count_key = f"{cls.STATS_KEY_PREFIX}:{today}:{api_path}:count"
        time_key = f"{cls.STATS_KEY_PREFIX}:{today}:{api_path}:time"
        hit_key = f"{cls.STATS_KEY_PREFIX}:{today}:{api_path}:hit"
        error_key = f"{cls.STATS_KEY_PREFIX}:{today}:{api_path}:error"
        
        cls._safe_incr(count_key, 1)
        cls._safe_incr(time_key, int(response_time))
        
        if is_cache_hit:
            cls._safe_incr(hit_key, 1)
        
        if is_error:
            cls._safe_incr(error_key, 1)
        
        if not cache.ttl(count_key):
            cache.expire(count_key, cls.STATS_TTL)
            cache.expire(time_key, cls.STATS_TTL)
            cache.expire(hit_key, cls.STATS_TTL)
            cache.expire(error_key, cls.STATS_TTL)

    @classmethod
    def _safe_incr(cls, key: str, amount: int = 1):
        """安全递增Redis计数器，key不存在时自动初始化"""
        try:
            cache.incr(key, amount)
        except ValueError:
            cache.set(key, amount, cls.STATS_TTL)
        except Exception as e:
            logger.warning(f"[ApiStats] Redis操作失败: key={key}, error={e}")
    
    @classmethod
    def get_today_stats(cls, api_path: str = None) -> Dict:
        """获取今日统计数据"""
        today = timezone.now().strftime('%Y-%m-%d')
        
        if api_path:
            return cls._get_single_api_stats(today, api_path)
        else:
            return cls._get_all_api_stats(today)
    
    @classmethod
    def _get_single_api_stats(cls, date: str, api_path: str) -> Dict:
        """获取单个API的统计"""
        count_key = f"{cls.STATS_KEY_PREFIX}:{date}:{api_path}:count"
        time_key = f"{cls.STATS_KEY_PREFIX}:{date}:{api_path}:time"
        hit_key = f"{cls.STATS_KEY_PREFIX}:{date}:{api_path}:hit"
        error_key = f"{cls.STATS_KEY_PREFIX}:{date}:{api_path}:error"
        
        request_count = cache.get(count_key, 0)
        total_time = cache.get(time_key, 0)
        cache_hit = cache.get(hit_key, 0)
        error_count = cache.get(error_key, 0)
        
        avg_time = round(total_time / request_count, 2) if request_count > 0 else 0
        hit_rate = round(cache_hit / request_count * 100, 2) if request_count > 0 else 0
        
        return {
            'api_path': api_path,
            'date': date,
            'request_count': request_count,
            'cache_hit_count': cache_hit,
            'total_response_time': total_time,
            'avg_response_time': avg_time,
            'cache_hit_rate': hit_rate,
            'error_count': error_count,
        }
    
    @classmethod
    def _get_all_api_stats(cls, date: str) -> Dict:
        """获取所有API的统计汇总"""
        pattern = f"{cls.STATS_KEY_PREFIX}:{date}:*:count"
        keys = cache.keys(pattern)
        
        total_requests = 0
        total_cache_hits = 0
        total_time = 0
        total_errors = 0
        api_count = len(keys)
        
        prefix_len = len(f"{cls.STATS_KEY_PREFIX}:{date}:")
        
        for key in keys:
            count = cache.get(key, 0)
            total_requests += count
            
            api_path = key[prefix_len:key.rfind(':')]
            time_key = f"{cls.STATS_KEY_PREFIX}:{date}:{api_path}:time"
            hit_key = f"{cls.STATS_KEY_PREFIX}:{date}:{api_path}:hit"
            error_key = f"{cls.STATS_KEY_PREFIX}:{date}:{api_path}:error"
            
            total_time += cache.get(time_key, 0)
            total_cache_hits += cache.get(hit_key, 0)
            total_errors += cache.get(error_key, 0)
        
        avg_time = round(total_time / total_requests, 2) if total_requests > 0 else 0
        hit_rate = round(total_cache_hits / total_requests * 100, 2) if total_requests > 0 else 0
        
        return {
            'date': date,
            'api_count': api_count,
            'total_requests': total_requests,
            'total_cache_hits': total_cache_hits,
            'total_response_time': total_time,
            'avg_response_time': avg_time,
            'cache_hit_rate': hit_rate,
            'total_errors': total_errors,
        }
    
    @classmethod
    def get_date_range_stats(cls, start_date, end_date, api_path: str = None) -> List[Dict]:
        """获取日期范围内的统计"""
        if api_path:
            stats = ApiStats.get_date_range_stats(api_path, start_date, end_date)
            return ApiStats.objects.filter(
                api_path=api_path,
                date__gte=start_date,
                date__lte=end_date
            ).order_by('date').values(
                'api_path', 'date', 'request_count', 'cache_hit_count',
                'total_response_time', 'error_count'
            )
        else:
            return ApiStats.objects.filter(
                date__gte=start_date,
                date__lte=end_date
            ).values('date').annotate(
                total_requests=Sum('request_count'),
                total_cache_hits=Sum('cache_hit_count'),
                total_time=Sum('total_response_time'),
                total_errors=Sum('error_count'),
                api_count=Count('api_path', distinct=True)
            ).order_by('date')
    
    @classmethod
    def aggregate_to_database(cls, date: str = None):
        """
        将Redis中的统计数据聚合到数据库
        通常由定时任务调用
        """
        if date is None:
            date = timezone.now().strftime('%Y-%m-%d')
        
        pattern = f"{cls.STATS_KEY_PREFIX}:{date}:*:count"
        keys = cache.keys(pattern)
        
        aggregated_count = 0
        prefix_len = len(f"{cls.STATS_KEY_PREFIX}:{date}:")
        for key in keys:
            api_path = key[prefix_len:key.rfind(':')]
            
            count_key = f"{cls.STATS_KEY_PREFIX}:{date}:{api_path}:count"
            time_key = f"{cls.STATS_KEY_PREFIX}:{date}:{api_path}:time"
            hit_key = f"{cls.STATS_KEY_PREFIX}:{date}:{api_path}:hit"
            error_key = f"{cls.STATS_KEY_PREFIX}:{date}:{api_path}:error"
            
            request_count = cache.get(count_key, 0)
            total_time = cache.get(time_key, 0)
            cache_hit = cache.get(hit_key, 0)
            error_count = cache.get(error_key, 0)
            
            if request_count > 0:
                ApiStats.objects.update_or_create(
                    api_path=api_path,
                    date=date,
                    defaults={
                        'request_count': request_count,
                        'total_response_time': total_time,
                        'cache_hit_count': cache_hit,
                        'error_count': error_count,
                    }
                )
                aggregated_count += 1
        
        logger.info(f"Aggregated {aggregated_count} API stats for {date}")
        return aggregated_count
    
    @classmethod
    def get_api_ranking(cls, date: str = None, limit: int = 10) -> List[Dict]:
        """获取API请求量排名"""
        if date is None:
            date = timezone.now().strftime('%Y-%m-%d')
        
        today = timezone.now().strftime('%Y-%m-%d')
        
        if date == today:
            pattern = f"{cls.STATS_KEY_PREFIX}:{date}:*:count"
            keys = cache.keys(pattern)
            
            ranking = []
            prefix_len = len(f"{cls.STATS_KEY_PREFIX}:{date}:")
            for key in keys:
                api_path = key[prefix_len:key.rfind(':')]
                count = cache.get(key, 0)
                if count > 0:
                    hit_key = f"{cls.STATS_KEY_PREFIX}:{date}:{api_path}:hit"
                    error_key = f"{cls.STATS_KEY_PREFIX}:{date}:{api_path}:error"
                    ranking.append({
                        'api_path': api_path,
                        'request_count': count,
                        'cache_hit_count': cache.get(hit_key, 0),
                        'error_count': cache.get(error_key, 0),
                    })
            
            ranking.sort(key=lambda x: x['request_count'], reverse=True)
            return ranking[:limit]
        
        return ApiStats.objects.filter(
            date=date
        ).order_by('-request_count')[:limit].values(
            'api_path', 'request_count', 'cache_hit_count', 'error_count'
        )
