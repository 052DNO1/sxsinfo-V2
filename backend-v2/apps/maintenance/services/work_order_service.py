"""
工单服务
"""

from django.db import models, transaction
from django.core.paginator import Paginator
from django.utils import timezone
from apps.core.exceptions import NotFoundError, PermissionDenied, ValidationError
from apps.core.constants import WorkOrderStatus, MaintenanceType
from apps.maintenance.models import WorkOrder
from apps.schedules.models import Semester
from apps.laboratories.models import Laboratory
from apps.users.models import User


class WorkOrderService:
    """工单服务"""

    def get_work_order_list(
        self,
        requester,
        laboratory_id: int = None,
        status: str = None,
        maintenance_type: int = None,
        maintenance_type_not: int = None,
        handler_id: int = None,
        reporter_id: int = None,
        search: str = None,
        page: int = 1,
        page_size: int = 20,
        no_page: bool = False
    ) -> dict:
        queryset = WorkOrder.objects.select_related(
            'laboratory', 'reporter', 'handler', 'semester', 'equipment'
        ).filter(is_deleted=False)
        
        if requester.is_department_admin and not requester.is_super_admin:
            queryset = queryset.filter(laboratory__department_id=requester.department_id)
        elif requester.is_laboratory_admin and not requester.is_super_admin:
            queryset = queryset.filter(laboratory__admin=requester)
        elif requester.is_teacher and not requester.is_super_admin:
            queryset = queryset.filter(reporter=requester)
        
        if laboratory_id:
            queryset = queryset.filter(laboratory_id=laboratory_id)
        if status:
            queryset = queryset.filter(status=status)
        if maintenance_type:
            queryset = queryset.filter(maintenance_type=maintenance_type)
        if maintenance_type_not:
            queryset = queryset.exclude(maintenance_type=maintenance_type_not)
        if handler_id:
            queryset = queryset.filter(handler_id=handler_id)
        if reporter_id:
            queryset = queryset.filter(reporter_id=reporter_id)
        if search:
            queryset = queryset.filter(
                models.Q(title__icontains=search) |
                models.Q(description__icontains=search) |
                models.Q(laboratory__name__icontains=search) |
                models.Q(laboratory__code__icontains=search)
            )
        
        queryset = queryset.order_by('-reported_at')
        
        if no_page:
            return {
                'list': [self._format_order(o) for o in queryset],
                'total': queryset.count(),
            }
        
        paginator = Paginator(queryset, page_size)
        page_obj = paginator.get_page(page)
        
        return {
            'list': [self._format_order(o) for o in page_obj],
            'total': paginator.count,
            'page': page,
            'page_size': page_size,
            'total_pages': paginator.num_pages,
        }

    def get_work_order_detail(self, requester, order_id: int) -> dict:
        try:
            order = WorkOrder.objects.select_related(
                'laboratory', 'reporter', 'handler', 'semester', 'equipment'
            ).get(id=order_id, is_deleted=False)
        except WorkOrder.DoesNotExist:
            raise NotFoundError('工单不存在')
        
        if not self._can_view_order(requester, order):
            raise PermissionDenied('无权限查看该工单')
        
        return self._format_order_detail(order)

    @transaction.atomic
    def create_work_order(self, requester, data: dict) -> WorkOrder:
        laboratory_id = data.get('laboratory_id')
        if not laboratory_id:
            raise ValidationError('实训室为必填项')
        
        try:
            laboratory = Laboratory.objects.get(id=laboratory_id, is_deleted=False)
        except Laboratory.DoesNotExist:
            raise ValidationError('指定的实训室不存在')
        
        semester = Semester.get_current()
        if not semester:
            raise ValidationError('未设置当前学期')
        
        title = data.get('title', '').strip()
        if not title:
            raise ValidationError('工单标题为必填项')
        
        description = data.get('description', '').strip()
        if not description:
            raise ValidationError('问题描述为必填项')
        
        maintenance_type = data.get('maintenance_type', MaintenanceType.REPAIR)
        
        order = WorkOrder.objects.create(
            title=title,
            description=description,
            laboratory_id=laboratory_id,
            equipment_id=data.get('equipment_id'),
            semester=semester,
            maintenance_type=maintenance_type,
            priority=data.get('priority', 1),
            reporter=requester,
            handle_note=data.get('handle_note', ''),
            order_number=WorkOrder.generate_order_number(maintenance_type),
        )
        
        return order

    @transaction.atomic
    def update_work_order(self, requester, order_id: int, data: dict) -> WorkOrder:
        try:
            order = WorkOrder.objects.select_related('laboratory').get(
                id=order_id, is_deleted=False
            )
        except WorkOrder.DoesNotExist:
            raise NotFoundError('工单不存在')
        
        if not self._can_edit_order(requester, order):
            raise PermissionDenied('无权限修改该工单')
        
        if order.status == WorkOrderStatus.CLOSED:
            raise ValidationError('工单已关闭，无法修改')
        
        for field in ['title', 'description', 'priority', 'handle_note']:
            if field in data:
                setattr(order, field, data[field])
        
        if 'maintenance_type' in data:
            order.maintenance_type = data['maintenance_type']
        
        order.save()
        return order

    @transaction.atomic
    def delete_work_order(self, requester, order_id: int) -> bool:
        try:
            order = WorkOrder.objects.select_related('laboratory').get(
                id=order_id, is_deleted=False
            )
        except WorkOrder.DoesNotExist:
            raise NotFoundError('工单不存在')
        
        if not self._can_delete_order(requester, order):
            raise PermissionDenied('无权限删除该工单')
        
        if order.status not in [WorkOrderStatus.PENDING, WorkOrderStatus.CLOSED]:
            raise ValidationError('只能删除待处理或已关闭的工单')
        
        if order.is_archived:
            order.is_deleted = True
            order.save(update_fields=['is_deleted'])
        else:
            order.delete()
        return True

    @transaction.atomic
    def batch_delete_orders(self, requester, order_ids: list) -> dict:
        deleted_count = 0
        failed_list = []
        
        for order_id in order_ids:
            try:
                self.delete_work_order(requester, order_id)
                deleted_count += 1
            except Exception as e:
                failed_list.append({'id': order_id, 'reason': str(e)})
        
        return {
            'deleted_count': deleted_count,
            'failed_count': len(failed_list),
            'failed_list': failed_list,
        }

    @transaction.atomic
    def assign_order(self, requester, order_id: int, handler_id: int) -> WorkOrder:
        try:
            order = WorkOrder.objects.select_related('laboratory').get(
                id=order_id, is_deleted=False
            )
        except WorkOrder.DoesNotExist:
            raise NotFoundError('工单不存在')
        
        if not self._can_handle_order(requester, order):
            raise PermissionDenied('无权限分配该工单')
        
        if order.status not in [WorkOrderStatus.PENDING]:
            raise ValidationError('只能分配待处理的工单')
        
        try:
            handler = User.objects.get(id=handler_id, is_deleted=False, is_active=True)
        except User.DoesNotExist:
            raise NotFoundError('处理人不存在')
        
        order.handler = handler
        order.status = WorkOrderStatus.PROCESSING
        order.assigned_at = timezone.now()
        order.save()
        
        return order

    @transaction.atomic
    def start_handle(self, requester, order_id: int) -> WorkOrder:
        try:
            order = WorkOrder.objects.get(id=order_id, is_deleted=False)
        except WorkOrder.DoesNotExist:
            raise NotFoundError('工单不存在')
        
        if not self._can_handle_order(requester, order):
            raise PermissionDenied('无权限处理该工单')
        
        if order.status not in [WorkOrderStatus.PENDING, WorkOrderStatus.PROCESSING]:
            raise ValidationError('工单状态不允许开始处理')
        
        order.status = WorkOrderStatus.PROCESSING
        if not order.handler:
            order.handler = requester
        order.started_at = timezone.now()
        order.save()
        
        return order

    @transaction.atomic
    def complete_order(self, requester, order_id: int, solution: str) -> WorkOrder:
        try:
            order = WorkOrder.objects.get(id=order_id, is_deleted=False)
        except WorkOrder.DoesNotExist:
            raise NotFoundError('工单不存在')
        
        if not self._can_handle_order(requester, order):
            raise PermissionDenied('无权限完成该工单')
        
        if order.status != WorkOrderStatus.PROCESSING:
            raise ValidationError('只能完成处理中的工单')
        
        order.status = WorkOrderStatus.COMPLETED
        order.solution = solution
        order.completed_at = timezone.now()
        order.save()
        
        return order

    @transaction.atomic
    def close_order(self, requester, order_id: int, feedback: str = '') -> WorkOrder:
        try:
            order = WorkOrder.objects.get(id=order_id, is_deleted=False)
        except WorkOrder.DoesNotExist:
            raise NotFoundError('工单不存在')
        
        if not self._can_close_order(requester, order):
            raise PermissionDenied('无权限关闭该工单')
        
        if order.status != WorkOrderStatus.COMPLETED:
            raise ValidationError('只能关闭已完成的工单')
        
        order.status = WorkOrderStatus.CLOSED
        order.closed_at = timezone.now()
        if feedback:
            order.feedback = feedback
        order.save()
        
        return order

    def get_form_options(self, requester, laboratory_id: int = None) -> dict:
        current_semester = Semester.get_current()
        
        if requester.is_super_admin:
            laboratories = Laboratory.objects.filter(
                is_deleted=False, is_available=True
            ).values('id', 'name', 'code')
        elif requester.is_department_admin:
            laboratories = Laboratory.objects.filter(
                department_id=requester.department_id,
                is_deleted=False,
                is_available=True
            ).values('id', 'name', 'code')
        elif requester.is_laboratory_admin:
            laboratories = Laboratory.objects.filter(
                admin=requester,
                is_deleted=False,
                is_available=True
            ).values('id', 'name', 'code')
        else:
            laboratories = Laboratory.objects.filter(
                is_deleted=False, is_available=True
            ).values('id', 'name', 'code')
        
        maintenance_type_choices = [
            {'value': t.value, 'label': t.name} for t in MaintenanceType
        ]
        
        status_choices = [
            {'value': s.value, 'label': s.name} for s in WorkOrderStatus
        ]
        
        current_laboratory = None
        if laboratory_id:
            try:
                lab = Laboratory.objects.get(id=laboratory_id, is_deleted=False)
                current_laboratory = {
                    'id': lab.id,
                    'name': lab.name,
                    'code': lab.code
                }
            except Laboratory.DoesNotExist:
                pass
        
        return {
            'laboratories': list(laboratories),
            'maintenance_type_choices': maintenance_type_choices,
            'status_choices': status_choices,
            'current_laboratory': current_laboratory,
            'current_semester': {
                'id': current_semester.id,
                'name': current_semester.name
            } if current_semester else None,
        }

    def _can_view_order(self, user, order: WorkOrder) -> bool:
        if user.is_super_admin:
            return True
        if user.is_department_admin:
            return order.laboratory.department_id == user.department_id
        if user.is_laboratory_admin:
            return order.laboratory.admin_id == user.id
        if user.is_teacher:
            return order.reporter_id == user.id
        return False

    def _can_edit_order(self, user, order: WorkOrder) -> bool:
        if user.is_super_admin:
            return True
        if user.is_department_admin:
            return order.laboratory.department_id == user.department_id
        if user.is_laboratory_admin:
            return order.laboratory.admin_id == user.id
        if user.is_teacher:
            return order.reporter_id == user.id
        return False

    def _can_delete_order(self, user, order: WorkOrder) -> bool:
        if user.is_super_admin:
            return True
        if user.is_department_admin:
            return order.laboratory.department_id == user.department_id
        if user.is_laboratory_admin:
            return order.laboratory.admin_id == user.id
        return False

    def _can_handle_order(self, user, order: WorkOrder) -> bool:
        if user.is_super_admin:
            return True
        if user.is_department_admin:
            return order.laboratory.department_id == user.department_id
        if user.is_laboratory_admin:
            return order.laboratory.admin_id == user.id
        return False

    def _can_close_order(self, user, order: WorkOrder) -> bool:
        if user.is_super_admin:
            return True
        if user.is_department_admin:
            return order.laboratory.department_id == user.department_id
        if user.is_laboratory_admin:
            return order.laboratory.admin_id == user.id
        if user.is_teacher:
            return order.reporter_id == user.id
        return False

    def _format_order(self, order: WorkOrder) -> dict:
        status_map = {
            WorkOrderStatus.PENDING: '待处理',
            WorkOrderStatus.PROCESSING: '处理中',
            WorkOrderStatus.COMPLETED: '已完成',
            WorkOrderStatus.CLOSED: '已关闭',
        }
        
        maintenance_type_map = {
            MaintenanceType.ROUTINE: '检查维护',
            MaintenanceType.SAFETY: '安全检查',
            MaintenanceType.REPAIR: '设备维修',
        }
        
        if order.laboratory:
            lab_name = order.laboratory.name
            lab_code = order.laboratory.code
            room_number = order.laboratory.room_number
        else:
            lab_name = order.laboratory_name or ''
            lab_code = order.laboratory_code or ''
            room_number = ''
        
        return {
            'id': order.id,
            'order_number': order.order_number,
            'title': order.title,
            'description': order.description,
            'laboratory_id': order.laboratory_id,
            'laboratory_name': lab_name,
            'laboratory_code': lab_code,
            'room_number': room_number,
            'equipment_id': order.equipment_id,
            'equipment_name': order.equipment.name if order.equipment else None,
            'semester_id': order.semester_id,
            'semester_name': order.semester.name,
            'maintenance_type': order.maintenance_type,
            'maintenance_type_display': maintenance_type_map.get(
                order.maintenance_type, str(order.maintenance_type)
            ),
            'status': order.status,
            'status_display': status_map.get(order.status, order.status),
            'priority': order.priority,
            'reporter_id': order.reporter_id,
            'reporter_name': order.reporter.nickname if order.reporter else '',
            'handler_id': order.handler_id,
            'handler_name': order.handler.nickname if order.handler else '',
            'reported_at': order.reported_at.strftime('%Y-%m-%d %H:%M:%S'),
            'assigned_at': order.assigned_at.strftime('%Y-%m-%d %H:%M:%S') if order.assigned_at else None,
            'started_at': order.started_at.strftime('%Y-%m-%d %H:%M:%S') if order.started_at else None,
            'completed_at': order.completed_at.strftime('%Y-%m-%d %H:%M:%S') if order.completed_at else None,
            'closed_at': order.closed_at.strftime('%Y-%m-%d %H:%M:%S') if order.closed_at else None,
            'solution': order.solution,
            'handle_note': order.handle_note,
            'is_archived': order.is_archived,
        }

    def _format_order_detail(self, order: WorkOrder) -> dict:
        data = self._format_order(order)
        data.update({
            'rating': order.rating,
            'feedback': order.feedback,
            'created_at': order.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': order.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
        })
        return data
