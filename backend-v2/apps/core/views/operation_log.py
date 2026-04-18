"""
系统操作日志视图
提供管理员查看操作日志的 API 接口
"""

import logging
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from datetime import timedelta

from apps.core.models import SystemOperationLog
from apps.core.serializers.operation_log import (
    SystemOperationLogSerializer,
    SystemOperationLogListSerializer,
    OperationLogStatsSerializer
)
from apps.core.services.operation_log_service import OperationLogService
from common.responses import ApiResponse

logger = logging.getLogger(__name__)


class SystemOperationLogViewSet(viewsets.ReadOnlyModelViewSet):
    """系统操作日志视图集 - 仅管理员可访问"""

    permission_classes = [IsAuthenticated]
    queryset = SystemOperationLog.objects.all()

    def get_permissions(self):
        """只有管理员才能访问操作日志"""
        from rest_framework.permissions import IsAuthenticated
        permissions = [IsAuthenticated()]
        
        if self.request and self.request.user.is_authenticated:
            if not (self.request.user.is_superuser or 
                   getattr(self.request.user, 'is_system_admin', False) or
                   getattr(self.request.user, 'is_super_admin', False)):
                from rest_framework.permissions import IsAdminUser
                permissions = [IsAuthenticated(), IsAdminUser()]
        
        return permissions

    def get_serializer_class(self):
        if self.action == 'list':
            return SystemOperationLogListSerializer
        return SystemOperationLogSerializer

    def get_queryset(self):
        queryset = SystemOperationLog.objects.select_related('operator').all()

        module = self.request.query_params.get('module')
        if module:
            queryset = queryset.filter(module=module)

        operation_type = self.request.query_params.get('operation_type')
        if operation_type:
            queryset = queryset.filter(operation_type=operation_type)

        operator_id = self.request.query_params.get('operator_id')
        if operator_id:
            queryset = queryset.filter(operator_id=operator_id)

        target_type = self.request.query_params.get('target_type')
        if target_type:
            queryset = queryset.filter(target_type=target_type)

        start_date = self.request.query_params.get('start_date')
        if start_date:
            try:
                from datetime import datetime
                start = datetime.strptime(start_date, '%Y-%m-%d')
                queryset = queryset.filter(created_at__gte=start)
            except ValueError:
                pass

        end_date = self.request.query_params.get('end_date')
        if end_date:
            try:
                from datetime import datetime
                end = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
                queryset = queryset.filter(created_at__lt=end)
            except ValueError:
                pass

        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                models.Q(description__icontains=search) |
                models.Q(target_name__icontains=search) |
                models.Q(operator_username__icontains=search)
            )

        return queryset.order_by('-created_at')

    def list(self, request, *args, **kwargs):
        """获取操作日志列表（支持分页和筛选）"""
        try:
            from django.core.paginator import Paginator
            
            queryset = self.get_queryset()
            
            page_size = int(request.query_params.get('page_size', 20))
            page = int(request.query_params.get('page', 1))
            
            paginator = Paginator(queryset, page_size)
            page_obj = paginator.page(page)
            
            serializer = self.get_serializer(page_obj.object_list, many=True)
            
            return ApiResponse.success(
                data={
                    'list': serializer.data,
                    'pagination': {
                        'total': paginator.count,
                        'page': page,
                        'page_size': page_size,
                        'total_pages': paginator.num_pages,
                    }
                },
                message='获取操作日志列表成功'
            )
        except Exception as e:
            logger.error(f"Failed to get operation logs: {e}")
            return ApiResponse.error(message=str(e))

    def retrieve(self, request, *args, **kwargs):
        """获取操作日志详情"""
        try:
            log = self.get_object()
            serializer = self.get_serializer(log)
            return ApiResponse.success(
                data=serializer.data,
                message='获取操作日志详情成功'
            )
        except Exception as e:
            logger.error(f"Failed to get operation log detail: {e}")
            return ApiResponse.error(message=str(e))

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """
        获取操作日志统计信息
        
        返回：
        - total_count: 总日志数
        - today_count: 今日日志数
        - week_count: 近7天日志数
        - module_stats: 按模块统计
        - recent_operations: 最近10条操作
        """
        try:
            stats = OperationLogService.get_stats()
            return ApiResponse.success(
                data=stats,
                message='获取统计信息成功'
            )
        except Exception as e:
            logger.error(f"Failed to get operation log stats: {e}")
            return ApiResponse.error(message=str(e))

    @action(detail=False, methods=['get'])
    def recent(self, request):
        """获取最近操作记录（用于仪表盘展示）"""
        try:
            limit = int(request.query_params.get('limit', 10))
            limit = min(limit, 50)
            
            logs = SystemOperationLog.objects.select_related('operator')[:limit]
            serializer = SystemOperationLogListSerializer(logs, many=True)
            
            return ApiResponse.success(
                data=serializer.data,
                message='获取最近操作成功'
            )
        except Exception as e:
            logger.error(f"Failed to get recent operations: {e}")
            return ApiResponse.error(message=str(e))

    @action(detail=False, methods=['get'])
    def modules(self, request):
        """获取所有可用模块及其操作类型"""
        try:
            modules = []
            for module_value, module_name in SystemOperationLog.MODULE_CHOICES:
                operations = [
                    {'value': op[0], 'label': op[1]}
                    for op in SystemOperationLog.OPERATION_TYPE_CHOICES
                    if op[0].startswith(f'{module_value}_')
                ]
                modules.append({
                    'value': module_value,
                    'name': module_name,
                    'operations': operations
                })
            
            return ApiResponse.success(
                data=modules,
                message='获取模块列表成功'
            )
        except Exception as e:
            logger.error(f"Failed to get modules: {e}")
            return ApiResponse.error(message=str(e))

    @action(detail=False, methods=['get'])
    def export(self, request):
        """
        导出操作日志
        
        支持筛选条件导出为 CSV 格式
        """
        try:
            queryset = self.get_queryset()
            
            limit = int(request.query_params.get('limit', 1000))
            limit = min(limit, 10000)
            
            logs = queryset[:limit]
            
            import csv
            import io
            
            output = io.StringIO()
            writer = csv.writer(output)
            
            writer.writerow([
                'ID', '操作时间', '模块', '操作类型', '操作人',
                '目标对象', '描述', 'IP地址'
            ])
            
            for log in logs:
                writer.writerow([
                    log.id,
                    log.created_at.strftime('%Y-%m-%d %H:%M:%S') if log.created_at else '',
                    log.get_module_display(),
                    log.get_operation_type_display(),
                    log.operator_username,
                    log.target_name,
                    log.description,
                    log.ip_address or '',
                ])
            
            filename = f"operation_logs_{timezone.now().strftime('%Y%m%d_%H%M%S')}.csv"
            response = Response(
                content=output.getvalue(),
                content_type='text/csv',
                headers={
                    'Content-Disposition': f'attachment; filename="{filename}"'
                }
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Failed to export operation logs: {e}")
            return ApiResponse.error(message=f'导出失败: {str(e)}')

    @action(detail=False, methods=['delete'])
    def cleanup(self, request):
        """
        清理历史日志
        
        参数：
        - days: 保留最近N天的日志（默认90天）
        
        仅超级管理员可执行
        """
        user = request.user
        
        if not (user.is_superuser or 
               getattr(user, 'is_system_admin', False) or
               getattr(user, 'is_super_admin', False)):
            return ApiResponse.error(message='无权限执行此操作', code=403)
        
        try:
            days = int(request.data.get('days', 90))
            days = max(days, 30)  # 至少保留30天
            
            cutoff_date = timezone.now() - timedelta(days=days)
            
            deleted_count, _ = SystemOperationLog.objects.filter(
                created_at__lt=cutoff_date
            ).delete()
            
            OperationLogService.log(
                request=request,
                module='system',
                operation_type='system_setting_update',
                description=f'清理了 {deleted_count} 条 {days} 天前的历史操作日志'
            )
            
            return ApiResponse.success(
                data={'deleted_count': deleted_count},
                message=f'成功清理 {deleted_count} 条历史日志'
            )
            
        except Exception as e:
            logger.error(f"Failed to cleanup operation logs: {e}")
            return ApiResponse.error(message=str(e))

# 需要导入 models
from django.db import models
