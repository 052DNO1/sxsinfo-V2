"""
使用记录服务
"""

from datetime import date
from django.db import models, transaction
from django.core.paginator import Paginator
from apps.core.exceptions import NotFoundError, PermissionDenied, ValidationError
from apps.schedules.models import Semester
from apps.laboratories.models import Laboratory
from apps.records.models import UsageRecord
from apps.users.models import User


class UsageRecordService:
    """使用记录服务"""

    def get_record_list(
        self,
        requester,
        laboratory_id: int = None,
        teacher_id: int = None,
        semester_id: int = None,
        start_date=None,
        end_date=None,
        search: str = None,
        page: int = 1,
        page_size: int = 20,
        no_page: bool = False
    ) -> dict:
        queryset = UsageRecord.objects.select_related(
            'laboratory', 'teacher', 'semester'
        ).filter(is_deleted=False)
        
        if requester.is_department_admin and not requester.is_super_admin:
            queryset = queryset.filter(laboratory__department_id=requester.department_id)
        elif requester.is_laboratory_admin and not requester.is_super_admin:
            queryset = queryset.filter(laboratory__admin=requester)
        elif requester.is_teacher and not requester.is_super_admin:
            queryset = queryset.filter(teacher=requester)
        
        if laboratory_id:
            queryset = queryset.filter(laboratory_id=laboratory_id)
        if teacher_id:
            queryset = queryset.filter(teacher_id=teacher_id)
        if semester_id:
            queryset = queryset.filter(semester_id=semester_id)
        else:
            current_semester = Semester.get_current()
            if current_semester:
                queryset = queryset.filter(semester=current_semester)
        if start_date:
            queryset = queryset.filter(usage_date__gte=start_date)
        if end_date:
            queryset = queryset.filter(usage_date__lte=end_date)
        if search:
            queryset = queryset.filter(
                models.Q(laboratory__name__icontains=search) |
                models.Q(laboratory__code__icontains=search) |
                models.Q(content__icontains=search) |
                models.Q(class_name__icontains=search) |
                models.Q(teacher__nickname__icontains=search)
            )
        
        queryset = queryset.order_by('-usage_date', 'laboratory__code')
        
        if no_page:
            return {
                'list': [self._format_record(r) for r in queryset],
                'total': queryset.count(),
            }
        
        paginator = Paginator(queryset, page_size)
        page_obj = paginator.get_page(page)
        
        return {
            'list': [self._format_record(r) for r in page_obj],
            'total': paginator.count,
            'page': page,
            'page_size': page_size,
            'total_pages': paginator.num_pages,
        }

    def get_record_detail(self, requester, record_id: int) -> dict:
        try:
            record = UsageRecord.objects.select_related(
                'laboratory', 'teacher', 'semester'
            ).get(id=record_id, is_deleted=False)
        except UsageRecord.DoesNotExist:
            raise NotFoundError('使用记录不存在')
        
        if not self._can_view_record(requester, record):
            raise PermissionDenied('无权限查看该记录')
        
        return self._format_record_detail(record)

    @transaction.atomic
    def create_record(self, requester, data: dict) -> UsageRecord:
        laboratory_id = data.get('laboratory_id')
        if not laboratory_id:
            raise ValidationError('实训室为必填项')
        
        try:
            laboratory = Laboratory.objects.get(id=laboratory_id, is_deleted=False)
        except Laboratory.DoesNotExist:
            raise ValidationError('指定的实训室不存在')
        
        semester_id = data.get('semester_id')
        if semester_id:
            try:
                semester = Semester.objects.get(id=semester_id)
            except Semester.DoesNotExist:
                raise ValidationError('指定的学期不存在')
        else:
            semester = Semester.get_current()
            if not semester:
                raise ValidationError('未设置当前学期')
        
        usage_date = data.get('usage_date') or date.today()
        
        record = UsageRecord.objects.create(
            usage_date=usage_date,
            time_slot=data.get('time_slot', '1-4'),
            class_hours=data.get('class_hours', 4),
            laboratory_id=laboratory_id,
            semester=semester,
            teacher=requester,
            class_name=data.get('class_name', ''),
            student_count=data.get('student_count', 0),
            content=data.get('content', ''),
            device_status=data.get('device_status', '正常'),
            laboratory_status=data.get('laboratory_status', '正常'),
            note=data.get('note', ''),
        )
        
        return record

    @transaction.atomic
    def update_record(self, requester, record_id: int, data: dict) -> UsageRecord:
        try:
            record = UsageRecord.objects.select_related('laboratory').get(
                id=record_id, is_deleted=False
            )
        except UsageRecord.DoesNotExist:
            raise NotFoundError('使用记录不存在')
        
        if not self._can_edit_record(requester, record):
            raise PermissionDenied('无权限修改该记录')
        
        if record.is_locked:
            raise PermissionDenied('该记录已锁定，无法修改')
        
        if 'laboratory_id' in data:
            laboratory_id = data['laboratory_id']
            try:
                laboratory = Laboratory.objects.get(id=laboratory_id, is_deleted=False)
                if self._can_manage_laboratory(requester, laboratory):
                    record.laboratory_id = laboratory_id
            except Laboratory.DoesNotExist:
                raise ValidationError('指定的实训室不存在')
        
        for field in ['usage_date', 'time_slot', 'class_hours', 'class_name',
                      'student_count', 'content', 'device_status', 
                      'laboratory_status', 'note']:
            if field in data:
                setattr(record, field, data[field])
        
        record.save()
        return record

    @transaction.atomic
    def delete_record(self, requester, record_id: int) -> dict:
        try:
            record = UsageRecord.objects.select_related('laboratory').get(
                id=record_id, is_deleted=False
            )
        except UsageRecord.DoesNotExist:
            raise NotFoundError('使用记录不存在')
        
        if not self._can_delete_record(requester, record):
            raise PermissionDenied('无权限删除该记录')
        
        if record.is_archived:
            record.is_deleted = True
            record.save(update_fields=['is_deleted'])
            return {'action': 'soft_deleted', 'message': '记录已从列表移除'}
        else:
            record.delete()
            return {'action': 'deleted', 'message': '使用记录删除成功'}

    @transaction.atomic
    def batch_delete_records(self, requester, record_ids: list) -> dict:
        deleted_count = 0
        failed_list = []
        
        for record_id in record_ids:
            try:
                result = self.delete_record(requester, record_id)
                deleted_count += 1
            except Exception as e:
                failed_list.append({'id': record_id, 'reason': str(e)})
        
        return {
            'deleted_count': deleted_count,
            'failed_count': len(failed_list),
            'failed_list': failed_list,
        }

    def get_form_options(self, requester) -> dict:
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
        
        return {
            'laboratories': list(laboratories),
            'current_semester': {
                'id': current_semester.id,
                'name': current_semester.name
            } if current_semester else None,
            'default_teacher': {
                'id': requester.id,
                'name': requester.nickname or requester.username
            }
        }

    def _can_view_record(self, user, record: UsageRecord) -> bool:
        if user.is_super_admin:
            return True
        if user.is_department_admin:
            return record.laboratory.department_id == user.department_id
        if user.is_laboratory_admin:
            return record.laboratory.admin_id == user.id
        if user.is_teacher:
            return record.teacher_id == user.id
        return False

    def _can_edit_record(self, user, record: UsageRecord) -> bool:
        if user.is_super_admin:
            return True
        if user.is_department_admin:
            return record.laboratory.department_id == user.department_id
        if user.is_laboratory_admin:
            return record.laboratory.admin_id == user.id
        if user.is_teacher:
            return record.teacher_id == user.id
        return False

    def _can_delete_record(self, user, record: UsageRecord) -> bool:
        if user.is_super_admin:
            return True
        if user.is_department_admin:
            return record.laboratory.department_id == user.department_id
        if user.is_laboratory_admin:
            return record.laboratory.admin_id == user.id
        if user.is_teacher:
            return record.teacher_id == user.id
        return False

    def _can_manage_laboratory(self, user, laboratory: Laboratory) -> bool:
        if user.is_super_admin:
            return True
        if user.is_department_admin:
            return laboratory.department_id == user.department_id
        if user.is_laboratory_admin:
            return laboratory.admin_id == user.id
        return False

    def _format_record(self, record: UsageRecord) -> dict:
        return {
            'id': record.id,
            'usage_date': record.usage_date.strftime('%Y-%m-%d'),
            'time_slot': record.time_slot,
            'class_hours': record.class_hours,
            'laboratory_id': record.laboratory_id,
            'laboratory_name': record.laboratory.name,
            'laboratory_code': record.laboratory.code,
            'teacher_id': record.teacher_id,
            'teacher_name': record.teacher.nickname if record.teacher else '',
            'class_name': record.class_name,
            'student_count': record.student_count,
            'content': record.content,
            'device_status': record.device_status,
            'laboratory_status': record.laboratory_status,
            'is_locked': record.is_locked,
            'is_archived': record.is_archived,
            'note': record.note,
            'created_at': record.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        }

    def _format_record_detail(self, record: UsageRecord) -> dict:
        data = self._format_record(record)
        data.update({
            'semester_id': record.semester_id,
            'semester_name': record.semester.name if record.semester else '',
            'updated_at': record.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
        })
        return data
