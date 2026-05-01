import pytest
from apps.records.services.record_service import UsageRecordService
from apps.records.models import UsageRecord
from apps.core.exceptions import PermissionDenied


@pytest.fixture
def record_service():
    return UsageRecordService()


class TestUsageRecordServiceUpdate:
    def test_update_locked_record(self, db, wb_super_admin, wb_usage_record):
        wb_usage_record.is_locked = True
        wb_usage_record.save()
        service = UsageRecordService()
        with pytest.raises(PermissionDenied, match='已锁定'):
            service.update_record(wb_super_admin, wb_usage_record.id, {'content': 'test'})


class TestUsageRecordServiceDelete:
    def test_delete_unarchived(self, db, wb_super_admin, wb_usage_record):
        service = UsageRecordService()
        result = service.delete_record(wb_super_admin, wb_usage_record.id)
        assert result['action'] == 'deleted'

    def test_delete_archived_soft(self, db, wb_super_admin, wb_usage_record):
        wb_usage_record.is_archived = True
        wb_usage_record.save()
        service = UsageRecordService()
        result = service.delete_record(wb_super_admin, wb_usage_record.id)
        assert result['action'] == 'soft_deleted'
        wb_usage_record.refresh_from_db()
        assert wb_usage_record.is_deleted is True
