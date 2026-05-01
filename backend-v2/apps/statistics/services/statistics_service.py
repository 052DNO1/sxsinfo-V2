"""
统计服务
"""

from datetime import date, datetime, timedelta
from django.db import models
from django.db.models import Count, Sum, Avg
from django.core.cache import cache
from django.utils import timezone
from apps.core.exceptions import ValidationError
from apps.laboratories.models import Laboratory, Equipment
from apps.schedules.models import Schedule, Semester
from apps.records.models import UsageRecord
from apps.maintenance.models import WorkOrder
from apps.users.models import User
from apps.core.constants import WorkOrderStatus
from common.services.cache_service import CacheKeyManager
from common.decorators import cached_method
from apps.core.utils import beijing_strftime, beijing_now, beijing_today


class StatisticsService:
    """统计服务"""

    @cached_method(timeout=60, key_prefix='stats:dashboard')
    def get_dashboard_stats(self, requester) -> dict:
        current_semester = Semester.get_current()
        if not current_semester:
            raise ValidationError('未设置当前学期')

        stats = {
            'laboratories': self._get_laboratory_stats(requester),
            'schedules': self._get_schedule_stats(requester, current_semester),
            'records': self._get_record_stats(requester, current_semester),
            'work_orders': self._get_work_order_stats(requester, current_semester),
            'equipment': self._get_equipment_stats(requester),
            'users': self._get_user_stats(requester),
            'usage_rate': self._calculate_usage_rate(requester, current_semester),
        }

        stats['current_semester'] = {
            'id': current_semester.id,
            'name': current_semester.name,
        }

        return stats

    @cached_method(timeout=60, key_prefix='stats:teacher')
    def get_teacher_stats(self, requester) -> dict:
        current_semester = Semester.get_current()
        if not current_semester:
            raise ValidationError('未设置当前学期')
        
        records = UsageRecord.objects.filter(
            teacher=requester,
            semester=current_semester,
            is_deleted=False
        )
        
        stats = {
            'total_records': records.count(),
            'month_records': records.filter(
                usage_date__gte=beijing_today().replace(day=1)
            ).count(),
            'used_laboratories': records.values('laboratory').distinct().count(),
            'total_students': records.aggregate(
                total=Sum('student_count')
            )['total'] or 0,
            'records': {
                'by_month': self._get_records_by_month(records),
                'by_laboratory': self._get_records_by_laboratory(records),
            },
            'records_by_sxs': self._get_records_by_laboratory(records),
            'recent_records': self._get_recent_records(records, 5),
        }
        
        return stats

    @cached_method(timeout=60, key_prefix='stats:lab_admin')
    def get_laboratory_admin_stats(self, requester) -> dict:
        current_semester = Semester.get_current()
        if not current_semester:
            raise ValidationError('未设置当前学期')
        
        managed_labs = Laboratory.objects.filter(
            admin=requester, is_deleted=False
        )
        managed_lab_ids = list(managed_labs.values_list('id', flat=True))
        
        stats = {
            'managed_laboratories': managed_labs.count(),
            'total_capacity': managed_labs.aggregate(
                total=Sum('capacity')
            )['total'] or 0,
            'avg_capacity': round(managed_labs.aggregate(
                avg=Avg('capacity')
            )['avg'] or 0, 1),
            'equipment': self._get_equipment_stats_for_labs(managed_lab_ids),
            'records': self._get_record_stats_for_labs(managed_lab_ids, current_semester),
            'work_orders': self._get_work_order_stats_for_labs(managed_lab_ids, current_semester),
        }
        
        return stats

    @cached_method(timeout=60, key_prefix='stats:super_admin')
    def get_super_admin_stats(self, requester) -> dict:
        stats = {
            'dept_distribution': self._get_department_distribution(),
            'user_type_distribution': self._get_user_type_distribution(),
            'laboratory_distribution': self._get_laboratory_distribution(),
        }
        return stats

    @cached_method(timeout=60, key_prefix='stats:system_superuser')
    def get_system_superuser_stats(self, requester) -> dict:
        stats = self._get_system_health_stats()
        return stats

    def _get_system_health_stats(self) -> dict:
        from django.db import connection
        from django.utils import timezone
        from datetime import timedelta
        
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM django_session WHERE expire_date > NOW()")
                active_sessions = cursor.fetchone()[0]
        except Exception:
            active_sessions = 0
        
        total_users = User.objects.filter(is_deleted=False).count()
        enabled_users = User.objects.filter(is_deleted=False, is_active=True).count()
        disabled_users = total_users - enabled_users
        
        thirty_days_ago = timezone.now() - timedelta(days=30)
        recently_active_users = User.objects.filter(
            is_deleted=False, 
            last_login__gte=thirty_days_ago
        ).count()
        inactive_users = total_users - recently_active_users
        
        return {
            'active_sessions': active_sessions,
            'total_users': total_users,
            'enabled_users': enabled_users,
            'disabled_users': disabled_users,
            'recently_active_users': recently_active_users,
            'inactive_users': inactive_users,
            'database_status': 'healthy',
        }

    @cached_method(timeout=60, key_prefix='stats:comprehensive')
    def get_comprehensive_stats(self, requester) -> dict:
        current_semester = Semester.get_current()
        if not current_semester:
            raise ValidationError('未设置当前学期，无法查看统计信息')

        stats = {
            'laboratories': self._get_comprehensive_lab_stats(requester),
            'schedules': self._get_comprehensive_schedule_stats(requester, current_semester),
            'records': self._get_comprehensive_record_stats(requester, current_semester),
            'work_orders': self._get_comprehensive_work_order_stats(requester, current_semester),
            'equipment': self._get_comprehensive_equipment_stats(requester),
            'users': self._get_comprehensive_user_stats(requester),
            'usage_rate': self._calculate_usage_rate(requester, current_semester),
        }

        result = {
            'stats': stats,
            'current_semester': {
                'id': current_semester.id,
                'name': current_semester.name,
            },
            'user_role': self._get_user_role_name(requester),
        }

        return result

    def _get_laboratory_stats(self, user) -> dict:
        queryset = Laboratory.objects.filter(is_deleted=False)
        
        if user.is_department_admin and not user.is_super_admin:
            queryset = queryset.filter(department_id=user.department_id)
        elif user.is_laboratory_admin and not user.is_super_admin:
            queryset = queryset.filter(admin=user)
        
        return {
            'total': queryset.count(),
            'available': queryset.filter(is_available=True).count(),
            'total_capacity': queryset.aggregate(total=Sum('capacity'))['total'] or 0,
            'avg_capacity': round(queryset.aggregate(avg=Avg('capacity'))['avg'] or 0, 1),
        }

    def _get_schedule_stats(self, user, semester) -> dict:
        queryset = Schedule.objects.filter(
            semester=semester, is_deleted=False
        )
        
        if user.is_department_admin and not user.is_super_admin:
            queryset = queryset.filter(laboratory__department_id=user.department_id)
        elif user.is_laboratory_admin and not user.is_super_admin:
            queryset = queryset.filter(laboratory__admin=user)
        elif user.is_teacher and not user.is_super_admin:
            queryset = queryset.filter(teacher=user)
        
        by_weekday = {}
        weekday_map = {1: '周一', 2: '周二', 3: '周三', 4: '周四', 5: '周五', 6: '周六', 7: '周日'}
        for schedule in queryset:
            weekday = weekday_map.get(schedule.weekday, f"周{schedule.weekday}")
            by_weekday[weekday] = by_weekday.get(weekday, 0) + 1
        
        return {
            'total': queryset.count(),
            'by_weekday': by_weekday,
        }

    def _get_record_stats(self, user, semester) -> dict:
        queryset = UsageRecord.objects.filter(
            semester=semester, is_deleted=False
        )
        
        if user.is_department_admin and not user.is_super_admin:
            queryset = queryset.filter(laboratory__department_id=user.department_id)
        elif user.is_laboratory_admin and not user.is_super_admin:
            queryset = queryset.filter(laboratory__admin=user)
        elif user.is_teacher and not user.is_super_admin:
            queryset = queryset.filter(teacher=user)
        
        return {
            'total': queryset.count(),
            'total_class_hours': queryset.aggregate(total=Sum('class_hours'))['total'] or 0,
            'total_students': queryset.aggregate(total=Sum('student_count'))['total'] or 0,
            'by_month': self._get_records_by_month(queryset),
        }

    def _get_work_order_stats(self, user, semester) -> dict:
        queryset = WorkOrder.objects.filter(
            semester=semester, is_deleted=False
        )
        
        if user.is_department_admin and not user.is_super_admin:
            queryset = queryset.filter(laboratory__department_id=user.department_id)
        elif user.is_laboratory_admin and not user.is_super_admin:
            queryset = queryset.filter(laboratory__admin=user)
        
        by_status = {}
        status_map = {
            WorkOrderStatus.PENDING: '待处理',
            WorkOrderStatus.PROCESSING: '处理中',
            WorkOrderStatus.COMPLETED: '已完成',
            WorkOrderStatus.CLOSED: '已关闭',
        }
        for order in queryset:
            status = status_map.get(order.status, order.status)
            by_status[status] = by_status.get(status, 0) + 1
        
        return {
            'total': queryset.count(),
            'pending': queryset.filter(status=WorkOrderStatus.PENDING).count(),
            'processing': queryset.filter(status=WorkOrderStatus.PROCESSING).count(),
            'completed': queryset.filter(status=WorkOrderStatus.COMPLETED).count(),
            'by_status': by_status,
        }

    def _get_equipment_stats(self, user) -> dict:
        queryset = Equipment.objects.filter(is_deleted=False)
        
        if user.is_department_admin and not user.is_super_admin:
            queryset = queryset.filter(laboratory__department_id=user.department_id)
        elif user.is_laboratory_admin and not user.is_super_admin:
            queryset = queryset.filter(laboratory__admin=user)
        
        by_status = {}
        for eq in queryset:
            by_status[eq.status] = by_status.get(eq.status, 0) + 1
        
        return {
            'total': queryset.count(),
            'by_status': by_status,
        }

    def _get_user_stats(self, user) -> dict:
        queryset = User.objects.filter(is_deleted=False)
        
        if user.is_department_admin and not user.is_super_admin:
            queryset = queryset.filter(department_id=user.department_id)
        
        return {
            'total': queryset.count(),
            'active': queryset.filter(is_active=True).count(),
        }

    def _calculate_usage_rate(self, user, semester) -> dict:
        lab_queryset = Laboratory.objects.filter(is_deleted=False)
        
        if user.is_department_admin and not user.is_super_admin:
            lab_queryset = lab_queryset.filter(department_id=user.department_id)
        elif user.is_laboratory_admin and not user.is_super_admin:
            lab_queryset = lab_queryset.filter(admin=user)
        
        total_labs = lab_queryset.count()
        
        schedule_queryset = Schedule.objects.filter(
            semester=semester, is_deleted=False
        )
        if user.is_department_admin and not user.is_super_admin:
            schedule_queryset = schedule_queryset.filter(laboratory__department_id=user.department_id)
        elif user.is_laboratory_admin and not user.is_super_admin:
            schedule_queryset = schedule_queryset.filter(laboratory__admin=user)
        
        used_labs = schedule_queryset.values('laboratory').distinct().count()
        
        record_queryset = UsageRecord.objects.filter(
            semester=semester, is_deleted=False
        )
        if user.is_department_admin and not user.is_super_admin:
            record_queryset = record_queryset.filter(laboratory__department_id=user.department_id)
        elif user.is_laboratory_admin and not user.is_super_admin:
            record_queryset = record_queryset.filter(laboratory__admin=user)
        
        thirty_days_ago = beijing_today() - timedelta(days=30)
        recent_used = record_queryset.filter(
            usage_date__gte=thirty_days_ago
        ).values('laboratory').distinct().count()
        
        return {
            'schedule_rate': round((used_labs / total_labs * 100) if total_labs > 0 else 0, 2),
            'record_rate': round((recent_used / total_labs * 100) if total_labs > 0 else 0, 2),
            'total_laboratories': total_labs,
            'used_laboratories': used_labs,
            'recent_used_laboratories': recent_used,
        }

    def _get_records_by_month(self, queryset) -> dict:
        by_month = {}
        for record in queryset:
            if record.usage_date:
                month = beijing_strftime(record.usage_date, '%Y-%m')
                by_month[month] = by_month.get(month, 0) + 1
        return by_month

    def _get_records_by_laboratory(self, queryset) -> dict:
        by_lab = {}
        for record in queryset:
            if record.laboratory:
                name = record.laboratory.name
                by_lab[name] = by_lab.get(name, 0) + 1
        return by_lab

    def _get_recent_records(self, queryset, limit: int) -> list:
        recent = queryset.order_by('-usage_date', '-id')[:limit]
        return [
            {
                'id': r.id,
                'laboratory_name': r.laboratory.name if r.laboratory else '',
                'usage_date': beijing_strftime(r.usage_date, '%Y-%m-%d'),
                'class_hours': r.class_hours,
                'class_name': r.class_name,
            }
            for r in recent
        ]

    def _get_equipment_stats_for_labs(self, lab_ids: list) -> dict:
        queryset = Equipment.objects.filter(
            laboratory_id__in=lab_ids, is_deleted=False
        )
        
        by_status = {}
        by_laboratory = {}
        for eq in queryset:
            by_status[eq.status] = by_status.get(eq.status, 0) + 1
            lab_name = eq.laboratory.name if eq.laboratory else '未分配'
            by_laboratory[lab_name] = by_laboratory.get(lab_name, 0) + 1
        
        return {
            'total': queryset.count(),
            'by_status': by_status,
            'by_laboratory': by_laboratory,
        }

    def _get_record_stats_for_labs(self, lab_ids: list, semester) -> dict:
        queryset = UsageRecord.objects.filter(
            laboratory_id__in=lab_ids,
            semester=semester,
            is_deleted=False
        )
        
        return {
            'total': queryset.count(),
            'by_month': self._get_records_by_month(queryset),
        }

    def _get_work_order_stats_for_labs(self, lab_ids: list, semester) -> dict:
        queryset = WorkOrder.objects.filter(
            laboratory_id__in=lab_ids,
            semester=semester,
            is_deleted=False
        )
        
        return {
            'total': queryset.count(),
            'pending': queryset.filter(status=WorkOrderStatus.PENDING).count(),
        }

    def _get_department_distribution(self) -> list:
        from apps.users.models import Department
        
        distribution = Laboratory.objects.filter(
            is_deleted=False
        ).values('department__name').annotate(
            count=Count('id')
        ).order_by('-count')
        
        return [
            {'name': item['department__name'] or '未分配', 'count': item['count']}
            for item in distribution
        ]

    def _get_user_type_distribution(self) -> list:
        return [
            {'name': '分院管理员', 'count': User.objects.filter(
                role__in=[4, 6, 8, 12, 20], is_active=True, is_deleted=False
            ).count()},
            {'name': '实训室管理员', 'count': User.objects.filter(
                role__in=[2, 6, 10, 18], is_active=True, is_deleted=False
            ).count()},
            {'name': '教师', 'count': User.objects.filter(
                role__in=[1, 3, 5, 9, 17], is_active=True, is_deleted=False
            ).count()},
        ]

    def _get_laboratory_distribution(self) -> list:
        distribution = Laboratory.objects.filter(
            is_deleted=False
        ).values('laboratory_type').annotate(
            count=Count('id')
        ).order_by('-count')
        
        return [
            {'name': item['laboratory_type'] or '未分类', 'count': item['count']}
            for item in distribution
        ]

    def _get_comprehensive_lab_stats(self, user) -> dict:
        queryset = Laboratory.objects.filter(is_deleted=False)
        
        if user.is_department_admin and not user.is_super_admin:
            queryset = queryset.filter(department_id=user.department_id)
        elif user.is_laboratory_admin and not user.is_super_admin:
            queryset = queryset.filter(admin=user)
        
        by_department = {}
        by_building = {}
        room_list = []
        
        for lab in queryset:
            room_list.append({
                'name': lab.name,
                'code': lab.code,
                'capacity': lab.capacity or 0,
            })
            
            dept_name = lab.department.name if lab.department else '未分配'
            if dept_name not in by_department:
                by_department[dept_name] = {'count': 0, 'capacity': 0}
            by_department[dept_name]['count'] += 1
            by_department[dept_name]['capacity'] += lab.capacity or 0
            
            building = self._get_building_from_code(lab.code)
            if building not in by_building:
                by_building[building] = {'count': 0, 'capacity': 0}
            by_building[building]['count'] += 1
            by_building[building]['capacity'] += lab.capacity or 0
        
        return {
            'total': queryset.count(),
            'by_department': by_department,
            'by_building': by_building,
            'room_list': room_list,
            'capacity_stats': {
                'total_capacity': queryset.aggregate(total=Sum('capacity'))['total'] or 0,
                'avg_capacity': round(queryset.aggregate(avg=Avg('capacity'))['avg'] or 0, 2),
                'max_capacity': queryset.aggregate(max=models.Max('capacity'))['max'] or 0,
                'min_capacity': queryset.aggregate(min=models.Min('capacity'))['min'] or 0,
            }
        }

    def _get_comprehensive_schedule_stats(self, user, semester) -> dict:
        queryset = Schedule.objects.filter(semester=semester, is_deleted=False)
        
        if user.is_department_admin and not user.is_super_admin:
            queryset = queryset.filter(laboratory__department_id=user.department_id)
        elif user.is_laboratory_admin and not user.is_super_admin:
            queryset = queryset.filter(laboratory__admin=user)
        elif user.is_teacher and not user.is_super_admin:
            queryset = queryset.filter(teacher=user)
        
        by_weekday = {}
        weekday_map = {1: '周一', 2: '周二', 3: '周三', 4: '周四', 5: '周五', 6: '周六', 7: '周日'}
        
        for schedule in queryset:
            weekday = weekday_map.get(schedule.weekday, f"周{schedule.weekday}")
            by_weekday[weekday] = by_weekday.get(weekday, 0) + 1
        
        return {
            'total': queryset.count(),
            'by_weekday': by_weekday,
            'capacity_usage': {
                'total_students': queryset.aggregate(total=Sum('student_count'))['total'] or 0,
                'avg_students': round(queryset.aggregate(avg=Avg('student_count'))['avg'] or 0, 2),
            }
        }

    def _get_comprehensive_record_stats(self, user, semester) -> dict:
        queryset = UsageRecord.objects.filter(semester=semester, is_deleted=False)
        
        if user.is_department_admin and not user.is_super_admin:
            queryset = queryset.filter(laboratory__department_id=user.department_id)
        elif user.is_laboratory_admin and not user.is_super_admin:
            queryset = queryset.filter(laboratory__admin=user)
        elif user.is_teacher and not user.is_super_admin:
            queryset = queryset.filter(teacher=user)
        
        by_month = {}
        by_laboratory = {}
        
        for record in queryset:
            if record.laboratory:
                name = record.laboratory.name
                by_laboratory[name] = by_laboratory.get(name, 0) + 1
            
            if record.usage_date:
                month = beijing_strftime(record.usage_date, '%Y-%m')
                by_month[month] = by_month.get(month, 0) + 1
        
        return {
            'total': queryset.count(),
            'by_month': by_month,
            'by_laboratory': by_laboratory,
        }

    def _get_comprehensive_work_order_stats(self, user, semester) -> dict:
        queryset = WorkOrder.objects.filter(semester=semester, is_deleted=False)
        
        if user.is_department_admin and not user.is_super_admin:
            queryset = queryset.filter(laboratory__department_id=user.department_id)
        elif user.is_laboratory_admin and not user.is_super_admin:
            queryset = queryset.filter(laboratory__admin=user)
        
        by_type = {}
        by_laboratory = {}
        by_month = {}
        
        for order in queryset:
            type_name = order.get_maintenance_type_display()
            by_type[type_name] = by_type.get(type_name, 0) + 1
            
            if order.laboratory:
                name = order.laboratory.name
                by_laboratory[name] = by_laboratory.get(name, 0) + 1
            
            report_date = order.reported_at.date() if order.reported_at else None
            if report_date:
                month = beijing_strftime(report_date, '%Y-%m')
                by_month[month] = by_month.get(month, 0) + 1
        
        return {
            'total': queryset.count(),
            'by_type': by_type,
            'by_laboratory': by_laboratory,
            'by_month': by_month,
        }

    def _get_comprehensive_equipment_stats(self, user) -> dict:
        queryset = Equipment.objects.filter(is_deleted=False)
        
        if user.is_department_admin and not user.is_super_admin:
            queryset = queryset.filter(laboratory__department_id=user.department_id)
        elif user.is_laboratory_admin and not user.is_super_admin:
            queryset = queryset.filter(laboratory__admin=user)
        
        by_type = {}
        by_status = {}
        by_laboratory = {}
        
        status_map = {
            'NORMAL': '正常',
            'MAINTENANCE': '维护中',
            'DAMAGED': '损坏',
            'SCRAPPED': '报废',
            'BORROWED': '借出'
        }
        
        for eq in queryset:
            eq_type = eq.category or '未知类型'
            by_type[eq_type] = by_type.get(eq_type, 0) + 1
            
            status = status_map.get(eq.status, eq.status)
            by_status[status] = by_status.get(status, 0) + 1
            
            lab_name = eq.laboratory.name if eq.laboratory else '未分配'
            by_laboratory[lab_name] = by_laboratory.get(lab_name, 0) + 1
        
        return {
            'total': queryset.count(),
            'by_type': by_type,
            'by_status': by_status,
            'by_laboratory': by_laboratory,
        }

    def _get_comprehensive_user_stats(self, user) -> dict:
        queryset = User.objects.filter(is_deleted=False)
        
        if user.is_department_admin and not user.is_super_admin:
            queryset = queryset.filter(department_id=user.department_id)
        
        by_role = {
            'super_admin': queryset.filter(role=16).count(),
            'dept_admin': queryset.filter(role__in=[4, 6, 8, 12, 20]).count(),
            'lab_admin': queryset.filter(role__in=[2, 6, 10, 18]).count(),
            'teacher': queryset.filter(role__in=[1, 3, 5, 9, 17]).count(),
        }
        
        return {
            'total': queryset.count(),
            'by_role': by_role,
            'active': queryset.filter(is_active=True).count(),
            'inactive': queryset.filter(is_active=False).count(),
        }

    def _get_building_from_code(self, code: str) -> str:
        if not code:
            return '其他'
        if code.startswith('20') or code.startswith('2'):
            return '二教'
        elif code.startswith('30') or code.startswith('3'):
            return '三教'
        elif code.startswith('40') or code.startswith('50') or code.startswith('4') or code.startswith('5'):
            return '五教'
        else:
            return '其他'

    def _get_user_role_name(self, user) -> str:
        if user.is_super_admin:
            return '超级管理员'
        elif user.is_department_admin:
            return '分院管理员'
        elif user.is_laboratory_admin:
            return '实训室管理员'
        elif user.is_teacher:
            return '教师'
        else:
            return '普通用户'

    def export_comprehensive_stats(self, requester):
        import io
        import urllib.parse
        from datetime import datetime
        from django.http import HttpResponse
        
        try:
            import pandas as pd
        except ImportError:
            raise ValidationError('请安装pandas库以支持导出功能')
        
        data = self.get_comprehensive_stats(requester)
        stats = data['stats']
        current_semester = data['current_semester']
        
        output = io.BytesIO()
        
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            overview_data = [
                ['统计项', '数值', '说明'],
                ['当前学期', current_semester['name'], ''],
                ['导出时间', beijing_now().strftime('%Y-%m-%d %H:%M:%S'), ''],
                ['实训室总数', stats['laboratories']['total'], '间'],
                ['实训室总容量', stats['laboratories']['capacity_stats']['total_capacity'], '人'],
                ['实训室平均容量', stats['laboratories']['capacity_stats']['avg_capacity'], '人'],
                ['教室使用率', f"{stats['usage_rate']['schedule_rate']}%", ''],
                ['记录使用率', f"{stats['usage_rate']['record_rate']}%", '最近30天'],
                ['课程总数', stats['schedules']['total'], '门'],
                ['设备总数', stats['equipment']['total'], '台'],
                ['使用记录总数', stats['records']['total'], '条'],
                ['工单总数', stats['work_orders']['total'], '条'],
                ['用户总数', stats['users']['total'], '人'],
            ]
            pd.DataFrame(overview_data).to_excel(writer, sheet_name='概览', index=False, header=False)
            
            if stats['laboratories']['room_list']:
                lab_df = pd.DataFrame(stats['laboratories']['room_list'])
                lab_df.columns = ['实训室名称', '门牌号', '容量']
                lab_df.to_excel(writer, sheet_name='实训室列表', index=False)
            
            dept_data = []
            for dept, data in stats['laboratories']['by_department'].items():
                dept_data.append({'分院': dept, '实训室数量': data['count'], '总容量': data['capacity']})
            if dept_data:
                pd.DataFrame(dept_data).to_excel(writer, sheet_name='分院分布', index=False)
            
            building_data = []
            for build, data in stats['laboratories']['by_building'].items():
                building_data.append({'教学楼': build, '实训室数量': data['count'], '总容量': data['capacity']})
            if building_data:
                pd.DataFrame(building_data).to_excel(writer, sheet_name='教学楼分布', index=False)
            
            work_order_type_data = []
            for wtype, count in stats['work_orders']['by_type'].items():
                work_order_type_data.append({'工单类型': wtype, '数量': count})
            if work_order_type_data:
                pd.DataFrame(work_order_type_data).to_excel(writer, sheet_name='工单类型统计', index=False)
            
            work_order_lab_data = []
            for lab, count in stats['work_orders']['by_laboratory'].items():
                work_order_lab_data.append({'实训室': lab, '工单数': count})
            if work_order_lab_data:
                pd.DataFrame(work_order_lab_data).to_excel(writer, sheet_name='实训室工单统计', index=False)
            
            record_lab_data = []
            for lab, count in stats['records']['by_laboratory'].items():
                record_lab_data.append({'实训室': lab, '使用记录数': count})
            if record_lab_data:
                pd.DataFrame(record_lab_data).to_excel(writer, sheet_name='实训室使用统计', index=False)
            
            usage_trend_data = []
            for month, count in stats['records']['by_month'].items():
                usage_trend_data.append({'月份': month, '使用次数': count})
            if usage_trend_data:
                usage_trend_data.sort(key=lambda x: x['月份'])
                pd.DataFrame(usage_trend_data).to_excel(writer, sheet_name='使用趋势', index=False)
            
            work_order_trend_data = []
            for month, count in stats['work_orders']['by_month'].items():
                work_order_trend_data.append({'月份': month, '工单数': count})
            if work_order_trend_data:
                work_order_trend_data.sort(key=lambda x: x['月份'])
                pd.DataFrame(work_order_trend_data).to_excel(writer, sheet_name='工单趋势', index=False)
            
            course_data = []
            for weekday, count in stats['schedules']['by_weekday'].items():
                course_data.append({'星期': weekday, '课程数量': count})
            if course_data:
                week_order = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
                course_data.sort(key=lambda x: week_order.index(x['星期']) if x['星期'] in week_order else 99)
                pd.DataFrame(course_data).to_excel(writer, sheet_name='课程分布', index=False)
            
            eq_type_data = []
            for eq_type, count in stats['equipment']['by_type'].items():
                eq_type_data.append({'设备类型': eq_type, '数量': count})
            if eq_type_data:
                pd.DataFrame(eq_type_data).to_excel(writer, sheet_name='设备类型分布', index=False)
            
            eq_status_data = []
            for status, count in stats['equipment']['by_status'].items():
                eq_status_data.append({'状态': status, '数量': count})
            if eq_status_data:
                pd.DataFrame(eq_status_data).to_excel(writer, sheet_name='设备状态分布', index=False)
            
            user_role_map = {
                'super_admin': '超级管理员',
                'dept_admin': '分院管理员',
                'lab_admin': '实训室管理员',
                'teacher': '教师',
            }
            user_data = []
            for role, count in stats['users']['by_role'].items():
                role_name = user_role_map.get(role, role)
                user_data.append({'用户角色': role_name, '人数': count})
            if user_data:
                pd.DataFrame(user_data).to_excel(writer, sheet_name='用户分布', index=False)
        
        output.seek(0)
        
        filename = f'综合统计报表_{current_semester["name"]}_{beijing_now().strftime("%Y%m%d")}.xlsx'
        encoded_filename = urllib.parse.quote(filename)
        
        response = HttpResponse(
            output.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename="{encoded_filename}"'
        return response
