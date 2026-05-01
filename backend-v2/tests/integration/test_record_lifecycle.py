import pytest
from apps.records.services.record_service import UsageRecordService
from apps.records.models import UsageRecord
from apps.core.exceptions import PermissionDenied


class TestRecordLockAndArchive:
    def test_create_update_lock(self, db, wb_super_admin, wb_laboratory, wb_semester):
        service = UsageRecordService()
        record = service.create_record(
            requester=wb_super_admin,
            data={
                'usage_date': '2025-10-20',
                'time_slot': '3-4',
                'class_hours': 2,
                'laboratory_id': wb_laboratory.id,
                'semester_id': wb_semester.id,
                'content': '测试内容',
                'device_status': 'NORMAL',
                'laboratory_status': 'NORMAL',
            },
        )
        assert record.is_locked is False

        record.is_locked = True
        record.save()

        with pytest.raises(PermissionDenied, match='已锁定'):
            service.update_record(
                requester=wb_super_admin,
                record_id=record.id,
                data={'content': '尝试修改锁定记录'},
            )

    def test_create_archive_soft_delete(self, db, wb_super_admin, wb_laboratory, wb_semester):
        service = UsageRecordService()
        record = service.create_record(
            requester=wb_super_admin,
            data={
                'usage_date': '2025-10-20',
                'time_slot': '3-4',
                'class_hours': 2,
                'laboratory_id': wb_laboratory.id,
                'semester_id': wb_semester.id,
                'content': '归档测试',
                'device_status': 'NORMAL',
                'laboratory_status': 'NORMAL',
            },
        )

        record.is_archived = True
        record.save()

        result = service.delete_record(requester=wb_super_admin, record_id=record.id)
        assert result['action'] == 'soft_deleted'
        record.refresh_from_db()
        assert record.is_deleted is True

    def test_full_record_lifecycle(self, db, wb_super_admin, wb_laboratory, wb_semester):
        service = UsageRecordService()
        record = service.create_record(
            requester=wb_super_admin,
            data={
                'usage_date': '2025-10-20',
                'time_slot': '3-4',
                'class_hours': 2,
                'laboratory_id': wb_laboratory.id,
                'semester_id': wb_semester.id,
                'content': '生命周期测试',
                'device_status': 'NORMAL',
                'laboratory_status': 'NORMAL',
            },
        )

        updated = service.update_record(
            requester=wb_super_admin,
            record_id=record.id,
            data={'content': '更新内容'},
        )
        assert updated.content == '更新内容'

        result = service.delete_record(requester=wb_super_admin, record_id=record.id)
        assert result['action'] == 'deleted'
