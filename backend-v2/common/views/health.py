"""
系统健康检查视图
"""

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from drf_spectacular.utils import extend_schema
from django.db import connection
from django.core.cache import cache
from common.responses import ApiResponse


class HealthCheckView(APIView):
    """健康检查视图"""
    permission_classes = [AllowAny]

    @extend_schema(description='健康检查')
    def get(self, request):
        health_status = {
            'status': 'healthy',
            'database': 'unknown',
            'cache': 'unknown',
        }
        
        try:
            with connection.cursor() as cursor:
                cursor.execute('SELECT 1')
            health_status['database'] = 'ok'
        except Exception as e:
            health_status['database'] = f'error: {str(e)}'
            health_status['status'] = 'unhealthy'
        
        try:
            cache.set('health_check', 'ok', 10)
            if cache.get('health_check') == 'ok':
                health_status['cache'] = 'ok'
            else:
                health_status['cache'] = 'error'
                health_status['status'] = 'unhealthy'
        except Exception as e:
            health_status['cache'] = f'error: {str(e)}'
            health_status['status'] = 'unhealthy'
        
        if health_status['status'] == 'healthy':
            return ApiResponse.success(data=health_status)
        else:
            # 注意：ApiResponse.error 的默认 HTTP 状态码是 400，
            # 而健康检查在数据库/缓存异常时的语义是 503（服务暂不可用）。
            # 只写 code=503 而不传 status_code 会让 HTTP 状态停在 400，
            # 客户端的探测逻辑（probeServer）就会把它当成"请求被拒绝"而不是"服务自检未通过"。
            return ApiResponse.error(
                message='系统不健康',
                data=health_status,
                code=503,
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
