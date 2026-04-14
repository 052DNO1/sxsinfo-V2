"""
维护记录视图
"""

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from drf_spectacular.utils import extend_schema
from common.responses import ApiResponse
from common.paginations import StandardPagination
from apps.maintenance.models import MaintenanceRecord
from apps.maintenance.serializers import (
    MaintenanceRecordSerializer, MaintenanceRecordCreateSerializer,
    MaintenanceRecordUpdateSerializer, BatchDeleteSerializer
)
from apps.maintenance.services import MaintenanceRecordService


class MaintenanceRecordViewSet(viewsets.ModelViewSet):
    """维护记录视图集"""
    
    permission_classes = [IsAuthenticated]
    pagination_class = StandardPagination
    serializer_class = MaintenanceRecordSerializer
    
    def get_queryset(self):
        return MaintenanceRecord.objects.filter(is_deleted=False)
    
    def get_serializer_class(self):
        if self.action == 'create':
            return MaintenanceRecordCreateSerializer
        if self.action in ['update', 'partial_update']:
            return MaintenanceRecordUpdateSerializer
        return MaintenanceRecordSerializer
    
    @extend_schema(description='获取维护记录列表')
    def list(self, request):
        service = MaintenanceRecordService()
        query_params = getattr(request, 'query_params', request.GET)
        result = service.get_record_list(
            requester=request.user,
            laboratory_id=query_params.get('laboratory_id'),
            maintainer_id=query_params.get('maintainer_id'),
            status=query_params.get('status'),
            order_type=query_params.get('order_type'),
            search=query_params.get('search'),
            page=int(query_params.get('page', 1)),
            page_size=int(query_params.get('page_size', 20)),
            no_page=query_params.get('nopage') == 'true'
        )
        return ApiResponse.success(data=result)
    
    @extend_schema(description='获取维护记录详情')
    def retrieve(self, request, pk=None):
        service = MaintenanceRecordService()
        result = service.get_record_detail(requester=request.user, record_id=pk)
        return ApiResponse.success(data=result)
    
    @extend_schema(description='创建维护记录')
    def create(self, request):
        serializer = MaintenanceRecordCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        service = MaintenanceRecordService()
        record = service.create_record(
            requester=request.user,
            data=serializer.validated_data
        )
        
        return ApiResponse.created(
            data={'id': record.id, 'order_number': record.order_number},
            message='维护记录创建成功'
        )
    
    @extend_schema(description='更新维护记录')
    def update(self, request, pk=None):
        serializer = MaintenanceRecordUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        service = MaintenanceRecordService()
        record = service.update_record(
            requester=request.user,
            record_id=pk,
            data=serializer.validated_data
        )
        
        return ApiResponse.success(
            data={'id': record.id},
            message='维护记录更新成功'
        )
    
    @extend_schema(description='删除维护记录')
    def destroy(self, request, pk=None):
        service = MaintenanceRecordService()
        service.delete_record(requester=request.user, record_id=pk)
        return ApiResponse.success(message='维护记录删除成功')
    
    @extend_schema(
        request=BatchDeleteSerializer,
        description='批量删除维护记录'
    )
    @action(methods=['post'], detail=False)
    def batch_delete(self, request):
        serializer = BatchDeleteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        service = MaintenanceRecordService()
        result = service.batch_delete_records(
            requester=request.user,
            record_ids=serializer.validated_data['ids']
        )
        
        message = f"成功删除 {result['deleted_count']} 条维护记录"
        if result['failed_count'] > 0:
            message += f"，{result['failed_count']} 条删除失败"
        
        return ApiResponse.success(data=result, message=message)
    
    @extend_schema(description='获取表单选项')
    @action(methods=['get'], detail=False)
    def form_options(self, request):
        service = MaintenanceRecordService()
        result = service.get_form_options(
            requester=request.user,
            laboratory_id=request.query_params.get('laboratory_id')
        )
        return ApiResponse.success(data=result)
