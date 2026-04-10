"""
工单中心视图
"""

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema
from common.responses import ApiResponse
from apps.maintenance.services.work_order_center_service import WorkOrderCenterService


class WorkOrderCenterListView(APIView):
    """工单中心列表视图"""
    permission_classes = [IsAuthenticated]

    @extend_schema(description='获取工单中心列表')
    def get(self, request):
        service = WorkOrderCenterService()
        result = service.get_work_order_list(
            requester=request.user,
            laboratory_id=request.query_params.get('laboratory_id'),
            status=request.query_params.get('status'),
            search=request.query_params.get('search'),
            page=int(request.query_params.get('page', 1)),
            page_size=int(request.query_params.get('page_size', 10)),
            hidden=request.query_params.get('hidden') == 'true'
        )
        return ApiResponse.success(data=result)


class WorkOrderCenterDetailView(APIView):
    """工单中心详情视图"""
    permission_classes = [IsAuthenticated]

    @extend_schema(description='获取工单详情')
    def get(self, request, order_id):
        service = WorkOrderCenterService()
        result = service.get_work_order_detail(
            requester=request.user,
            order_id=order_id
        )
        return ApiResponse.success(data={'order': result})

    @extend_schema(description='更新工单状态')
    def post(self, request, order_id):
        service = WorkOrderCenterService()
        status = request.data.get('status')
        memo = request.data.get('memo', '')
        
        if not status:
            return ApiResponse.error(message='状态不能为空')
        
        order = service.update_order_status(
            requester=request.user,
            order_id=order_id,
            status=status,
            memo=memo
        )
        
        return ApiResponse.success(
            data={'id': order.id, 'status': order.status},
            message='状态更新成功'
        )


class WorkOrderCenterHideView(APIView):
    """工单中心隐藏视图"""
    permission_classes = [IsAuthenticated]

    @extend_schema(description='隐藏工单')
    def post(self, request, order_id):
        service = WorkOrderCenterService()
        service.hide_order(
            requester=request.user,
            order_id=order_id
        )
        return ApiResponse.success(message='已从工单中心隐藏')
