import pytest
import json
import gzip
import io
from unittest.mock import patch, MagicMock
from apps.backup.services.backup_service import BackupService, ARCHIVE_TYPE_MAP
from apps.core.exceptions import PermissionDenied, ValidationError


class TestBackupServiceArchiveTypeMap:
    def test_archive_type_map_completeness(self):
        expected_keys = ['usage_records', 'schedules', 'maintain_records',
                         'fault_records', 'lab_info', 'device_info', 'user_info']
        for key in expected_keys:
            assert key in ARCHIVE_TYPE_MAP

    def test_archive_type_map_values(self):
        assert ARCHIVE_TYPE_MAP['usage_records'] == 'records'
        assert ARCHIVE_TYPE_MAP['schedules'] == 'schedules'
        assert ARCHIVE_TYPE_MAP['maintain_records'] == 'work_orders'
        assert ARCHIVE_TYPE_MAP['fault_records'] == 'work_orders'
        assert ARCHIVE_TYPE_MAP['lab_info'] == 'laboratories'
        assert ARCHIVE_TYPE_MAP['device_info'] == 'equipment'
        assert ARCHIVE_TYPE_MAP['user_info'] == 'users'


class TestBackupServiceGetStats:
    def test_super_admin_can_get_stats(self, db, wb_super_admin):
        result = BackupService.get_backup_stats(wb_super_admin)
        assert 'users' in result
        assert 'departments' in result
        assert 'semesters' in result
        assert 'laboratories' in result
        assert 'schedules' in result
        assert 'records' in result
        assert 'work_orders' in result
        assert 'equipment' in result
        assert 'system_settings' in result
        assert 'term_archives' in result

    def test_non_admin_cannot_get_stats(self, db, wb_teacher):
        with pytest.raises(PermissionDenied, match='仅超级管理员'):
            BackupService.get_backup_stats(wb_teacher)

    def test_stats_structure(self, db, wb_super_admin):
        result = BackupService.get_backup_stats(wb_super_admin)
        for key in ['users', 'laboratories', 'schedules', 'records', 'work_orders', 'equipment']:
            assert 'active' in result[key]
            assert 'archived' in result[key]
            assert 'total' in result[key]


class TestBackupServiceValidateBackupData:
    def test_valid_data_raises_no_exception(self):
        data = {
            'version': '2.5',
            'checksum': None,
        }
        result = BackupService.validate_backup_data(data)
        assert result is True

    def test_old_version_raises(self):
        data = {
            'version': '1.0',
            'checksum': None,
        }
        with pytest.raises(ValidationError, match='版本过旧'):
            BackupService.validate_backup_data(data)

    def test_no_version_raises(self):
        data = {'checksum': None}
        with pytest.raises(ValidationError, match='版本过旧'):
            BackupService.validate_backup_data(data)

    def test_no_checksum_passes(self):
        data = {'version': '2.5'}
        result = BackupService.validate_backup_data(data)
        assert result is True


class TestBackupServiceParseBackupFile:
    def test_parse_json_file(self):
        data = {'version': '2.5', 'data': {}}
        mock_file = MagicMock()
        mock_file.name = 'backup.json'
        mock_file.read.return_value = json.dumps(data).encode('utf-8')
        mock_file.seek(0)
        result = BackupService.parse_backup_file(mock_file)
        assert result['version'] == '2.5'

    def test_parse_gz_file(self):
        data = {'version': '2.5', 'data': {}}
        json_bytes = json.dumps(data).encode('utf-8')
        gz_buffer = io.BytesIO()
        with gzip.GzipFile(fileobj=gz_buffer, mode='wb') as gz:
            gz.write(json_bytes)
        gz_buffer.seek(0)

        class GzFile:
            name = 'backup.json.gz'
            def __init__(self, buf):
                self._buf = buf
            def read(self, size=-1):
                if size == -1:
                    return self._buf.read()
                return self._buf.read(size)
            def seek(self, pos):
                self._buf.seek(pos)

        result = BackupService.parse_backup_file(GzFile(gz_buffer))
        assert result['version'] == '2.5'


class TestAutoBackupConfigService:
    def test_get_config_default(self, db, wb_super_admin):
        from apps.backup.services.auto_backup_service import AutoBackupConfigService
        service = AutoBackupConfigService()
        result = service.get_config(wb_super_admin)
        assert 'enabled' in result
        assert 'period' in result

    def test_save_config(self, db, wb_super_admin):
        from apps.backup.services.auto_backup_service import AutoBackupConfigService
        service = AutoBackupConfigService()
        result = service.save_config(wb_super_admin, {
            'enabled': True,
            'period': 'daily',
        })
        assert result['enabled'] is True
        assert result['period'] == 'daily'

    def test_save_config_invalid_period(self, db, wb_super_admin):
        from apps.backup.services.auto_backup_service import AutoBackupConfigService
        service = AutoBackupConfigService()
        with pytest.raises(ValidationError, match='无效的备份周期'):
            service.save_config(wb_super_admin, {
                'enabled': True,
                'period': 'hourly',
            })

    def test_non_admin_cannot_get_config(self, db, wb_teacher):
        from apps.backup.services.auto_backup_service import AutoBackupConfigService
        service = AutoBackupConfigService()
        with pytest.raises(PermissionDenied):
            service.get_config(wb_teacher)
