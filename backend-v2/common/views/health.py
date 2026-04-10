"""
系统健康检查视图
"""

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
            return ApiResponse.error(message='系统不健康', data=health_status, code=503)
