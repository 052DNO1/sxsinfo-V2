"""
学期服务
"""

import json
import io
import logging
from datetime import date, timedelta
from django.db import transaction, models
from django.core.paginator import Paginator
from django.core.cache import cache
from django.core.serializers import serialize
from django.http import HttpResponse
from django.utils import timezone
from django.utils.encoding import escape_uri_path
from apps.core.exceptions import ValidationError, NotFoundError, PermissionDenied
from apps.schedules.models import Semester, TermArchive
from apps.laboratories.models import Laboratory, Equipment
from apps.records.models import UsageRecord
from apps.maintenance.models import WorkOrder
from apps.users.models import User, SystemSetting
from apps.schedules.models import Schedule

logger = logging.getLogger(__name__)


class SemesterService:
    """学期服务"""

    def get_semester_list(
        self,
        requester,
        page: int = 1,
        page_size: int = 20,
        no_page: bool = False
    ) -> dict:
        queryset = Semester.objects.filter(is_deleted=False)
        queryset = queryset.order_by('-start_date')
        
        if no_page:
            return {
                'list': [self._format_semester(s) for s in queryset],
                'pagination': {
                    'total': queryset.count(),
                }
            }
        
        paginator = Paginator(queryset, page_size)
        page_obj = paginator.get_page(page)
        
        return {
            'list': [self._format_semester(s) for s in page_obj],
            'pagination': {
                'total': paginator.count,
                'page': page,
                'page_size': page_size,
                'total_pages': paginator.num_pages,
            }
        }

    def get_semester_detail(self, requester, semester_id: int) -> dict:
        try:
            semester = Semester.objects.get(id=semester_id, is_deleted=False)
        except Semester.DoesNotExist:
            raise NotFoundError('学期不存在')
        
        return self._format_semester_detail(semester)

    def get_current_semester(self, requester) -> dict:
        semester = Semester.get_current()
        if not semester:
            return {'current_semester': None}
        return {'current_semester': self._format_semester(semester)}

    def get_semester_options(self, requester) -> list:
        semesters = Semester.objects.filter(is_deleted=False).order_by('-start_date')
        options = [{'id': '', 'text': '全部学期'}]
        for s in semesters:
            label = s.name
            if s.is_current:
                label += ' (当前)'
            options.append({'id': s.id, 'text': label})
        return options

    @transaction.atomic
    def create_semester(self, requester, data: dict) -> Semester:
        if not requester.is_super_admin:
            raise PermissionDenied('无权限创建学期')
        
        name = data.get('name', '').strip()
        code = data.get('code', '').strip()
        
        if not name:
            raise ValidationError('学期名称不能为空')
        
        if not code:
            code = name.lower().replace(' ', '_').replace('-', '_')
        
        if Semester.objects.filter(code=code).exists():
            counter = 1
            original_code = code
            while Semester.objects.filter(code=code).exists():
                code = f"{original_code}_{counter}"
                counter += 1
        
        if Semester.objects.filter(name=name).exists():
            raise ValidationError(f'学期名称 "{name}" 已存在')
        
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        
        if start_date and end_date and start_date > end_date:
            raise ValidationError('开始日期不能晚于结束日期')
        
        is_current = data.get('is_current', True)
        
        if is_current:
            existing_current = Semester.objects.filter(is_current=True, is_archived=False).first()
            if existing_current:
                raise ValidationError(f'当前已有正在进行的学期「{existing_current.name}」，请先将其归档后再设置新的当前学期')
        
        semester = Semester.objects.create(
            name=name,
            code=code,
            start_date=start_date,
            end_date=end_date,
            total_weeks=data.get('total_weeks', 18),
            description=data.get('description', ''),
            is_current=is_current,
        )
        
        return semester

    @transaction.atomic
    def update_semester(self, requester, semester_id: int, data: dict) -> Semester:
        if not requester.is_super_admin:
            raise PermissionDenied('无权限修改学期')
        
        try:
            semester = Semester.objects.get(id=semester_id, is_deleted=False)
        except Semester.DoesNotExist:
            raise NotFoundError('学期不存在')
        
        if semester.is_archived:
            raise ValidationError('已归档的学期无法修改')
        
        if 'name' in data:
            name = data['name'].strip()
            if not name:
                raise ValidationError('学期名称不能为空')
            if Semester.objects.filter(name=name).exclude(id=semester_id).exists():
                raise ValidationError(f'学期名称 "{name}" 已存在')
            semester.name = name
        
        if 'code' in data:
            code = data['code'].strip()
            if not code:
                raise ValidationError('学期代码不能为空')
            if Semester.objects.filter(code=code).exclude(id=semester_id).exists():
                raise ValidationError(f'学期代码 "{code}" 已存在')
            semester.code = code
        
        for field in ['start_date', 'end_date', 'total_weeks', 'description']:
            if field in data:
                setattr(semester, field, data[field])
        
        if semester.start_date and semester.end_date and semester.start_date > semester.end_date:
            raise ValidationError('开始日期不能晚于结束日期')
        
        semester.save()
        return semester

    @transaction.atomic
    def delete_semester(self, requester, semester_id: int) -> bool:
        if not requester.is_super_admin:
            raise PermissionDenied('无权限删除学期')
        
        try:
            semester = Semester.objects.get(id=semester_id, is_deleted=False)
        except Semester.DoesNotExist:
            raise NotFoundError('学期不存在')
        
        if semester.is_current:
            raise ValidationError('不能删除当前学期')
        
        if semester.is_archived:
            raise ValidationError('已归档的学期禁止删除')
        
        semester.delete()
        return True

    @transaction.atomic
    def batch_delete_semesters(self, requester, semester_ids: list) -> dict:
        if not requester.is_super_admin:
            raise PermissionDenied('无权限删除学期')
        
        deleted_count = 0
        failed_list = []
        
        for semester_id in semester_ids:
            try:
                self.delete_semester(requester, semester_id)
                deleted_count += 1
            except Exception as e:
                failed_list.append({'id': semester_id, 'reason': str(e)})
        
        return {
            'deleted_count': deleted_count,
            'failed_count': len(failed_list),
            'failed_list': failed_list,
        }

    @transaction.atomic
    def set_current_semester(self, requester, semester_id: int) -> Semester:
        if not requester.is_super_admin:
            raise PermissionDenied('无权限设置当前学期')
        
        try:
            semester = Semester.objects.get(id=semester_id, is_deleted=False)
        except Semester.DoesNotExist:
            raise NotFoundError('学期不存在')
        
        if semester.is_archived:
            raise ValidationError('不能将已归档的学期设为当前学期')
        
        semester.set_as_current()
        return semester

    @transaction.atomic
    def unset_current_semester(self, requester, semester_id: int) -> Semester:
        if not requester.is_super_admin:
            raise PermissionDenied('无权限操作')
        
        try:
            semester = Semester.objects.get(id=semester_id, is_deleted=False)
        except Semester.DoesNotExist:
            raise NotFoundError('学期不存在')
        
        if not semester.is_current:
            raise ValidationError('该学期不是当前学期')
        
        semester.is_current = False
        semester.save(update_fields=['is_current'])
        return semester

    @transaction.atomic
    def archive_semester(self, requester, semester_id: int) -> Semester:
        if not requester.is_super_admin:
            raise PermissionDenied('无权限归档学期')
        
        try:
            semester = Semester.objects.get(id=semester_id, is_deleted=False)
        except Semester.DoesNotExist:
            raise NotFoundError('学期不存在')
        
        if semester.is_current:
            raise ValidationError('不能归档当前学期')
        
        if semester.is_archived:
            raise ValidationError('该学期已归档')
        
        semester.archive()
        return semester

    def get_archive_overview(self, requester) -> dict:
        if not requester.is_super_admin:
            raise PermissionDenied('无权限查看归档概览')
        
        current_semester = Semester.get_current()
        current_semester_data = None
        
        if current_semester:
            current_semester_data = {
                'id': current_semester.id,
                'name': current_semester.name,
                'start_date': current_semester.start_date.strftime('%Y-%m-%d'),
                'end_date': current_semester.end_date.strftime('%Y-%m-%d'),
                'stats': self._get_semester_stats(current_semester),
            }
        
        archived_semesters = Semester.objects.filter(is_archived=True).order_by('-end_date')
        archived_list = []
        
        for sem in archived_semesters:
            archived_list.append({
                'id': sem.id,
                'name': sem.name,
                'start_date': sem.start_date.strftime('%Y-%m-%d'),
                'end_date': sem.end_date.strftime('%Y-%m-%d'),
                'stats': self._get_semester_stats(sem),
            })
        
        return {
            'current_semester': current_semester_data,
            'archived_semesters': archived_list,
        }

    def _get_semester_stats(self, semester: Semester) -> dict:
        return {
            'record_count': UsageRecord.objects.filter(semester=semester).count(),
            'maintain_count': WorkOrder.objects.filter(semester=semester).exclude(maintenance_type=3).count(),
            'equipment_maintenance_count': WorkOrder.objects.filter(semester=semester, maintenance_type=3).count(),
            'class_count': semester.get_schedule_count(),
            'lab_count': Laboratory.objects.filter(is_deleted=False).count(),
            'device_count': Equipment.objects.filter(is_deleted=False).count(),
            'user_count': User.objects.filter(is_deleted=False).count(),
        }

    def _format_semester(self, semester: Semester) -> dict:
        return {
            'id': semester.id,
            'name': semester.name,
            'code': semester.code,
            'start_date': semester.start_date.strftime('%Y-%m-%d'),
            'end_date': semester.end_date.strftime('%Y-%m-%d'),
            'is_current': semester.is_current,
            'is_archived': semester.is_archived,
            'total_weeks': semester.total_weeks,
            'schedule_count': semester.get_schedule_count(),
            'created_at': semester.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        }

    def _format_semester_detail(self, semester: Semester) -> dict:
        data = self._format_semester(semester)
        data.update({
            'description': semester.description,
            'updated_at': semester.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
        })
        return data

    CACHE_KEY_ARCHIVE_SETTINGS = 'archive_settings'

    def get_archive_settings(self, requester) -> dict:
        if not requester.is_super_admin:
            raise PermissionDenied('无权限访问')
        
        cached = cache.get(self.CACHE_KEY_ARCHIVE_SETTINGS)
        if cached is not None:
            return {'retention_months': cached}
        
        setting, created = SystemSetting.objects.get_or_create(
            key='archive_retention_months',
            defaults={'value': 0, 'description': '归档保留时间(月)，0表示永久保留'}
        )
        cache.set(self.CACHE_KEY_ARCHIVE_SETTINGS, setting.value, 3600)
        return {'retention_months': setting.value}

    @transaction.atomic
    def save_archive_settings(self, requester, retention_months: int) -> dict:
        if not requester.is_super_admin:
            raise PermissionDenied('无权限访问')
        
        try:
            retention_months = int(retention_months)
            if retention_months < 0:
                raise ValueError
        except (TypeError, ValueError):
            raise ValidationError('请输入有效的月份数值')
        
        SystemSetting.objects.update_or_create(
            key='archive_retention_months',
            defaults={
                'value': retention_months,
                'description': '归档保留时间(月)，0表示永久保留'
            }
        )
        cache.set(self.CACHE_KEY_ARCHIVE_SETTINGS, retention_months, 3600)
        
        cleanup_msg = ''
        if retention_months > 0:
            deleted_count = self._cleanup_expired_archives(retention_months)
            if deleted_count > 0:
                cleanup_msg = f'，并自动清理了 {deleted_count} 个已过期的归档学期'
        
        return {'retention_months': retention_months, 'message': f'设置已保存{cleanup_msg}'}

    def manual_cleanup(self, requester) -> dict:
        if not requester.is_super_admin:
            raise PermissionDenied('只有超级管理员可以执行清理操作')
        
        cached_retention = cache.get(self.CACHE_KEY_ARCHIVE_SETTINGS)
        if cached_retention is not None:
            retention_months = cached_retention
        else:
            try:
                setting = SystemSetting.objects.get(key='archive_retention_months')
                retention_months = int(setting.value)
                cache.set(self.CACHE_KEY_ARCHIVE_SETTINGS, retention_months, 3600)
            except SystemSetting.DoesNotExist:
                raise ValidationError('请先设置过期时间')
        
        if retention_months <= 0:
            raise ValidationError('请先设置过期时间')
        
        deleted_count = self._cleanup_expired_archives(retention_months)
        
        if deleted_count > 0:
            return {'deleted_count': deleted_count, 'message': f'成功清理了 {deleted_count} 个过期的归档学期'}
        else:
            return {'deleted_count': 0, 'message': '没有找到需要清理的过期归档学期'}

    def _cleanup_expired_archives(self, months: int) -> int:
        if months <= 0:
            return 0
        
        cutoff_date = timezone.now().date() - timedelta(days=months * 30)
        
        with transaction.atomic():
            expired_ids = list(Semester.objects.filter(
                is_archived=True,
                end_date__lt=cutoff_date
            ).values_list('id', flat=True))
            
            count = len(expired_ids)
            if count > 0:
                Semester.objects.filter(id__in=expired_ids).delete()
                cache.delete(self.CACHE_KEY_ARCHIVE_SETTINGS)
        
        return count

    @transaction.atomic
    def archive_current_term_records(self, requester, archive_types: list) -> dict:
        if not requester.is_super_admin:
            raise PermissionDenied('只有超级管理员可以归档学期记录')
        
        if not archive_types:
            raise ValidationError('请至少选择一种要归档的数据类型')
        
        current_semester = Semester.objects.select_for_update().filter(
            is_current=True, is_archived=False
        ).first()
        
        if not current_semester:
            raise ValidationError('未设置当前学期，请先由超级管理员创建并设为当前学期')
        
        if current_semester.is_archived:
            raise ValidationError('当前学期记录已经归档')
        
        archived_items = []
        archived_counts = {}
        
        if 'lab_info' in archive_types:
            labs = Laboratory.objects.filter(is_deleted=False)
            if labs.exists():
                data_str = serialize('json', labs)
                TermArchive.objects.create(
                    semester=current_semester,
                    archive_type='lab_info',
                    content=json.loads(data_str)
                )
                count = labs.count()
                labs.update(is_deleted=True, admin=None)
                archived_items.append('实训室信息')
                archived_counts['实训室信息'] = count
        
        if 'device_info' in archive_types:
            equipment = Equipment.objects.filter(is_deleted=False)
            if equipment.exists():
                data_str = serialize('json', equipment)
                TermArchive.objects.create(
                    semester=current_semester,
                    archive_type='device_info',
                    content=json.loads(data_str)
                )
                count = equipment.count()
                equipment.delete()
                archived_items.append('设备信息')
                archived_counts['设备信息'] = count
        
        if 'user_info' in archive_types:
            users = User.objects.filter(is_deleted=False)
            if users.exists():
                data_str = serialize('json', users, fields=('username', 'nickname', 'department', 'role', 'phone', 'email'))
                TermArchive.objects.create(
                    semester=current_semester,
                    archive_type='user_info',
                    content=json.loads(data_str)
                )
                archived_items.append('用户信息')
                archived_counts['用户信息'] = users.count()
        
        if 'records' in archive_types:
            count = UsageRecord.objects.filter(semester=current_semester).update(is_archived=True)
            archived_items.append('使用记录')
            archived_counts['使用记录'] = count
        
        if 'maintain' in archive_types:
            count = WorkOrder.objects.filter(semester=current_semester).update(is_archived=True)
            archived_items.append('工单记录')
            archived_counts['工单记录'] = count
        
        if 'classes' in archive_types:
            count = Schedule.objects.filter(semester=current_semester).update(is_archived=True)
            archived_items.append('课表记录')
            archived_counts['课表记录'] = count
        
        if archived_items:
            current_semester.is_archived = True
            current_semester.is_current = False
            current_semester.save(update_fields=['is_archived', 'is_current'])
        
        message_parts = []
        for item in archived_items:
            count = archived_counts.get(item, 0)
            message_parts.append(f'{item}({count}条)')
        
        message = f'成功归档学期「{current_semester.name}」的以下数据：{", ".join(message_parts)}。归档后除超级管理员外其他用户只能查看不能修改'
        
        return {
            'archived_items': archived_items,
            'archived_counts': archived_counts,
            'semester_id': current_semester.id,
            'message': message,
        }

    def get_archived_records(self, requester, semester_id: int, record_type: str = None,
                             department_id: int = None, page: int = 1, page_size: int = 10,
                             export_format: str = None) -> dict:
        if not requester.is_super_admin:
            raise PermissionDenied('只有超级管理员可以查看归档记录')
        
        try:
            semester = Semester.objects.get(id=semester_id)
        except Semester.DoesNotExist:
            raise NotFoundError('学期不存在')
        
        if export_format in ['excel', 'pdf']:
            return self._export_archived_records(semester, export_format, department_id)
        
        if not record_type:
            stats = self._get_archived_dashboard_stats(semester, department_id)
            return {
                'mode': 'dashboard',
                'semester_name': semester.name,
                'stats': stats,
            }
        
        records_list = self._get_archived_records_by_type(semester, record_type, department_id)
        
        paginator = Paginator(records_list, page_size)
        page_obj = paginator.get_page(page)
        
        return {
            'mode': 'list',
            'semester_name': semester.name,
            'record_type': record_type,
            'list': list(page_obj),
            'total': paginator.count,
            'page': page,
            'page_size': page_size,
            'total_pages': paginator.num_pages,
        }

    def _get_archived_dashboard_stats(self, semester: Semester, department_id: int = None) -> dict:
        filter_kwargs = {'semester': semester}
        if department_id:
            filter_kwargs['laboratory__department_id'] = department_id
        
        usage_count = UsageRecord.objects.filter(**filter_kwargs).count()
        
        work_order_filter = filter_kwargs.copy()
        maintain_count = WorkOrder.objects.filter(**work_order_filter).exclude(maintenance_type=3).count()
        
        fault_filter = filter_kwargs.copy()
        fault_filter['maintenance_type'] = 3
        fault_count = WorkOrder.objects.filter(**fault_filter).count()
        
        class_count = Schedule.objects.filter(**filter_kwargs).count()
        
        lab_archive = TermArchive.objects.filter(semester=semester, archive_type='lab_info').first()
        lab_count = len(lab_archive.content) if lab_archive else 0
        
        device_archive = TermArchive.objects.filter(semester=semester, archive_type='device_info').first()
        device_count = len(device_archive.content) if device_archive else 0
        
        user_archive = TermArchive.objects.filter(semester=semester, archive_type='user_info').first()
        user_count = len(user_archive.content) if user_archive else 0
        
        return {
            'usage': usage_count,
            'maintain': maintain_count,
            'fault': fault_count,
            'class': class_count,
            'lab': lab_count,
            'device': device_count,
            'user': user_count,
        }

    def _get_archived_records_by_type(self, semester: Semester, record_type: str,
                                       department_id: int = None) -> list:
        filter_kwargs = {'semester': semester}
        if department_id:
            filter_kwargs['laboratory__department_id'] = department_id
        
        records_list = []
        
        if record_type == 'usage':
            records = UsageRecord.objects.filter(**filter_kwargs).select_related(
                'laboratory', 'teacher'
            ).order_by('-usage_date')
            for record in records:
                records_list.append({
                    'type': '使用',
                    'id': record.id,
                    'laboratory_name': record.laboratory.name if record.laboratory else '未知实训室',
                    'content': record.content[:30] + '...' if len(record.content or '') > 30 else record.content,
                    'date': record.usage_date.strftime('%Y-%m-%d') if record.usage_date else '',
                    'operator': record.teacher.username if record.teacher else '未知用户',
                })
        
        elif record_type == 'maintain':
            records = WorkOrder.objects.filter(**filter_kwargs).exclude(
                maintenance_type=3
            ).select_related('laboratory', 'reporter').order_by('-reported_at')
            for record in records:
                records_list.append({
                    'type': '维护',
                    'id': record.id,
                    'laboratory_name': record.laboratory.name if record.laboratory else '未知实训室',
                    'content': record.description[:30] + '...' if len(record.description or '') > 30 else record.description,
                    'date': record.reported_at.strftime('%Y-%m-%d') if record.reported_at else '',
                    'operator': record.reporter.username if record.reporter else '未知用户',
                })
        
        elif record_type == 'fault':
            fault_filter = filter_kwargs.copy()
            fault_filter['maintenance_type'] = 3
            records = WorkOrder.objects.filter(**fault_filter).select_related(
                'laboratory', 'reporter'
            ).order_by('-reported_at')
            for record in records:
                records_list.append({
                    'type': '故障',
                    'id': record.id,
                    'laboratory_name': record.laboratory.name if record.laboratory else '未知实训室',
                    'content': record.description[:30] + '...' if len(record.description or '') > 30 else record.description,
                    'date': record.reported_at.strftime('%Y-%m-%d') if record.reported_at else '',
                    'operator': record.reporter.username if record.reporter else '未知用户',
                })
        
        elif record_type == 'class':
            records = Schedule.objects.filter(**filter_kwargs).select_related(
                'laboratory', 'teacher'
            ).order_by('weekday')
            for record in records:
                records_list.append({
                    'type': '课表',
                    'id': record.id,
                    'laboratory_name': record.laboratory.name if record.laboratory else '未知实训室',
                    'content': record.course_name,
                    'date': f"第{record.weekday}周",
                    'operator': record.teacher.username if record.teacher else '未知用户',
                })
        
        elif record_type == 'lab_info':
            archive = TermArchive.objects.filter(semester=semester, archive_type='lab_info').first()
            if archive:
                for item in archive.content:
                    fields = item['fields']
                    records_list.append({
                        'type': '实训室',
                        'id': item['pk'],
                        'laboratory_name': fields.get('name', ''),
                        'content': f"门牌:{fields.get('code', '')} 备注:{fields.get('description', '')}",
                        'date': archive.created_at.strftime('%Y-%m-%d'),
                        'operator': '-',
                    })
        
        elif record_type == 'device_info':
            archive = TermArchive.objects.filter(semester=semester, archive_type='device_info').first()
            if archive:
                location_ids = set()
                for item in archive.content:
                    loc = item['fields'].get('laboratory')
                    if loc:
                        location_ids.add(loc)
                
                loc_map = {}
                if location_ids:
                    locs = Laboratory.objects.filter(id__in=location_ids)
                    for l in locs:
                        loc_map[l.id] = l.name
                
                status_map = {
                    'NORMAL': '正常', 'MAINTENANCE': '维护中',
                    'DAMAGED': '损坏', 'SCRAPPED': '报废', 'BORROWED': '借出'
                }
                
                for item in archive.content:
                    fields = item['fields']
                    loc_id = fields.get('laboratory')
                    loc_name = loc_map.get(loc_id, '未分配') if loc_id else '未分配'
                    status_val = fields.get('status', 'NORMAL')
                    status_text = status_map.get(status_val, status_val)
                    
                    records_list.append({
                        'type': '设备',
                        'id': item['pk'],
                        'laboratory_name': loc_name,
                        'content': f"{fields.get('name', '')} ({fields.get('code', '')})",
                        'date': archive.created_at.strftime('%Y-%m-%d'),
                        'operator': status_text,
                    })
        
        elif record_type == 'user_info':
            archive = TermArchive.objects.filter(semester=semester, archive_type='user_info').first()
            if archive:
                for item in archive.content:
                    fields = item['fields']
                    records_list.append({
                        'type': '用户',
                        'id': item['pk'],
                        'laboratory_name': '-',
                        'content': f"{fields.get('nickname', '')} ({fields.get('username', '')})",
                        'date': archive.created_at.strftime('%Y-%m-%d'),
                        'operator': str(fields.get('role', '')),
                    })
        
        return records_list

    def _export_archived_records(self, semester: Semester, format_type: str,
                                  department_id: int = None):
        from openpyxl import Workbook
        
        filter_kwargs = {'semester': semester}
        if department_id:
            filter_kwargs['laboratory__department_id'] = department_id
        
        if format_type == 'excel':
            wb = Workbook()
            default_ws = wb.active
            wb.remove(default_ws)
            
            usage_rows = []
            records = UsageRecord.objects.filter(**filter_kwargs).select_related(
                'laboratory', 'teacher'
            ).order_by('-usage_date')
            for record in records:
                usage_rows.append([
                    record.id,
                    record.laboratory.name if record.laboratory else '',
                    record.content or '',
                    record.usage_date.strftime('%Y-%m-%d') if record.usage_date else '',
                    record.teacher.username if record.teacher else '',
                    record.class_name or '',
                ])
            
            ws = wb.create_sheet(title='使用记录')
            headers = ['ID', '实训室', '内容', '日期', '教师', '班级']
            for col, header in enumerate(headers, 1):
                ws.cell(row=1, column=col, value=header)
            for row_idx, row_data in enumerate(usage_rows, 2):
                for col_idx, value in enumerate(row_data, 1):
                    ws.cell(row=row_idx, column=col_idx, value=str(value) if value else '')
            
            response = HttpResponse(
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            filename = f"学期{semester.name}归档记录.xlsx"
            response['Content-Disposition'] = f'attachment; filename="{escape_uri_path(filename)}"'
            wb.save(response)
            return response
        
        raise ValidationError('不支持的导出格式')

    def check_term_status(self, requester) -> dict:
        current_semester = Semester.get_current()
        
        return {
            'is_super_admin': requester.is_super_admin,
            'has_current_semester': current_semester is not None,
            'current_semester': {
                'id': current_semester.id,
                'name': current_semester.name,
            } if current_semester else None,
        }
