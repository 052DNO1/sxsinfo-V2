"""
设备视图
"""

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from drf_spectacular.utils import extend_schema
from common.responses import ApiResponse
from common.paginations import StandardPagination
from apps.laboratories.models import Equipment
from apps.laboratories.serializers import (
    EquipmentSerializer, EquipmentCreateSerializer, EquipmentUpdateSerializer, BatchDeleteSerializer
)
from apps.laboratories.services import EquipmentService


class EquipmentViewSet(viewsets.ModelViewSet):
    """设备视图集"""

    permission_classes = [IsAuthenticated]
    pagination_class = StandardPagination
    serializer_class = EquipmentSerializer

    def get_queryset(self):
        return Equipment.objects.filter(is_deleted=False)

    def get_serializer_class(self):
        if self.action == 'create':
            return EquipmentCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return EquipmentUpdateSerializer
        return EquipmentSerializer

    @extend_schema(description='获取设备列表')
    def list(self, request):
        service = EquipmentService()
        result = service.get_equipment_list(
            requester=request.user,
            laboratory_id=request.query_params.get('laboratory_id'),
            category=request.query_params.get('category'),
            status=request.query_params.get('status'),
            search=request.query_params.get('search'),
            page=int(request.query_params.get('page', 1)),
            page_size=int(request.query_params.get('page_size', 20)),
            no_page=request.query_params.get('nopage') == 'true'
        )
        return ApiResponse.success(data=result)
    
    @extend_schema(description='获取设备详情')
    def retrieve(self, request, pk=None):
        service = EquipmentService()
        result = service.get_equipment_detail(requester=request.user, equipment_id=pk)
        return ApiResponse.success(data=result)
    
    @extend_schema(description='创建设备')
    def create(self, request):
        serializer = EquipmentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        service = EquipmentService()
        equipment = service.create_equipment(
            requester=request.user,
            data=serializer.validated_data,
            request=request
        )

        return ApiResponse.created(
            data={'id': equipment.id, 'code': equipment.code},
            message='设备创建成功'
        )
    
    @extend_schema(description='更新设备')
    def update(self, request, pk=None, *args, **kwargs):
        service = EquipmentService()
        
        try:
            equipment = Equipment.objects.get(id=pk, is_deleted=False)
        except Equipment.DoesNotExist:
            return ApiResponse.error(message='设备不存在', code=404)
        
        # DRF PATCH 会以 partial=True 调用本方法；同时保留按请求体字段数推断的兜底
        partial = kwargs.get('partial', len(request.data) < len(self.get_serializer_class().Meta.fields))
        serializer = self.get_serializer(instance=equipment, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        equipment = service.update_equipment(
            requester=request.user,
            equipment_id=pk,
            data=serializer.validated_data,
            request=request
        )

        return ApiResponse.success(
            data={'id': equipment.id},
            message='设备更新成功'
        )
    
    @extend_schema(description='删除设备')
    def destroy(self, request, pk=None):
        service = EquipmentService()
        service.delete_equipment(requester=request.user, equipment_id=pk, request=request)
        return ApiResponse.success(message='设备删除成功')
    
    @extend_schema(
        request=BatchDeleteSerializer,
        description='批量删除设备'
    )
    @action(methods=['post'], detail=False)
    def batch_delete(self, request):
        serializer = BatchDeleteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        service = EquipmentService()
        result = service.batch_delete_equipments(
            requester=request.user,
            equipment_ids=serializer.validated_data['ids']
        )
        
        message = f"成功删除 {result['deleted_count']} 台设备"
        if result['failed_count'] > 0:
            message += f"，{result['failed_count']} 台删除失败"
        
        return ApiResponse.success(data=result, message=message)
    
    @extend_schema(description='获取设备类别选项')
    @action(methods=['get'], detail=False)
    def category_options(self, request):
        service = EquipmentService()
        options = service.get_category_options()
        return ApiResponse.success(data={'categories': options})
    
    @extend_schema(description='获取设备状态选项')
    @action(methods=['get'], detail=False)
    def status_options(self, request):
        service = EquipmentService()
        options = service.get_status_options()
        return ApiResponse.success(data={'statuses': options})
