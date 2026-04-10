"""
工单视图
"""

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from drf_spectacular.utils import extend_schema
from common.responses import ApiResponse
from common.paginations import StandardPagination
from apps.maintenance.models import WorkOrder
from apps.maintenance.serializers import (
    WorkOrderSerializer, WorkOrderCreateSerializer, WorkOrderUpdateSerializer,
    WorkOrderAssignSerializer, WorkOrderCompleteSerializer, WorkOrderCloseSerializer,
    BatchDeleteSerializer
)
from apps.maintenance.services import WorkOrderService


class WorkOrderViewSet(viewsets.ModelViewSet):
    """工单视图集"""
    
    permission_classes = [IsAuthenticated]
    pagination_class = StandardPagination
    serializer_class = WorkOrderSerializer
    
    def get_queryset(self):
        return WorkOrder.objects.filter(is_deleted=False)
    
    def get_serializer_class(self):
        if self.action == 'create':
            return WorkOrderCreateSerializer
        if self.action in ['update', 'partial_update']:
            return WorkOrderUpdateSerializer
        return WorkOrderSerializer
    
    @extend_schema(description='获取工单列表')
    def list(self, request):
        service = WorkOrderService()
        result = service.get_work_order_list(
            requester=request.user,
            laboratory_id=request.query_params.get('laboratory_id'),
            status=request.query_params.get('status'),
            maintenance_type=request.query_params.get('maintenance_type'),
            handler_id=request.query_params.get('handler_id'),
            reporter_id=request.query_params.get('reporter_id'),
            search=request.query_params.get('search'),
            page=int(request.query_params.get('page', 1)),
            page_size=int(request.query_params.get('page_size', 20)),
            no_page=request.query_params.get('nopage') == 'true'
        )
        return ApiResponse.success(data=result)
    
    @extend_schema(description='获取工单详情')
    def retrieve(self, request, pk=None):
        service = WorkOrderService()
        result = service.get_work_order_detail(requester=request.user, order_id=pk)
        return ApiResponse.success(data=result)
    
    @extend_schema(description='创建工单')
    def create(self, request):
        serializer = WorkOrderCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        service = WorkOrderService()
        order = service.create_work_order(
            requester=request.user,
            data=serializer.validated_data
        )
        
        return ApiResponse.created(
            data={'id': order.id},
            message='工单创建成功'
        )
    
    @extend_schema(description='更新工单')
    def update(self, request, pk=None):
        serializer = WorkOrderUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        service = WorkOrderService()
        order = service.update_work_order(
            requester=request.user,
            order_id=pk,
            data=serializer.validated_data
        )
        
        return ApiResponse.success(
            data={'id': order.id},
            message='工单更新成功'
        )
    
    @extend_schema(description='删除工单')
    def destroy(self, request, pk=None):
        service = WorkOrderService()
        service.delete_work_order(requester=request.user, order_id=pk)
        return ApiResponse.success(message='工单删除成功')
    
    @extend_schema(
        request=BatchDeleteSerializer,
        description='批量删除工单'
    )
    @action(methods=['post'], detail=False)
    def batch_delete(self, request):
        serializer = BatchDeleteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        service = WorkOrderService()
        result = service.batch_delete_orders(
            requester=request.user,
            order_ids=serializer.validated_data['ids']
        )
        
        message = f"成功删除 {result['deleted_count']} 个工单"
        if result['failed_count'] > 0:
            message += f"，{result['failed_count']} 个删除失败"
        
        return ApiResponse.success(data=result, message=message)
    
    @extend_schema(
        request=WorkOrderAssignSerializer,
        description='分配工单'
    )
    @action(methods=['post'], detail=True)
    def assign(self, request, pk=None):
        serializer = WorkOrderAssignSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        service = WorkOrderService()
        order = service.assign_order(
            requester=request.user,
            order_id=pk,
            handler_id=serializer.validated_data['handler_id']
        )
        
        return ApiResponse.success(
            data={'id': order.id, 'status': order.status},
            message='工单分配成功'
        )
    
    @extend_schema(description='开始处理工单')
    @action(methods=['post'], detail=True)
    def start_handle(self, request, pk=None):
        service = WorkOrderService()
        order = service.start_handle(requester=request.user, order_id=pk)
        
        return ApiResponse.success(
            data={'id': order.id, 'status': order.status},
            message='已开始处理工单'
        )
    
    @extend_schema(
        request=WorkOrderCompleteSerializer,
        description='完成工单'
    )
    @action(methods=['post'], detail=True)
    def complete(self, request, pk=None):
        serializer = WorkOrderCompleteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        service = WorkOrderService()
        order = service.complete_order(
            requester=request.user,
            order_id=pk,
            solution=serializer.validated_data['solution']
        )
        
        return ApiResponse.success(
            data={'id': order.id, 'status': order.status},
            message='工单已完成'
        )
    
    @extend_schema(
        request=WorkOrderCloseSerializer,
        description='关闭工单'
    )
    @action(methods=['post'], detail=True)
    def close(self, request, pk=None):
        serializer = WorkOrderCloseSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        service = WorkOrderService()
        order = service.close_order(
            requester=request.user,
            order_id=pk,
            feedback=serializer.validated_data.get('feedback', '')
        )
        
        return ApiResponse.success(
            data={'id': order.id, 'status': order.status},
            message='工单已关闭'
        )
    
    @extend_schema(description='获取表单选项')
    @action(methods=['get'], detail=False)
    def form_options(self, request):
        service = WorkOrderService()
        result = service.get_form_options(
            requester=request.user,
            laboratory_id=request.query_params.get('laboratory_id')
        )
        return ApiResponse.success(data=result)
