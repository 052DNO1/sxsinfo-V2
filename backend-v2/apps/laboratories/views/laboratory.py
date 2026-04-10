"""
实训室视图
"""

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from drf_spectacular.utils import extend_schema, OpenApiResponse
from common.responses import ApiResponse
from common.paginations import StandardPagination
from apps.laboratories.models import Laboratory
from apps.laboratories.serializers import (
    LaboratorySerializer, LaboratoryCreateSerializer,
    LaboratoryUpdateSerializer, BatchDeleteSerializer
)
from apps.laboratories.services import LaboratoryService, LaboratorySummaryService


class LaboratoryViewSet(viewsets.ModelViewSet):
    """实训室视图集"""
    
    permission_classes = [IsAuthenticated]
    pagination_class = StandardPagination
    serializer_class = LaboratorySerializer
    
    def get_queryset(self):
        return Laboratory.objects.filter(is_deleted=False)
    
    def get_serializer_class(self):
        if self.action == 'create':
            return LaboratoryCreateSerializer
        if self.action in ['update', 'partial_update']:
            return LaboratoryUpdateSerializer
        return LaboratorySerializer
    
    @extend_schema(description='获取实训室列表')
    def list(self, request):
        service = LaboratoryService()
        result = service.get_laboratory_list(
            requester=request.user,
            department_id=request.query_params.get('department_id'),
            status=request.query_params.get('status'),
            laboratory_type=request.query_params.get('laboratory_type'),
            search=request.query_params.get('search'),
            page=int(request.query_params.get('page', 1)),
            page_size=int(request.query_params.get('page_size', 20)),
            no_page=request.query_params.get('nopage') == 'true'
        )
        return ApiResponse.success(data=result)
    
    @extend_schema(description='获取实训室详情')
    def retrieve(self, request, pk=None):
        service = LaboratoryService()
        result = service.get_laboratory_detail(requester=request.user, laboratory_id=pk)
        return ApiResponse.success(data=result)
    
    @extend_schema(description='创建实训室')
    def create(self, request):
        serializer = LaboratoryCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        service = LaboratoryService()
        laboratory = service.create_laboratory(
            requester=request.user,
            data=serializer.validated_data
        )
        
        return ApiResponse.created(
            data={'id': laboratory.id, 'code': laboratory.code},
            message='实训室创建成功'
        )
    
    @extend_schema(description='更新实训室')
    def update(self, request, pk=None):
        try:
            laboratory = Laboratory.objects.get(id=pk, is_deleted=False)
        except Laboratory.DoesNotExist:
            return ApiResponse.not_found(message='实训室不存在')
        
        serializer = LaboratoryUpdateSerializer(instance=laboratory, data=request.data)
        serializer.is_valid(raise_exception=True)
        
        service = LaboratoryService()
        laboratory = service.update_laboratory(
            requester=request.user,
            laboratory_id=pk,
            data=serializer.validated_data
        )
        
        return ApiResponse.success(
            data={'id': laboratory.id},
            message='实训室更新成功'
        )
    
    @extend_schema(description='删除实训室')
    def destroy(self, request, pk=None):
        service = LaboratoryService()
        result = service.delete_laboratory(requester=request.user, laboratory_id=pk)
        return ApiResponse.success(message=result['message'])
    
    @extend_schema(
        request=BatchDeleteSerializer,
        description='批量删除实训室'
    )
    @action(methods=['post'], detail=False)
    def batch_delete(self, request):
        serializer = BatchDeleteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        service = LaboratoryService()
        result = service.batch_delete_laboratories(
            requester=request.user,
            laboratory_ids=serializer.validated_data['ids']
        )
        
        message = f"成功删除 {result['deleted_count']} 个实训室"
        if result['failed_count'] > 0:
            message += f"，{result['failed_count']} 个删除失败"
        
        return ApiResponse.success(data=result, message=message)
    
    @extend_schema(description='获取管理员选项')
    @action(methods=['get'], detail=False)
    def admin_options(self, request):
        service = LaboratoryService()
        options = service.get_admin_options(requester=request.user)
        return ApiResponse.success(data={'admins': options})
    
    @extend_schema(description='获取实训室选项列表')
    @action(methods=['get'], detail=False)
    def options(self, request):
        service = LaboratoryService()
        options = service.get_laboratory_options(requester=request.user)
        return ApiResponse.success(data={'options': options})
    
    @extend_schema(description='获取实训室记录汇总')
    @action(methods=['get'], detail=True)
    def summary(self, request, pk=None):
        service = LaboratorySummaryService()
        result = service.get_laboratory_summary(
            requester=request.user,
            laboratory_id=pk,
            semester_id=request.query_params.get('semester_id')
        )
        return ApiResponse.success(data=result)
    
    @extend_schema(description='获取所有实训室汇总')
    @action(methods=['get'], detail=False)
    def all_summary(self, request):
        service = LaboratorySummaryService()
        result = service.get_all_laboratories_summary(
            requester=request.user,
            semester_id=request.query_params.get('semester_id'),
            page=int(request.query_params.get('page', 1)),
            page_size=int(request.query_params.get('page_size', 20))
        )
        return ApiResponse.success(data=result)
