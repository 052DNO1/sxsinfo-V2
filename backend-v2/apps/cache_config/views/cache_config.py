"""
缓存配置视图
"""

import logging
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone
from django.db.models import Count, Q as QueryQ
from datetime import timedelta

from apps.cache_config.models import CacheConfig, ApiStats, CacheOperationLog
from apps.cache_config.serializers.cache_config import (
    CacheConfigSerializer, CacheConfigCreateSerializer, CacheConfigUpdateSerializer,
    ApiStatsSerializer, ApiStatsSummarySerializer, CacheOperationLogSerializer,
    CacheClearSerializer
)
from apps.cache_config.services.cache_config_service import CacheConfigService, ApiStatsService
from common.responses import ApiResponse
from common.permissions import IsSuperAdmin
from rest_framework.permissions import IsAuthenticated

logger = logging.getLogger(__name__)


class CacheConfigViewSet(viewsets.ModelViewSet):
    """缓存配置视图集（仅超管）"""
    permission_classes = [IsAuthenticated, IsSuperAdmin]
    
    queryset = CacheConfig.objects.all().order_by('category', 'api_path')
    serializer_class = CacheConfigSerializer
    pagination_class = None
    
    def get_queryset(self):
        queryset = super().get_queryset()
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category=category)
        return queryset
    
    def get_serializer_class(self):
        if self.action == 'create':
            return CacheConfigCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return CacheConfigUpdateSerializer
        return CacheConfigSerializer
    
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return ApiResponse.success(data=serializer.data)
    
    def create(self, request, *args, **kwargs):
        try:
            config = CacheConfigService.create_config(request, request.data)
            serializer = CacheConfigSerializer(config)
            return ApiResponse.success(
                data=serializer.data,
                message='缓存配置创建成功'
            )
        except Exception as e:
            logger.error(f"Failed to create cache config: {e}")
            return ApiResponse.error(message=str(e))
    
    def update(self, request, *args, **kwargs):
        try:
            config_id = kwargs.get('pk')
            config = CacheConfigService.update_config(request, config_id, request.data)
            serializer = CacheConfigSerializer(config)
            return ApiResponse.success(
                data=serializer.data,
                message='缓存配置更新成功'
            )
        except ValueError as e:
            return ApiResponse.error(message=str(e), code=404)
        except Exception as e:
            logger.error(f"Failed to update cache config: {e}")
            return ApiResponse.error(message=str(e))
    
    def destroy(self, request, *args, **kwargs):
        try:
            config_id = kwargs.get('pk')
            CacheConfigService.delete_config(request, config_id)
            return ApiResponse.success(message='缓存配置删除成功')
        except ValueError as e:
            return ApiResponse.error(message=str(e), code=404)
        except Exception as e:
            logger.error(f"Failed to delete cache config: {e}")
            return ApiResponse.error(message=str(e))
    
    @action(detail=False, methods=['get'])
    def all(self, request):
        """获取所有缓存配置"""
        configs = CacheConfigService.get_all_configs()
        return ApiResponse.success(data=configs)


class ApiStatsViewSet(viewsets.ReadOnlyModelViewSet):
    """API统计视图集（仅超管）"""
    permission_classes = [IsAuthenticated, IsSuperAdmin]
    
    queryset = ApiStats.objects.all()
    serializer_class = ApiStatsSerializer
    
    @action(detail=False, methods=['get'])
    def today(self, request):
        """获取今日统计"""
        api_path = request.query_params.get('api_path')
        stats = ApiStatsService.get_today_stats(api_path)
        return ApiResponse.success(data=stats)
    
    @action(detail=False, methods=['get'])
    def range(self, request):
        """获取日期范围统计"""
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        api_path = request.query_params.get('api_path')
        
        if not start_date or not end_date:
            return ApiResponse.error(message='请提供start_date和end_date参数')
        
        stats = ApiStatsService.get_date_range_stats(start_date, end_date, api_path)
        return ApiResponse.success(data=list(stats))
    
    @action(detail=False, methods=['get'])
    def ranking(self, request):
        """获取API请求量排名"""
        date = request.query_params.get('date')
        limit = int(request.query_params.get('limit', 10))
        
        ranking = ApiStatsService.get_api_ranking(date, limit)
        return ApiResponse.success(data=list(ranking))


