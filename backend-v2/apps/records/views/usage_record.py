"""
使用记录视图
"""

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from drf_spectacular.utils import extend_schema
from common.responses import ApiResponse
from common.paginations import StandardPagination
from apps.records.models import UsageRecord
from apps.records.serializers import (
    UsageRecordSerializer, UsageRecordCreateSerializer,
    UsageRecordUpdateSerializer, BatchDeleteSerializer
)
from apps.records.services import UsageRecordService


class UsageRecordViewSet(viewsets.ModelViewSet):
    """使用记录视图集"""
    
    permission_classes = [IsAuthenticated]
    pagination_class = StandardPagination
    serializer_class = UsageRecordSerializer
    
    def get_queryset(self):
        return UsageRecord.objects.filter(is_deleted=False)
    
    def get_serializer_class(self):
        if self.action == 'create':
            return UsageRecordCreateSerializer
        if self.action in ['update', 'partial_update']:
            return UsageRecordUpdateSerializer
        return UsageRecordSerializer
    
    @extend_schema(description='获取使用记录列表')
    def list(self, request):
        service = UsageRecordService()
        result = service.get_record_list(
            requester=request.user,
            laboratory_id=request.query_params.get('laboratory_id'),
            teacher_id=request.query_params.get('teacher_id'),
            semester_id=request.query_params.get('semester_id'),
            start_date=request.query_params.get('start_date'),
            end_date=request.query_params.get('end_date'),
            search=request.query_params.get('search'),
            page=int(request.query_params.get('page', 1)),
            page_size=int(request.query_params.get('page_size', 20)),
            no_page=request.query_params.get('nopage') == 'true'
        )
        return ApiResponse.success(data=result)
    
    @extend_schema(description='获取使用记录详情')
    def retrieve(self, request, pk=None):
        service = UsageRecordService()
        result = service.get_record_detail(requester=request.user, record_id=pk)
        return ApiResponse.success(data=result)
    
    @extend_schema(description='创建使用记录')
    def create(self, request):
        serializer = UsageRecordCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        service = UsageRecordService()
        record = service.create_record(
            requester=request.user,
            data=serializer.validated_data
        )
        
        response_data = {'id': record.id}
        
        if record.device_status and record.device_status.strip() != '正常':
            response_data['redirect_to_report'] = True
            response_data['report_info'] = {
                'laboratory_id': record.laboratory_id,
                'laboratory_name': record.laboratory.name,
                'usage_date': record.usage_date.strftime('%Y-%m-%d'),
                'note': record.note or '',
            }
            return ApiResponse.created(
                data=response_data,
                message='使用记录创建成功，设备状态异常，请填写维护上报'
            )
        
        return ApiResponse.created(
            data=response_data,
            message='使用记录创建成功'
        )
    
    @extend_schema(description='更新使用记录')
    def update(self, request, pk=None):
        serializer = UsageRecordUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        service = UsageRecordService()
        record = service.update_record(
            requester=request.user,
            record_id=pk,
            data=serializer.validated_data
        )
        
        return ApiResponse.success(
            data={'id': record.id},
            message='使用记录更新成功'
        )
    
    @extend_schema(description='删除使用记录')
    def destroy(self, request, pk=None):
        service = UsageRecordService()
        result = service.delete_record(requester=request.user, record_id=pk)
        return ApiResponse.success(message=result['message'])
    
    @extend_schema(
        request=BatchDeleteSerializer,
        description='批量删除使用记录'
    )
    @action(methods=['post'], detail=False)
    def batch_delete(self, request):
        serializer = BatchDeleteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        service = UsageRecordService()
        result = service.batch_delete_records(
            requester=request.user,
            record_ids=serializer.validated_data['ids']
        )
        
        message = f"成功删除 {result['deleted_count']} 条使用记录"
        if result['failed_count'] > 0:
            message += f"，{result['failed_count']} 条删除失败"
        
        return ApiResponse.success(data=result, message=message)
    
    @extend_schema(description='获取表单选项')
    @action(methods=['get'], detail=False)
    def form_options(self, request):
        service = UsageRecordService()
        result = service.get_form_options(requester=request.user)
        return ApiResponse.success(data=result)
