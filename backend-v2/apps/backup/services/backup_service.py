"""
备份恢复服务 - 改进版
支持 Gzip 压缩、校验机制、本地存储、归档数据（含学期归档）
"""

import json
import os
import io
import gzip
import hashlib
import logging
from datetime import datetime
from django.http import HttpResponse
from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder
from apps.core.exceptions import PermissionDenied, ValidationError
from apps.users.models import User, Department, SystemSetting
from apps.laboratories.models import Laboratory, Equipment
from apps.schedules.models import Schedule, Semester, TermArchive
from apps.records.models import UsageRecord
from apps.maintenance.models import WorkOrder

logger = logging.getLogger(__name__)

ARCHIVE_TYPE_MAP = {
    'usage_records': 'records',
    'schedules': 'schedules',
    'maintain_records': 'work_orders',
    'fault_records': 'work_orders',
    'lab_info': 'laboratories',
    'device_info': 'equipment',
    'user_info': 'users',
}


class BackupService:
    """备份恢复服务 - 支持完整数据备份（含归档数据+学期归档）"""

    BACKUP_DIR = os.path.join(settings.BASE_DIR, 'backups')
    BACKUP_VERSION = '2.5'
    MAX_BACKUP_FILES = 10

    @classmethod
    def get_backup_stats(cls, requester) -> dict:
        if not requester.is_super_admin:
            raise PermissionDenied('仅超级管理员可执行此操作')

        archive_stats = cls._get_term_archive_stats()

        return {
            'users': cls._merge_stats(cls._get_model_stats(User), archive_stats.get('users', {})),
            'departments': cls._get_model_stats(Department),
            'semesters': cls._get_model_stats(Semester),
            'term_archives': {'total': cls._safe_count(TermArchive)},
            'laboratories': cls._merge_stats(cls._get_model_stats(Laboratory), archive_stats.get('laboratories', {})),
            'schedules': cls._merge_stats(cls._get_model_stats(Schedule), archive_stats.get('schedules', {})),
            'records': cls._merge_stats(cls._get_model_stats(UsageRecord), archive_stats.get('records', {})),
            'work_orders': cls._merge_stats(cls._get_model_stats(WorkOrder), archive_stats.get('work_orders', {})),
            'equipment': cls._merge_stats(cls._get_model_stats(Equipment), archive_stats.get('equipment', {})),
            'system_settings': {'total': cls._safe_count(SystemSetting)},
        }

    @classmethod
    def _get_term_archive_stats(cls) -> dict:
        stats = {}
        try:
            archives = TermArchive.objects.all()
            for archive in archives:
                atype = archive.archive_type
                target_key = ARCHIVE_TYPE_MAP.get(atype)
                if not target_key:
                    continue

                content = archive.content
                count = len(content) if isinstance(content, list) else 0

                if target_key not in stats:
                    stats[target_key] = {'archived_from_term': 0}

                stats[target_key]['archived_from_term'] = stats[target_key].get('archived_from_term', 0) + count
        except Exception as e:
            logger.warning(f"统计学期归档数据失败: {e}")
        return stats

    @classmethod
    def _merge_stats(cls, db_stats: dict, archive_stats: dict) -> dict:
        archived_extra = archive_stats.get('archived_from_term', 0)
        return {
            'active': db_stats.get('active', 0),
            'archived': db_stats.get('archived', 0) + archived_extra,
            'total': db_stats.get('total', 0) + archived_extra,
            'archived_from_term': archived_extra,
        }

    @classmethod
    def _get_model_stats(cls, model) -> dict:
        active = model.objects.filter(is_deleted=False).count()
        archived = model.objects.filter(is_deleted=True).count()
        return {
            'active': active,
            'archived': archived,
            'total': active + archived
        }

    @classmethod
    def _safe_count(cls, model) -> int:
        try:
            return model.objects.count()
        except Exception as e:
            logger.warning(f"统计 {model.__name__} 失败: {e}")
            return 0

    @classmethod
    def export_backup(cls, requester, compress: bool = True, save_local: bool = True) -> HttpResponse:
        if not requester.is_super_admin:
            raise PermissionDenied('仅超级管理员可执行此操作')

        backup_data = {
            'version': cls.BACKUP_VERSION,
            'created_at': datetime.now().isoformat(),
            'created_by': requester.username,
            'checksum': None,
            'compressed': compress,
            'include_archived': True,
            'include_term_archive': True,
            'data': cls._collect_backup_data()
        }

        json_str = json.dumps(backup_data, cls=DjangoJSONEncoder, ensure_ascii=False, indent=2)
        checksum = cls._calculate_checksum(json_str)
        backup_data['checksum'] = checksum
        json_str = json.dumps(backup_data, cls=DjangoJSONEncoder, ensure_ascii=False, indent=2)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        if compress:
            response = cls._create_gzip_response(json_str, timestamp)
            if save_local:
                cls._save_backup_local(json_str, timestamp, compressed=True)
        else:
            response = cls._create_json_response(json_str, timestamp)
            if save_local:
                cls._save_backup_local(json_str, timestamp, compressed=False)

        cls._cleanup_old_backups()
        
        return response

    @classmethod
    def _collect_backup_data(cls) -> dict:
        db_data = {
            'departments': list(Department.objects.values()),
            'users': list(User.objects.values(
                'id', 'username', 'nickname', 'email', 'phone',
                'role', 'department_id', 'is_active', 'is_superuser',
                'is_deleted', 'deleted_at', 'created_at'
            )),
            'semesters': list(Semester.objects.values()),
            'term_archives': list(TermArchive.objects.values()),
            'laboratories': list(Laboratory.objects.values()),
            'schedules': list(Schedule.objects.values()),
            'records': list(UsageRecord.objects.values()),
            'work_orders': list(WorkOrder.objects.values()),
            'equipment': list(Equipment.objects.values()),
            'system_settings': list(SystemSetting.objects.values()),
        }

        expanded_archive = cls._expand_term_archives()
        for key, items in expanded_archive.items():
            if key in db_data and items:
                existing_ids = {item.get('id') for item in db_data[key] if item.get('id')}
                new_items = [item for item in items if item.get('id') not in existing_ids]
                db_data[key].extend(new_items)

        return db_data

    @classmethod
    def _expand_term_archives(cls) -> dict:
        expanded = {}
        try:
            archives = TermArchive.objects.all()
            for archive in archives:
                atype = archive.archive_type
                target_key = ARCHIVE_TYPE_MAP.get(atype)
                if not target_key:
                    continue

                content = archive.content
                if isinstance(content, list):
                    if target_key not in expanded:
                        expanded[target_key] = []
                    for item in content:
                        if isinstance(item, dict):
                            item['_source'] = 'term_archive'
                            item['_archive_id'] = archive.id
                            item['_archive_type'] = atype
                            expanded[target_key].append(item)
        except Exception as e:
            logger.warning(f"展开学期归档数据失败: {e}")
        return expanded

    @classmethod
    def _calculate_checksum(cls, data: str) -> str:
        return hashlib.sha256(data.encode('utf-8')).hexdigest()[:16]

    @classmethod
    def _create_gzip_response(cls, json_str: str, timestamp: str) -> HttpResponse:
        buffer = io.BytesIO()
        with gzip.GzipFile(fileobj=buffer, mode='wb', compresslevel=6) as gz:
            gz.write(json_str.encode('utf-8'))
        
        buffer.seek(0)
        filename = f'lims_backup_{timestamp}.json.gz'
        
        response = HttpResponse(buffer.getvalue(), content_type='application/gzip')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response

    @classmethod
    def _create_json_response(cls, json_str: str, timestamp: str) -> HttpResponse:
        filename = f'lims_backup_{timestamp}.json'
        response = HttpResponse(json_str, content_type='application/json')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response

    @classmethod
    def _save_backup_local(cls, json_str: str, timestamp: str, compressed: bool = True):
        try:
            os.makedirs(cls.BACKUP_DIR, exist_ok=True)
            
            if compressed:
                filename = f'lims_backup_{timestamp}.json.gz'
                filepath = os.path.join(cls.BACKUP_DIR, filename)
                with gzip.open(filepath, 'wt', encoding='utf-8', compresslevel=6) as gz:
                    gz.write(json_str)
            else:
                filename = f'lims_backup_{timestamp}.json'
                filepath = os.path.join(cls.BACKUP_DIR, filename)
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(json_str)
            
            logger.info(f"备份文件已保存到服务器: {filename}")
        except Exception as e:
            logger.error(f"保存备份文件到服务器失败: {e}")

    @classmethod
    def _cleanup_old_backups(cls):
        try:
            if not os.path.exists(cls.BACKUP_DIR):
                return
            
            files = []
            for f in os.listdir(cls.BACKUP_DIR):
                if f.startswith('lims_backup_') and (f.endswith('.json') or f.endswith('.json.gz')):
                    filepath = os.path.join(cls.BACKUP_DIR, f)
                    files.append((filepath, os.path.getmtime(filepath)))
            
            files.sort(key=lambda x: x[1], reverse=True)
            
            for filepath, _ in files[cls.MAX_BACKUP_FILES:]:
                os.remove(filepath)
                logger.info(f"已删除旧备份文件: {os.path.basename(filepath)}")
                
        except Exception as e:
            logger.error(f"清理旧备份文件失败: {e}")

    @classmethod
    def get_backup_info(cls, backup_data: dict) -> dict:
        info = {
            'version': backup_data.get('version', 'unknown'),
            'created_at': backup_data.get('created_at', 'unknown'),
            'created_by': backup_data.get('created_by', 'unknown'),
            'compressed': backup_data.get('compressed', False),
            'include_archived': backup_data.get('include_archived', True),
            'include_term_archive': backup_data.get('include_term_archive', False),
            'checksum': backup_data.get('checksum', None),
            'counts': {}
        }

        data = backup_data.get('data', {})
        for key, items in data.items():
            if isinstance(items, list):
                from_archive = sum(1 for item in items if item.get('_source') == 'term_archive')
                active_count = sum(1 for item in items if not item.get('is_deleted', False))
                archived_count = len(items) - active_count
                info['counts'][key] = {
                    'total': len(items),
                    'active': active_count,
                    'archived': archived_count,
                    'from_term_archive': from_archive,
                }

        return info

    @classmethod
    def parse_backup_file(cls, backup_file) -> dict:
        filename = backup_file.name.lower() if hasattr(backup_file, 'name') else ''
        
        try:
            if filename.endswith('.gz'):
                with gzip.GzipFile(fileobj=backup_file, mode='rb') as gz:
                    content = gz.read().decode('utf-8')
                backup_data = json.loads(content)
            else:
                backup_data = json.load(backup_file)
            
            return backup_data
        except json.JSONDecodeError as e:
            raise ValidationError('备份文件格式错误，无法解析 JSON')
        except gzip.BadGzipFile:
            raise ValidationError('压缩文件格式错误，请确认是有效的 Gzip 文件')
        except Exception as e:
            raise ValidationError(f'读取备份文件失败: {str(e)}')

    @classmethod
    def validate_backup_data(cls, backup_data: dict) -> bool:
        version = backup_data.get('version', '1.0')
        
        if version < '2.0':
            raise ValidationError(f'备份文件版本过旧 ({version})，请使用 {cls.BACKUP_VERSION} 或更高版本')
        
        stored_checksum = backup_data.get('checksum')
        if stored_checksum:
            data_copy = dict(backup_data)
            data_copy['checksum'] = None
            json_str = json.dumps(data_copy, cls=DjangoJSONEncoder, ensure_ascii=False)
            computed_checksum = cls._calculate_checksum(json_str)
            
            if stored_checksum != computed_checksum:
                raise ValidationError('备份文件校验失败，文件可能已损坏或被篡改')
        
        return True

    @classmethod
    def restore_backup(cls, requester, backup_data: dict, options: dict = None) -> dict:
        if not requester.is_super_admin:
            raise PermissionDenied('仅超级管理员可执行此操作')

        cls.validate_backup_data(backup_data)

        options = options or {}
        clear_existing = options.get('clear_existing', False)

        results = {
            'success': True,
            'restored': {},
            'errors': [],
            'version': backup_data.get('version', 'unknown'),
            'restored_archived': 0,
            'restored_active': 0,
            'restored_from_archive': 0
        }

        try:
            data = backup_data.get('data', {})

            if clear_existing:
                cls._clear_existing_data()

            restore_order = [
                ('departments', cls._restore_departments),
                ('users', cls._restore_users),
                ('semesters', cls._restore_semesters),
                ('term_archives', cls._restore_term_archives),
                ('laboratories', cls._restore_laboratories),
                ('schedules', cls._restore_schedules),
                ('records', cls._restore_records),
                ('work_orders', cls._restore_work_orders),
                ('equipment', cls._restore_equipment),
                ('system_settings', cls._restore_system_settings),
            ]

            for key, restore_func in restore_order:
                if key in data:
                    count, archived, active, from_archive = restore_func(data[key])
                    results['restored'][key] = count
                    results['restored_archived'] += archived
                    results['restored_active'] += active
                    results['restored_from_archive'] += from_archive

        except Exception as e:
            results['success'] = False
            results['errors'].append(str(e))
            logger.error(f"恢复备份失败: {str(e)}")

        return results

    @classmethod
    def _clear_existing_data(cls):
        SystemSetting.objects.all().delete()
        TermArchive.objects.all().delete()
        WorkOrder.objects.all().delete()
        UsageRecord.objects.all().delete()
        Schedule.objects.all().delete()
        Equipment.objects.all().delete()
        Laboratory.objects.all().delete()
        Semester.objects.all().delete()
        User.objects.filter(is_superuser=False).delete()
        Department.objects.all().delete()

    @classmethod
    def _clean_item(cls, item: dict) -> dict:
        keys_to_remove = {'_source', '_archive_id', '_archive_type'}
        return {k: v for k, v in item.items() if k not in keys_to_remove}

    @classmethod
    def _restore_departments(cls, departments: list) -> tuple:
        count = 0
        archived = 0
        active = 0
        from_archive = 0
        for dept_data in departments:
            try:
                clean_data = cls._clean_item(dept_data)
                Department.objects.update_or_create(
                    id=dept_data['id'],
                    defaults=clean_data
                )
                count += 1
                if dept_data.get('_source') == 'term_archive':
                    from_archive += 1
                elif dept_data.get('is_deleted'):
                    archived += 1
                else:
                    active += 1
            except Exception as e:
                logger.warning(f"恢复部门失败: {e}")
        return count, archived, active, from_archive

    @classmethod
    def _restore_users(cls, users: list) -> tuple:
        count = 0
        archived = 0
        active = 0
        from_archive = 0
        for user_data in users:
            try:
                clean_data = cls._clean_item(user_data)
                clean_data = {k: v for k, v in clean_data.items() if k != 'password'}
                User.objects.update_or_create(
                    id=user_data['id'],
                    defaults=clean_data
                )
                count += 1
                if user_data.get('_source') == 'term_archive':
                    from_archive += 1
                elif user_data.get('is_deleted'):
                    archived += 1
                else:
                    active += 1
            except Exception as e:
                logger.warning(f"恢复用户失败: {e}")
        return count, archived, active, from_archive

    @classmethod
    def _restore_semesters(cls, semesters: list) -> tuple:
        count = 0
        archived = 0
        active = 0
        from_archive = 0
        for sem_data in semesters:
            try:
                clean_data = cls._clean_item(sem_data)
                Semester.objects.update_or_create(
                    id=sem_data['id'],
                    defaults=clean_data
                )
                count += 1
                if sem_data.get('_source') == 'term_archive':
                    from_archive += 1
                elif sem_data.get('is_deleted'):
                    archived += 1
                else:
                    active += 1
            except Exception as e:
                logger.warning(f"恢复学期失败: {e}")
        return count, archived, active, from_archive

    @classmethod
    def _restore_term_archives(cls, archives: list) -> tuple:
        count = 0
        for archive_data in archives:
            try:
                clean_data = cls._clean_item(archive_data)
                TermArchive.objects.update_or_create(
                    id=archive_data['id'],
                    defaults=clean_data
                )
                count += 1
            except Exception as e:
                logger.warning(f"恢复学期归档失败: {e}")
        return count, 0, count, 0

    @classmethod
    def _restore_laboratories(cls, laboratories: list) -> tuple:
        count = 0
        archived = 0
        active = 0
        from_archive = 0
        for lab_data in laboratories:
            try:
                clean_data = cls._clean_item(lab_data)
                Laboratory.objects.update_or_create(
                    id=lab_data['id'],
                    defaults=clean_data
                )
                count += 1
                if lab_data.get('_source') == 'term_archive':
                    from_archive += 1
                elif lab_data.get('is_deleted'):
                    archived += 1
                else:
                    active += 1
            except Exception as e:
                logger.warning(f"恢复实训室失败: {e}")
        return count, archived, active, from_archive

    @classmethod
    def _restore_schedules(cls, schedules: list) -> tuple:
        count = 0
        archived = 0
        active = 0
        from_archive = 0
        for schedule_data in schedules:
            try:
                clean_data = cls._clean_item(schedule_data)
                Schedule.objects.update_or_create(
                    id=schedule_data['id'],
                    defaults=clean_data
                )
                count += 1
                if schedule_data.get('_source') == 'term_archive':
                    from_archive += 1
                elif schedule_data.get('is_deleted'):
                    archived += 1
                else:
                    active += 1
            except Exception as e:
                logger.warning(f"恢复课表失败: {e}")
        return count, archived, active, from_archive

    @classmethod
    def _restore_records(cls, records: list) -> tuple:
        count = 0
        archived = 0
        active = 0
        from_archive = 0
        for record_data in records:
            try:
                clean_data = cls._clean_item(record_data)
                UsageRecord.objects.update_or_create(
                    id=record_data['id'],
                    defaults=clean_data
                )
                count += 1
                if record_data.get('_source') == 'term_archive':
                    from_archive += 1
                elif record_data.get('is_deleted'):
                    archived += 1
                else:
                    active += 1
            except Exception as e:
                logger.warning(f"恢复使用记录失败: {e}")
        return count, archived, active, from_archive

    @classmethod
    def _restore_work_orders(cls, work_orders: list) -> tuple:
        count = 0
        archived = 0
        active = 0
        from_archive = 0
        for order_data in work_orders:
            try:
                clean_data = cls._clean_item(order_data)
                WorkOrder.objects.update_or_create(
                    id=order_data['id'],
                    defaults=clean_data
                )
                count += 1
                if order_data.get('_source') == 'term_archive':
                    from_archive += 1
                elif order_data.get('is_deleted'):
                    archived += 1
                else:
                    active += 1
            except Exception as e:
                logger.warning(f"恢复工单失败: {e}")
        return count, archived, active, from_archive

    @classmethod
    def _restore_equipment(cls, equipment: list) -> tuple:
        count = 0
        archived = 0
        active = 0
        from_archive = 0
        for eq_data in equipment:
            try:
                clean_data = cls._clean_item(eq_data)
                Equipment.objects.update_or_create(
                    id=eq_data['id'],
                    defaults=clean_data
                )
                count += 1
                if eq_data.get('_source') == 'term_archive':
                    from_archive += 1
                elif eq_data.get('is_deleted'):
                    archived += 1
                else:
                    active += 1
            except Exception as e:
                logger.warning(f"恢复设备失败: {e}")
        return count, archived, active, from_archive

    @classmethod
    def _restore_system_settings(cls, settings: list) -> tuple:
        count = 0
        for setting_data in settings:
            try:
                SystemSetting.objects.update_or_create(
                    key=setting_data['key'],
                    defaults=setting_data
                )
                count += 1
            except Exception as e:
                logger.warning(f"恢复系统设置失败: {e}")
        return count, 0, count, 0
