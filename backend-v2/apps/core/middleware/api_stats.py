"""
API统计中间件
记录API请求统计信息
"""

import time
import logging
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger(__name__)


class ApiStatsMiddleware(MiddlewareMixin):
    """API请求统计中间件"""
    
    EXCLUDED_PATHS = [
        '/api/v1/cache-config/',
        '/api/v1/cache-config',
        '/admin/',
        '/static/',
        '/media/',
        '/__debug__/',
        '/api/schema/',
        '/api/docs/',
    ]
    
    def process_request(self, request):
        if self._should_track(request):
            request._api_stats_start_time = time.time()
        return None
    
    def process_response(self, request, response):
        if not hasattr(request, '_api_stats_start_time'):
            return response
        
        if not self._should_track(request):
            return response
        
        try:
            response_time = (time.time() - request._api_stats_start_time) * 1000
            
            api_path = request.path
            if api_path.startswith('/api/v1/'):
                api_path = api_path[7:].lstrip('/')
            
            is_error = response.status_code >= 400
            
            is_cache_hit = self._check_cache_hit(request, response)
            
            from apps.cache_config.services.cache_config_service import ApiStatsService
            ApiStatsService.record_request(
                api_path=api_path,
                response_time=response_time,
                is_cache_hit=is_cache_hit,
                is_error=is_error
            )
            
        except Exception as e:
            logger.error(f"[ApiStats] 记录失败: {e}, path={request.path}", exc_info=True)
        
        return response
    
    def _should_track(self, request) -> bool:
        """判断是否需要统计该请求"""
        if not request.path.startswith('/api/'):
            return False
        
        for excluded in self.EXCLUDED_PATHS:
            if request.path.startswith(excluded):
                return False
        
        return True
    
    def _check_cache_hit(self, request, response) -> bool:
        """检查是否命中缓存"""
        if hasattr(response, 'get'):
            cache_status = response.get('X-Cache-Status', '')
            if cache_status.lower() in ['hit', 'cached']:
                return True
        
        if hasattr(request, '_cache_hit'):
            return request._cache_hit
        
        return False
