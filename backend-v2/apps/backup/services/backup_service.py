"""
备份恢复服务
"""

import json
import os
import logging
from datetime import datetime
from django.http import HttpResponse
from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder
from apps.core.exceptions import PermissionDenied, ValidationError
from apps.users.models import User, Department
from apps.laboratories.models import Laboratory, Equipment
from apps.schedules.models import Schedule, Semester
from apps.records.models import UsageRecord
from apps.maintenance.models import WorkOrder

logger = logging.getLogger(__name__)


class BackupService:
    """备份恢复服务"""

    BACKUP_DIR = os.path.join(settings.BASE_DIR, 'backups')

    @classmethod
    def get_backup_stats(cls, requester) -> dict:
        if not requester.is_super_admin:
            raise PermissionDenied('仅超级管理员可执行此操作')

        return {
            'users': User.objects.filter(is_deleted=False).count(),
            'departments': Department.objects.filter(is_deleted=False).count(),
            'semesters': Semester.objects.filter(is_deleted=False).count(),
            'laboratories': Laboratory.objects.filter(is_deleted=False).count(),
            'schedules': Schedule.objects.filter(is_deleted=False).count(),
            'records': UsageRecord.objects.filter(is_deleted=False).count(),
            'work_orders': WorkOrder.objects.filter(is_deleted=False).count(),
            'equipment': Equipment.objects.filter(is_deleted=False).count(),
        }

    @classmethod
    def export_backup(cls, requester) -> HttpResponse:
        if not requester.is_super_admin:
            raise PermissionDenied('仅超级管理员可执行此操作')

        backup_data = {
            'version': '2.0',
            'created_at': datetime.now().isoformat(),
            'created_by': requester.username,
            'data': {}
        }

        backup_data['data']['departments'] = list(
            Department.objects.filter(is_deleted=False).values()
        )
        backup_data['data']['users'] = list(
            User.objects.filter(is_deleted=False).values(
                'id', 'username', 'nickname', 'email', 'phone',
                'role', 'department_id', 'is_active', 'created_at'
            )
        )
        backup_data['data']['semesters'] = list(
            Semester.objects.filter(is_deleted=False).values()
        )
        backup_data['data']['laboratories'] = list(
            Laboratory.objects.filter(is_deleted=False).values()
        )
        backup_data['data']['schedules'] = list(
            Schedule.objects.filter(is_deleted=False).values()
        )
        backup_data['data']['records'] = list(
            UsageRecord.objects.filter(is_deleted=False).values()
        )
        backup_data['data']['work_orders'] = list(
            WorkOrder.objects.filter(is_deleted=False).values()
        )
        backup_data['data']['equipment'] = list(
            Equipment.objects.filter(is_deleted=False).values()
        )

        json_data = json.dumps(backup_data, cls=DjangoJSONEncoder, ensure_ascii=False, indent=2)

        filename = f'lims_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'

        response = HttpResponse(json_data, content_type='application/json')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'

        return response

    @classmethod
    def get_backup_info(cls, backup_data: dict) -> dict:
        info = {
            'version': backup_data.get('version', 'unknown'),
            'created_at': backup_data.get('created_at', 'unknown'),
            'created_by': backup_data.get('created_by', 'unknown'),
            'counts': {}
        }

        data = backup_data.get('data', {})
        for key, items in data.items():
            info['counts'][key] = len(items) if isinstance(items, list) else 0

        return info

    @classmethod
    def restore_backup(cls, requester, backup_data: dict, options: dict = None) -> dict:
        if not requester.is_super_admin:
            raise PermissionDenied('仅超级管理员可执行此操作')

        options = options or {}
        clear_existing = options.get('clear_existing', False)

        results = {
            'success': True,
            'restored': {},
            'errors': []
        }

        try:
            data = backup_data.get('data', {})

            if clear_existing:
                cls._clear_existing_data()

            if 'departments' in data:
                count = cls._restore_departments(data['departments'])
                results['restored']['departments'] = count

            if 'users' in data:
                count = cls._restore_users(data['users'])
                results['restored']['users'] = count

            if 'semesters' in data:
                count = cls._restore_semesters(data['semesters'])
                results['restored']['semesters'] = count

            if 'laboratories' in data:
                count = cls._restore_laboratories(data['laboratories'])
                results['restored']['laboratories'] = count

            if 'schedules' in data:
                count = cls._restore_schedules(data['schedules'])
                results['restored']['schedules'] = count

            if 'records' in data:
                count = cls._restore_records(data['records'])
                results['restored']['records'] = count

            if 'work_orders' in data:
                count = cls._restore_work_orders(data['work_orders'])
                results['restored']['work_orders'] = count

            if 'equipment' in data:
                count = cls._restore_equipment(data['equipment'])
                results['restored']['equipment'] = count

        except Exception as e:
            results['success'] = False
            results['errors'].append(str(e))
            logger.error(f"恢复备份失败: {str(e)}")

        return results

    @classmethod
    def _clear_existing_data(cls):
        WorkOrder.objects.all().delete()
        UsageRecord.objects.all().delete()
        Schedule.objects.all().delete()
        Equipment.objects.all().delete()
        Laboratory.objects.all().delete()
        Semester.objects.all().delete()
        User.objects.filter(is_superuser=False).delete()
        Department.objects.all().delete()

    @classmethod
    def _restore_departments(cls, departments: list) -> int:
        count = 0
        for dept_data in departments:
            try:
                Department.objects.update_or_create(
                    id=dept_data['id'],
                    defaults=dept_data
                )
                count += 1
            except Exception as e:
                logger.warning(f"恢复部门失败: {e}")
        return count

    @classmethod
    def _restore_users(cls, users: list) -> int:
        count = 0
        for user_data in users:
            try:
                User.objects.update_or_create(
                    id=user_data['id'],
                    defaults=user_data
                )
                count += 1
            except Exception as e:
                logger.warning(f"恢复用户失败: {e}")
        return count

    @classmethod
    def _restore_semesters(cls, semesters: list) -> int:
        count = 0
        for sem_data in semesters:
            try:
                Semester.objects.update_or_create(
                    id=sem_data['id'],
                    defaults=sem_data
                )
                count += 1
            except Exception as e:
                logger.warning(f"恢复学期失败: {e}")
        return count

    @classmethod
    def _restore_laboratories(cls, laboratories: list) -> int:
        count = 0
        for lab_data in laboratories:
            try:
                Laboratory.objects.update_or_create(
                    id=lab_data['id'],
                    defaults=lab_data
                )
                count += 1
            except Exception as e:
                logger.warning(f"恢复实训室失败: {e}")
        return count

    @classmethod
    def _restore_schedules(cls, schedules: list) -> int:
        count = 0
        for schedule_data in schedules:
            try:
                Schedule.objects.update_or_create(
                    id=schedule_data['id'],
                    defaults=schedule_data
                )
                count += 1
            except Exception as e:
                logger.warning(f"恢复课表失败: {e}")
        return count

    @classmethod
    def _restore_records(cls, records: list) -> int:
        count = 0
        for record_data in records:
            try:
                UsageRecord.objects.update_or_create(
                    id=record_data['id'],
                    defaults=record_data
                )
                count += 1
            except Exception as e:
                logger.warning(f"恢复使用记录失败: {e}")
        return count

    @classmethod
    def _restore_work_orders(cls, work_orders: list) -> int:
        count = 0
        for order_data in work_orders:
            try:
                WorkOrder.objects.update_or_create(
                    id=order_data['id'],
                    defaults=order_data
                )
                count += 1
            except Exception as e:
                logger.warning(f"恢复工单失败: {e}")
        return count

    @classmethod
    def _restore_equipment(cls, equipment: list) -> int:
        count = 0
        for eq_data in equipment:
            try:
                Equipment.objects.update_or_create(
                    id=eq_data['id'],
                    defaults=eq_data
                )
                count += 1
            except Exception as e:
                logger.warning(f"恢复设备失败: {e}")
        return count
