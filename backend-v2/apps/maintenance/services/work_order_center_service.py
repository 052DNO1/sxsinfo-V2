"""
工单中心服务
"""

from django.db import models, transaction
from django.core.paginator import Paginator
from django.utils import timezone
from apps.core.exceptions import NotFoundError, PermissionDenied, ValidationError
from apps.core.constants import WorkOrderStatus
from apps.maintenance.models import WorkOrder
from apps.schedules.models import Semester
from apps.laboratories.models import Laboratory
from apps.users.models import User


class WorkOrderCenterService:
    """工单中心服务"""

    def get_work_order_list(
        self,
        requester,
        laboratory_id: int = None,
        status: str = None,
        search: str = None,
        page: int = 1,
        page_size: int = 10,
        hidden: bool = False
    ) -> dict:
        queryset = WorkOrder.objects.select_related(
            'laboratory', 'reporter', 'handler'
        ).filter(is_deleted=False)
        
        if not requester.is_super_admin:
            if requester.is_department_admin:
                queryset = queryset.filter(laboratory__department_id=requester.department_id)
            elif requester.is_laboratory_admin:
                queryset = queryset.filter(laboratory__admin=requester)
            else:
                queryset = queryset.filter(reporter=requester)

        if laboratory_id:
            queryset = queryset.filter(laboratory_id=laboratory_id)
        if status:
            queryset = queryset.filter(status=status)
        if search:
            queryset = queryset.filter(
                models.Q(title__icontains=search) |
                models.Q(description__icontains=search) |
                models.Q(laboratory__name__icontains=search)
            )
        
        queryset = queryset.order_by('-reported_at')
        
        status_counts = {
            'pending': queryset.filter(status=WorkOrderStatus.PENDING).count(),
            'processing': queryset.filter(status=WorkOrderStatus.PROCESSING).count(),
            'completed': queryset.filter(status=WorkOrderStatus.COMPLETED).count(),
            'closed': queryset.filter(status=WorkOrderStatus.CLOSED).count(),
        }
        
        paginator = Paginator(queryset, page_size)
        page_obj = paginator.get_page(page)
        
        return {
            'orders': [self._format_order(o) for o in page_obj],
            'total': paginator.count,
            'page': page,
            'page_size': page_size,
            'total_pages': paginator.num_pages,
            'status_counts': status_counts,
        }

    def get_work_order_detail(self, requester, order_id: int) -> dict:
        try:
            order = WorkOrder.objects.select_related(
                'laboratory', 'reporter', 'handler'
            ).get(id=order_id, is_deleted=False)
        except WorkOrder.DoesNotExist:
            raise NotFoundError('工单不存在')
        
        if not self._can_view_order(requester, order):
            raise PermissionDenied('无权限查看该工单')
        
        return self._format_order_detail(order)

    @transaction.atomic
    def update_order_status(
        self,
        requester,
        order_id: int,
        status: str,
        memo: str = ''
    ) -> WorkOrder:
        try:
            order = WorkOrder.objects.select_related('laboratory').get(
                id=order_id, is_deleted=False
            )
        except WorkOrder.DoesNotExist:
            raise NotFoundError('工单不存在')
        
        if status == 'processing':
            if not requester.is_laboratory_admin and not requester.is_department_admin and not requester.is_super_admin:
                raise PermissionDenied('无权限处理工单')
            order.status = WorkOrderStatus.PROCESSING
            order.handler = requester
            order.started_at = timezone.now()
            order.save()
            
        elif status == 'completed':
            if not requester.is_laboratory_admin and not requester.is_department_admin and not requester.is_super_admin:
                raise PermissionDenied('无权限完成工单')
            order.status = WorkOrderStatus.COMPLETED
            order.completed_at = timezone.now()
            order.solution = memo
            order.save()
            
        elif status == 'closed':
            if order.reporter_id != requester.id and not requester.is_super_admin:
                raise PermissionDenied('只有上报人可以关闭工单')
            order.status = WorkOrderStatus.CLOSED
            order.closed_at = timezone.now()
            order.save()
            
        else:
            raise ValidationError('无效的状态')
        
        return order

    @transaction.atomic
    def hide_order(self, requester, order_id: int) -> bool:
        try:
            order = WorkOrder.objects.get(id=order_id, is_deleted=False)
        except WorkOrder.DoesNotExist:
            raise NotFoundError('工单不存在')
        
        if not self._can_view_order(requester, order):
            raise PermissionDenied('无权限操作该工单')
        
        order.hidden_in_center = True
        order.save(update_fields=['hidden_in_center'])
        
        return True

    def _can_view_order(self, user, order: WorkOrder) -> bool:
        if user.is_super_admin:
            return True
        if user.is_department_admin:
            return order.laboratory.department_id == user.department_id
        if user.is_laboratory_admin:
            return order.laboratory.admin_id == user.id
        return order.reporter_id == user.id

    def _format_order(self, order: WorkOrder) -> dict:
        status_map = {
            WorkOrderStatus.PENDING: '待处理',
            WorkOrderStatus.PROCESSING: '处理中',
            WorkOrderStatus.COMPLETED: '已完成',
            WorkOrderStatus.CLOSED: '已关闭',
        }
        
        return {
            'id': order.id,
            'order_number': order.order_number,
            'title': order.title,
            'laboratory_id': order.laboratory_id,
            'laboratory_name': order.laboratory.name if order.laboratory else '',
            'laboratory_code': order.laboratory.code if order.laboratory else '',
            'room_number': order.laboratory.room_number if order.laboratory else '',
            'reporter_id': order.reporter_id,
            'reporter_name': order.reporter.nickname if order.reporter else '',
            'handler_id': order.handler_id,
            'handler_name': order.handler.nickname if order.handler else '',
            'status': order.status,
            'status_display': status_map.get(order.status, order.status),
            'priority': order.priority,
            'maintenance_type': order.maintenance_type,
            'reported_at': order.reported_at.strftime('%Y-%m-%d %H:%M:%S'),
            'handle_memo': order.handle_note or '',
            'handle_time': order.started_at.strftime('%Y-%m-%d %H:%M') if order.started_at else '',
            'complete_time': order.completed_at.strftime('%Y-%m-%d %H:%M') if order.completed_at else '',
            'close_time': order.closed_at.strftime('%Y-%m-%d %H:%M') if order.closed_at else '',
        }

    def _format_order_detail(self, order: WorkOrder) -> dict:
        data = self._format_order(order)
        data.update({
            'description': order.description,
            'solution': order.solution,
            'feedback': order.feedback,
            'rating': order.rating,
        })
        return data
