"""
实训室记录汇总服务
"""

from django.db import models
from django.core.paginator import Paginator
from apps.core.exceptions import NotFoundError, PermissionDenied
from apps.laboratories.models import Laboratory
from apps.records.models import UsageRecord
from apps.maintenance.models import WorkOrder
from apps.schedules.models import Semester


class LaboratorySummaryService:
    """实训室记录汇总服务"""

    def get_laboratory_summary(
        self,
        requester,
        laboratory_id: int,
        semester_id: int = None
    ) -> dict:
        try:
            laboratory = Laboratory.objects.get(id=laboratory_id, is_deleted=False)
        except Laboratory.DoesNotExist:
            raise NotFoundError('实训室不存在')
        
        if not self._can_view_laboratory(requester, laboratory):
            raise PermissionDenied('无权限查看该实训室')
        
        if not semester_id:
            semester = Semester.get_current()
            if semester:
                semester_id = semester.id
        
        usage_records = UsageRecord.objects.filter(
            laboratory=laboratory,
            is_deleted=False
        )
        
        work_orders = WorkOrder.objects.filter(
            laboratory=laboratory,
            is_deleted=False
        )
        
        if semester_id:
            usage_records = usage_records.filter(semester_id=semester_id)
            work_orders = work_orders.filter(semester_id=semester_id)
        
        usage_records = usage_records.select_related('teacher').order_by('-usage_date')
        work_orders = work_orders.select_related('reporter', 'handler').order_by('-reported_at')
        
        total_class_hours = usage_records.aggregate(
            total=models.Sum('class_hours')
        )['total'] or 0
        
        total_students = usage_records.aggregate(
            total=models.Sum('student_count')
        )['total'] or 0
        
        return {
            'laboratory': {
                'id': laboratory.id,
                'name': laboratory.name,
                'code': laboratory.code,
                'location': laboratory.location,
                'capacity': laboratory.capacity,
            },
            'semester_id': semester_id,
            'statistics': {
                'total_records': usage_records.count(),
                'total_class_hours': total_class_hours,
                'total_students': total_students,
                'total_work_orders': work_orders.count(),
                'pending_orders': work_orders.filter(status='pending').count(),
                'completed_orders': work_orders.filter(status='completed').count(),
            },
            'recent_records': [
                {
                    'id': r.id,
                    'usage_date': r.usage_date.strftime('%Y-%m-%d'),
                    'time_slot': r.time_slot,
                    'class_hours': r.class_hours,
                    'teacher_name': r.teacher.nickname if r.teacher else '',
                    'class_name': r.class_name,
                    'student_count': r.student_count,
                    'content': r.content,
                    'device_status': r.device_status,
                }
                for r in usage_records[:10]
            ],
            'recent_work_orders': [
                {
                    'id': o.id,
                    'title': o.title,
                    'status': o.status,
                    'priority': o.priority,
                    'reporter_name': o.reporter.nickname if o.reporter else '',
                    'handler_name': o.handler.nickname if o.handler else '',
                    'reported_at': o.reported_at.strftime('%Y-%m-%d %H:%M'),
                    'description': o.description[:100] if o.description else '',
                }
                for o in work_orders[:10]
            ],
        }

    def get_all_laboratories_summary(
        self,
        requester,
        semester_id: int = None,
        page: int = 1,
        page_size: int = 20
    ) -> dict:
        queryset = Laboratory.objects.filter(is_deleted=False)
        
        if requester.is_department_admin and not requester.is_super_admin:
            queryset = queryset.filter(department_id=requester.department_id)
        elif requester.is_laboratory_admin and not requester.is_super_admin:
            queryset = queryset.filter(admin=requester)
        
        if not semester_id:
            semester = Semester.get_current()
            if semester:
                semester_id = semester.id
        
        summaries = []
        for lab in queryset:
            usage_records = UsageRecord.objects.filter(
                laboratory=lab, is_deleted=False
            )
            work_orders = WorkOrder.objects.filter(
                laboratory=lab, is_deleted=False
            )
            
            if semester_id:
                usage_records = usage_records.filter(semester_id=semester_id)
                work_orders = work_orders.filter(semester_id=semester_id)
            
            summaries.append({
                'id': lab.id,
                'name': lab.name,
                'code': lab.code,
                'location': lab.location,
                'capacity': lab.capacity,
                'total_records': usage_records.count(),
                'total_class_hours': usage_records.aggregate(
                    total=models.Sum('class_hours')
                )['total'] or 0,
                'total_work_orders': work_orders.count(),
                'pending_orders': work_orders.filter(status='pending').count(),
            })
        
        paginator = Paginator(summaries, page_size)
        page_obj = paginator.get_page(page)
        
        return {
            'list': list(page_obj),
            'total': paginator.count,
            'page': page,
            'page_size': page_size,
            'total_pages': paginator.num_pages,
            'semester_id': semester_id,
        }

    def _can_view_laboratory(self, user, laboratory: Laboratory) -> bool:
        if user.is_super_admin:
            return True
        if user.is_department_admin:
            return laboratory.department_id == user.department_id
        if user.is_laboratory_admin:
            return laboratory.admin_id == user.id
        return False