class CacheOperationLogViewSet(viewsets.ReadOnlyModelViewSet):
    """缓存操作日志视图集（仅超管）"""
    permission_classes = [IsAuthenticated, IsSuperAdmin]
    
    queryset = CacheOperationLog.objects.all()
    serializer_class = CacheOperationLogSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        operation_type = self.request.query_params.get('operation_type')
        if operation_type:
            queryset = queryset.filter(operation_type=operation_type)
        
        api_path = self.request.query_params.get('api_path')
        if api_path:
            queryset = queryset.filter(api_path__icontains=api_path)
        
        operator_id = self.request.query_params.get('operator_id')
        if operator_id:
            queryset = queryset.filter(operator_id=operator_id)
        
        return queryset


class CacheClearView(APIView):
    """缓存清除视图（仅超管）"""
    permission_classes = [IsAuthenticated, IsSuperAdmin]
    
    def post(self, request):
        serializer = CacheClearSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        api_path = serializer.validated_data.get('api_path', '')
        reason = serializer.validated_data.get('reason', '')
        
        try:
            cleared_count = CacheConfigService.clear_cache(request, api_path, reason)
            return ApiResponse.success(
                data={'cleared_count': cleared_count},
                message=f'成功清除 {cleared_count} 个缓存'
            )
        except Exception as e:
            logger.error(f"Failed to clear cache: {e}")
            return ApiResponse.error(message=str(e))


class CacheConfigOverviewView(APIView):
    """缓存配置概览视图（仅超管）"""
    permission_classes = [IsAuthenticated, IsSuperAdmin]
    
    def get(self, request):
        today_stats = ApiStatsService.get_today_stats()
        
        total_configs = CacheConfig.objects.count()
        enabled_configs = CacheConfig.objects.filter(enabled=True).count()
        
        recent_logs = CacheOperationLog.objects.order_by('-created_at')[:5]
        log_serializer = CacheOperationLogSerializer(recent_logs, many=True)
        
        top_apis = ApiStatsService.get_api_ranking(limit=5)
        
        category_stats = CacheConfig.objects.values('category').annotate(
            total=Count('id'),
            enabled=Count('id', filter=QueryQ(enabled=True))
        ).order_by('category')
        
        return ApiResponse.success(data={
            'today_stats': today_stats,
            'config_stats': {
                'total': total_configs,
                'enabled': enabled_configs,
                'disabled': total_configs - enabled_configs,
            },
            'category_stats': list(category_stats),
            'recent_logs': log_serializer.data,
            'top_apis': list(top_apis),
        })


class AutoDiscoverAPIView(APIView):
    """自动扫描并初始化API缓存配置（仅超管）"""
    permission_classes = [IsAuthenticated, IsSuperAdmin]
    
    def post(self, request):
        try:
            result = CacheConfigService.auto_discover_apis(request)
            
            return ApiResponse.success(
                data=result,
                message=f'成功发现 {result["total_discovered"]} 个API，新增 {result["created"]} 个配置'
            )
        except Exception as e:
            logger.error(f"Failed to auto-discover APIs: {e}")
            return ApiResponse.error(message=str(e))


class CacheBatchToggleView(APIView):
    """批量开启/关闭缓存（仅超管）"""
    permission_classes = [IsAuthenticated, IsSuperAdmin]
    
    def post(self, request):
        from django.utils import timezone
        
        enabled = request.data.get('enabled', True)
        count = CacheConfig.objects.update(
            enabled=enabled,
            updated_at=timezone.now()
        )
        
        action_text = '开启' if enabled else '关闭'
        
        CacheOperationLog.create_log(
            request=request,
            operation_type='config_update',
            api_path='*',
            new_value={'enabled': enabled, 'count': count},
            reason=f'批量{action_text}所有缓存配置'
        )
        
        CacheConfigService._invalidate_config_cache('')
        
        return ApiResponse.success(
            data={'count': count},
            message=f'已{action_text} {count} 个缓存配置'
        )
