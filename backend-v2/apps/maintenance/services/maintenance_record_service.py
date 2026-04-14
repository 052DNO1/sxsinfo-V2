"""
维护记录服务
"""

from django.db import models, transaction
from django.core.paginator import Paginator
from django.utils import timezone
from apps.core.exceptions import NotFoundError, PermissionDenied, ValidationError
from apps.maintenance.models import MaintenanceRecord
from apps.schedules.models import Semester
from apps.laboratories.models import Laboratory
from apps.users.models import User


class MaintenanceRecordService:
    """维护记录服务"""

    def get_record_list(
        self,
        requester,
        laboratory_id: int = None,
        maintainer_id: int = None,
        status: str = None,
        order_type: str = None,
        search: str = None,
        page: int = 1,
        page_size: int = 20,
        no_page: bool = False
    ) -> dict:
        queryset = MaintenanceRecord.objects.select_related(
            'laboratory', 'maintainer', 'semester'
        ).filter(is_deleted=False)
        
        if hasattr(requester, 'is_department_admin') and requester.is_department_admin and not requester.is_super_admin:
            if hasattr(requester, 'department_id') and requester.department_id:
                queryset = queryset.filter(laboratory__department_id=requester.department_id)
        elif hasattr(requester, 'is_laboratory_admin') and requester.is_laboratory_admin and not requester.is_super_admin:
            queryset = queryset.filter(laboratory__admin=requester)
        elif hasattr(requester, 'is_teacher') and requester.is_teacher and not requester.is_super_admin:
            queryset = queryset.filter(maintainer=requester)
        
        if laboratory_id:
            queryset = queryset.filter(laboratory_id=laboratory_id)
        if maintainer_id:
            queryset = queryset.filter(maintainer_id=maintainer_id)
        if status:
            queryset = queryset.filter(status=status)
        if order_type:
            queryset = queryset.filter(order_type=order_type)
        if search:
            queryset = queryset.filter(
                models.Q(order_number__icontains=search) |
                models.Q(content__icontains=search) |
                models.Q(laboratory__name__icontains=search) |
                models.Q(laboratory__code__icontains=search)
            )
        
        queryset = queryset.order_by('-maintenance_time')
        
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
            record = MaintenanceRecord.objects.select_related(
                'laboratory', 'maintainer', 'semester'
            ).get(id=record_id, is_deleted=False)
        except MaintenanceRecord.DoesNotExist:
            raise NotFoundError('维护记录不存在')
        
        if not self._can_view_record(requester, record):
            raise PermissionDenied('无权限查看该记录')
        
        return self._format_record_detail(record)

    @transaction.atomic
    def create_record(self, requester, data: dict) -> MaintenanceRecord:
        laboratory_id = data.get('laboratory_id')
        if not laboratory_id:
            raise ValidationError('实训实验室为必填项')
        
        try:
            laboratory = Laboratory.objects.get(id=laboratory_id, is_deleted=False)
        except Laboratory.DoesNotExist:
            raise ValidationError('指定的实训实验室不存在')
        
        semester = Semester.get_current()
        if not semester:
            raise ValidationError('未设置当前学期')
        
        content = data.get('content', '').strip()
        if not content:
            raise ValidationError('维护内容为必填项')
        
        order_type = data.get('order_type', 'W')
        order_number = MaintenanceRecord.generate_order_number(order_type)
        
        maintainer_id = data.get('maintainer_id')
        maintainer = None
        if maintainer_id:
            try:
                maintainer = User.objects.get(id=maintainer_id, is_deleted=False, is_active=True)
            except User.DoesNotExist:
                raise ValidationError('指定的维护人不存在')
        else:
            maintainer = requester
        
        maintenance_time = data.get('maintenance_time') or timezone.now()
        
        record = MaintenanceRecord.objects.create(
            order_number=order_number,
            order_type=order_type,
            laboratory_id=laboratory_id,
            maintainer=maintainer,
            content=content,
            status=data.get('status', 'maintained'),
            maintenance_time=maintenance_time,
            semester=semester,
            note=data.get('note', ''),
        )
        
        return record

    @transaction.atomic
    def update_record(self, requester, record_id: int, data: dict) -> MaintenanceRecord:
        try:
            record = MaintenanceRecord.objects.select_related('laboratory').get(
                id=record_id, is_deleted=False
            )
        except MaintenanceRecord.DoesNotExist:
            raise NotFoundError('维护记录不存在')
        
        if not self._can_edit_record(requester, record):
            raise PermissionDenied('无权限修改该记录')
        
        if 'laboratory_id' in data:
            laboratory_id = data['laboratory_id']
            try:
                laboratory = Laboratory.objects.get(id=laboratory_id, is_deleted=False)
                if self._can_manage_laboratory(requester, laboratory):
                    record.laboratory_id = laboratory_id
            except Laboratory.DoesNotExist:
                raise ValidationError('指定的实训实验室不存在')
        
        if 'maintainer_id' in data:
            maintainer_id = data['maintainer_id']
            if maintainer_id:
                try:
                    maintainer = User.objects.get(id=maintainer_id, is_deleted=False, is_active=True)
                    record.maintainer = maintainer
                except User.DoesNotExist:
                    raise ValidationError('指定的维护人不存在')
            else:
                record.maintainer = None
        
        for field in ['content', 'status', 'maintenance_time', 'note']:
            if field in data:
                setattr(record, field, data[field])
        
        record.save()
        return record

    @transaction.atomic
    def delete_record(self, requester, record_id: int) -> bool:
        try:
            record = MaintenanceRecord.objects.select_related('laboratory').get(
                id=record_id, is_deleted=False
            )
        except MaintenanceRecord.DoesNotExist:
            raise NotFoundError('维护记录不存在')
        
        if not self._can_delete_record(requester, record):
            raise PermissionDenied('无权限删除该记录')
        
        if record.is_archived:
            record.is_deleted = True
            record.save(update_fields=['is_deleted'])
        else:
            record.delete()
        return True

    @transaction.atomic
    def batch_delete_records(self, requester, record_ids: list) -> dict:
        deleted_count = 0
        failed_list = []
        
        for record_id in record_ids:
            try:
                self.delete_record(requester, record_id)
                deleted_count += 1
            except Exception as e:
                failed_list.append({'id': record_id, 'reason': str(e)})
        
        return {
            'deleted_count': deleted_count,
            'failed_count': len(failed_list),
            'failed_list': failed_list,
        }

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
            'current_laboratory': current_laboratory,
            'current_semester': {
                'id': current_semester.id,
                'name': current_semester.name
            } if current_semester else None,
            'default_maintainer': {
                'id': requester.id,
                'name': requester.nickname or requester.username
            }
        }

    def _can_view_record(self, user, record: MaintenanceRecord) -> bool:
        if user.is_super_admin:
            return True
        if user.is_department_admin:
            return record.laboratory.department_id == user.department_id
        if user.is_laboratory_admin:
            return record.laboratory.admin_id == user.id
        if user.is_teacher:
            return record.maintainer_id == user.id
        return False

    def _can_edit_record(self, user, record: MaintenanceRecord) -> bool:
        if user.is_super_admin:
            return True
        if user.is_department_admin:
            return record.laboratory.department_id == user.department_id
        if user.is_laboratory_admin:
            return record.laboratory.admin_id == user.id
        if user.is_teacher:
            return record.maintainer_id == user.id
        return False

    def _can_delete_record(self, user, record: MaintenanceRecord) -> bool:
        if user.is_super_admin:
            return True
        if user.is_department_admin:
            return record.laboratory.department_id == user.department_id
        if user.is_laboratory_admin:
            return record.laboratory.admin_id == user.id
        return False

    def _can_manage_laboratory(self, user, laboratory: Laboratory) -> bool:
        if user.is_super_admin:
            return True
        if user.is_department_admin:
            return laboratory.department_id == user.department_id
        if user.is_laboratory_admin:
            return laboratory.admin_id == user.id
        return False

    def _format_record(self, record: MaintenanceRecord) -> dict:
        status_map = {
            'maintained': '已维护',
            'pending': '待维护',
            'processing': '维护中',
        }
        
        order_type_map = {
            'W': '维护',
            'G': '故障',
        }
        
        return {
            'id': record.id,
            'order_number': record.order_number,
            'order_type': record.order_type,
            'order_type_display': order_type_map.get(record.order_type, record.order_type),
            'laboratory_id': record.laboratory_id,
            'laboratory_name': record.laboratory.name,
            'laboratory_code': record.laboratory.code,
            'maintainer_id': record.maintainer_id,
            'maintainer_name': record.maintainer.nickname if record.maintainer else '',
            'content': record.content,
            'status': record.status,
            'status_display': status_map.get(record.status, record.status),
            'maintenance_time': record.maintenance_time.strftime('%Y-%m-%d %H:%M:%S'),
            'semester_id': record.semester_id,
            'semester_name': record.semester.name,
            'note': record.note,
            'is_archived': record.is_archived,
            'created_at': record.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        }

    def _format_record_detail(self, record: MaintenanceRecord) -> dict:
        data = self._format_record(record)
        data.update({
            'updated_at': record.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
        })
        return data
