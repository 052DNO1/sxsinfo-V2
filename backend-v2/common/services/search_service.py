"""
全局搜索服务
"""

from django.db import models
from apps.laboratories.models import Laboratory, Equipment
from apps.schedules.models import Schedule, Semester
from apps.records.models import UsageRecord
from apps.maintenance.models import WorkOrder
from apps.users.models import User


class GlobalSearchService:
    """全局搜索服务"""

    def search(self, requester, keyword: str, limit: int = 10) -> dict:
        if not keyword or not keyword.strip():
            return {'results': {}, 'total': 0}
        
        keyword = keyword.strip()
        all_results = []
        
        all_results.extend(self._search_laboratories(requester, keyword, limit))
        all_results.extend(self._search_schedules(requester, keyword, limit))
        all_results.extend(self._search_records(requester, keyword, limit))
        all_results.extend(self._search_work_orders(requester, keyword, limit))
        all_results.extend(self._search_equipment(requester, keyword, limit))
        all_results.extend(self._search_users(requester, keyword, limit))
        
        grouped_results = {}
        for item in all_results:
            type_name = item.get('type_name', '其他')
            if type_name not in grouped_results:
                grouped_results[type_name] = []
            grouped_results[type_name].append(item)
        
        return {
            'results': grouped_results,
            'total': len(all_results),
            'keyword': keyword,
        }

    def _search_laboratories(self, user, keyword: str, limit: int) -> list:
        queryset = Laboratory.objects.filter(
            is_deleted=False
        ).filter(
            models.Q(name__icontains=keyword) |
            models.Q(code__icontains=keyword) |
            models.Q(building__icontains=keyword)
        )
        
        if user.is_department_admin and not user.is_super_admin:
            queryset = queryset.filter(department_id=user.department_id)
        elif user.is_laboratory_admin and not user.is_super_admin:
            queryset = queryset.filter(admin=user)
        
        results = []
        for lab in queryset[:limit]:
            results.append({
                'type': 'laboratory',
                'type_name': '实训室',
                'resource_type': 'sxs',
                'action_type': 'view',
                'id': lab.id,
                'title': lab.name,
                'subtitle': f"{lab.code} - {lab.building or ''}",
            })
        
        return results

    def _search_schedules(self, user, keyword: str, limit: int) -> list:
        queryset = Schedule.objects.filter(
            is_deleted=False
        ).filter(
            models.Q(course_name__icontains=keyword) |
            models.Q(teacher_name__icontains=keyword) |
            models.Q(class_name__icontains=keyword)
        )
        
        if user.is_department_admin and not user.is_super_admin:
            queryset = queryset.filter(laboratory__department_id=user.department_id)
        elif user.is_laboratory_admin and not user.is_super_admin:
            queryset = queryset.filter(laboratory__admin=user)
        elif user.is_teacher and not user.is_super_admin:
            queryset = queryset.filter(teacher=user)
        
        results = []
        for schedule in queryset[:limit]:
            results.append({
                'type': 'schedule',
                'type_name': '课表',
                'resource_type': 'sxs_class',
                'action_type': 'view',
                'id': schedule.id,
                'title': schedule.course_name,
                'subtitle': f"{schedule.teacher_name or ''} - {schedule.laboratory.name if schedule.laboratory else ''}",
            })
        
        return results

    def _search_records(self, user, keyword: str, limit: int) -> list:
        queryset = UsageRecord.objects.filter(
            is_deleted=False
        ).filter(
            models.Q(content__icontains=keyword) |
            models.Q(class_name__icontains=keyword) |
            models.Q(laboratory__name__icontains=keyword)
        )
        
        if user.is_department_admin and not user.is_super_admin:
            queryset = queryset.filter(laboratory__department_id=user.department_id)
        elif user.is_laboratory_admin and not user.is_super_admin:
            queryset = queryset.filter(laboratory__admin=user)
        elif user.is_teacher and not user.is_super_admin:
            queryset = queryset.filter(teacher=user)
        
        results = []
        for record in queryset[:limit]:
            results.append({
                'type': 'record',
                'type_name': '使用记录',
                'resource_type': 'record',
                'action_type': 'view',
                'id': record.id,
                'title': f"{record.laboratory.name if record.laboratory else ''} - {record.class_name or ''}",
                'subtitle': record.usage_date.strftime('%Y-%m-%d') if record.usage_date else '',
            })
        
        return results

    def _search_work_orders(self, user, keyword: str, limit: int) -> list:
        queryset = WorkOrder.objects.filter(
            is_deleted=False
        ).filter(
            models.Q(title__icontains=keyword) |
            models.Q(description__icontains=keyword) |
            models.Q(laboratory__name__icontains=keyword)
        )
        
        if user.is_department_admin and not user.is_super_admin:
            queryset = queryset.filter(laboratory__department_id=user.department_id)
        elif user.is_laboratory_admin and not user.is_super_admin:
            queryset = queryset.filter(laboratory__admin=user)
        
        results = []
        for order in queryset[:limit]:
            results.append({
                'type': 'work_order',
                'type_name': '维护记录',
                'resource_type': 'maintain',
                'action_type': 'view',
                'id': order.id,
                'title': order.title,
                'subtitle': f"{order.laboratory.name if order.laboratory else ''} - {order.get_status_display()}",
            })
        
        return results

    def _search_equipment(self, user, keyword: str, limit: int) -> list:
        queryset = Equipment.objects.filter(
            is_deleted=False
        ).filter(
            models.Q(name__icontains=keyword) |
            models.Q(code__icontains=keyword) |
            models.Q(serial_number__icontains=keyword)
        )
        
        if user.is_department_admin and not user.is_super_admin:
            queryset = queryset.filter(laboratory__department_id=user.department_id)
        elif user.is_laboratory_admin and not user.is_super_admin:
            queryset = queryset.filter(laboratory__admin=user)
        
        results = []
        for eq in queryset[:limit]:
            results.append({
                'type': 'equipment',
                'type_name': '设备',
                'resource_type': 'equipment',
                'action_type': 'view',
                'id': eq.id,
                'title': eq.name,
                'subtitle': f"{eq.code} - {eq.laboratory.name if eq.laboratory else '未分配'}",
            })
        
        return results

    def _search_users(self, user, keyword: str, limit: int) -> list:
        if not user.is_department_admin and not user.is_super_admin:
            return []
        
        queryset = User.objects.filter(
            is_deleted=False
        ).filter(
            models.Q(username__icontains=keyword) |
            models.Q(nickname__icontains=keyword) |
            models.Q(phone__icontains=keyword)
        )
        
        if user.is_department_admin and not user.is_super_admin:
            queryset = queryset.filter(department_id=user.department_id)
        
        results = []
        for u in queryset[:limit]:
            results.append({
                'type': 'user',
                'type_name': '用户',
                'resource_type': 'user',
                'action_type': 'view',
                'id': u.id,
                'title': u.nickname or u.username,
                'subtitle': f"{u.username} - {u.department.name if u.department else ''}",
            })
        
        return results
