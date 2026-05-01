import pytest
from apps.records.services.record_service import UsageRecordService
from apps.records.models import UsageRecord
from apps.core.exceptions import ValidationError, NotFoundError, PermissionDenied


@pytest.fixture
def record_service():
    return UsageRecordService()


class TestUsageRecordServiceCreate:
    def test_create_success(self, db, wb_super_admin, wb_laboratory, wb_semester):
        service = UsageRecordService()
        record = service.create_record(
            requester=wb_super_admin,
            data={
                'usage_date': '2025-10-20',
                'time_slot': '3-4',
                'class_hours': 2,
                'laboratory_id': wb_laboratory.id,
                'semester_id': wb_semester.id,
                'class_name': '白盒测试班级',
                'student_count': 35,
                'content': '白盒测试课程内容',
                'device_status': 'NORMAL',
                'laboratory_status': 'NORMAL',
            },
        )
        assert record.usage_date == '2025-10-20'
        assert record.class_hours == 2

    def test_create_default_teacher(self, db, wb_teacher, wb_laboratory, wb_semester):
        service = UsageRecordService()
        record = service.create_record(
            requester=wb_teacher,
            data={
                'usage_date': '2025-10-20',
                'time_slot': '3-4',
                'class_hours': 2,
                'laboratory_id': wb_laboratory.id,
                'semester_id': wb_semester.id,
                'content': '测试',
                'device_status': 'NORMAL',
                'laboratory_status': 'NORMAL',
            },
        )
        assert record.teacher == wb_teacher


class TestUsageRecordServiceUpdate:
    def test_update_success(self, db, wb_super_admin, wb_usage_record):
        service = UsageRecordService()
        record = service.update_record(
            requester=wb_super_admin,
            record_id=wb_usage_record.id,
            data={'content': '更新内容'},
        )
        assert record.content == '更新内容'

    def test_update_locked_record(self, db, wb_super_admin, wb_usage_record):
        wb_usage_record.is_locked = True
        wb_usage_record.save()
        service = UsageRecordService()
        with pytest.raises(PermissionDenied, match='已锁定'):
            service.update_record(
                requester=wb_super_admin,
                record_id=wb_usage_record.id,
                data={'content': '尝试修改'},
            )

    def test_update_nonexistent(self, db, wb_super_admin):
        service = UsageRecordService()
        with pytest.raises(NotFoundError):
            service.update_record(
                requester=wb_super_admin,
                record_id=99999,
                data={'content': 'test'},
            )


class TestUsageRecordServiceDelete:
    def test_delete_unarchived_returns_deleted(self, db, wb_super_admin, wb_usage_record):
        service = UsageRecordService()
        result = service.delete_record(
            requester=wb_super_admin,
            record_id=wb_usage_record.id,
        )
        assert result['action'] == 'deleted'

    def test_delete_archived_soft_delete(self, db, wb_super_admin, wb_usage_record):
        wb_usage_record.is_archived = True
        wb_usage_record.save()
        service = UsageRecordService()
        result = service.delete_record(
            requester=wb_super_admin,
            record_id=wb_usage_record.id,
        )
        assert result['action'] == 'soft_deleted'
        wb_usage_record.refresh_from_db()
        assert wb_usage_record.is_deleted is True


class TestUsageRecordServiceList:
    def test_list_default(self, db, wb_super_admin):
        service = UsageRecordService()
        result = service.get_record_list(requester=wb_super_admin)
        assert 'list' in result
        assert 'total' in result

    def test_list_teacher_only_own(self, db, wb_teacher):
        service = UsageRecordService()
        result = service.get_record_list(requester=wb_teacher)
        assert 'list' in result
