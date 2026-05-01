import pytest
from apps.schedules.services.schedule_service import ScheduleService
from apps.schedules.models import Schedule
from apps.core.exceptions import ValidationError, NotFoundError, PermissionDenied, ScheduleConflictError
from apps.core.constants import UserRole, LaboratoryStatus


@pytest.fixture
def schedule_service():
    return ScheduleService()


class TestScheduleServiceCreate:
    def test_create_success(self, db, wb_super_admin, wb_laboratory, wb_semester, wb_teacher, wb_mock_request):
        service = ScheduleService()
        schedule = service.create_schedule(
            requester=wb_super_admin,
            data={
                'course_name': '白盒创建课程',
                'weekday': 2,
                'time_slot': '3-4',
                'weeks': '1-16',
                'laboratory_id': wb_laboratory.id,
                'semester_id': wb_semester.id,
                'teacher_id': wb_teacher.id,
            },
            request=wb_mock_request,
        )
        assert schedule.course_name == '白盒创建课程'
        assert schedule.weekday == 2

    def test_create_no_laboratory(self, db, wb_super_admin):
        service = ScheduleService()
        with pytest.raises(ValidationError, match='实训室为必填项'):
            service.create_schedule(
                requester=wb_super_admin,
                data={'course_name': '测试', 'weekday': 1},
            )

    def test_create_no_course_name(self, db, wb_super_admin, wb_laboratory):
        service = ScheduleService()
        with pytest.raises(ValidationError, match='课程名称为必填项'):
            service.create_schedule(
                requester=wb_super_admin,
                data={
                    'laboratory_id': wb_laboratory.id,
                    'weekday': 1,
                    'time_slot': '1-2',
                    'weeks': '1-16',
                },
            )

    def test_create_invalid_weekday(self, db, wb_super_admin, wb_laboratory):
        service = ScheduleService()
        with pytest.raises(ValidationError, match='星期'):
            service.create_schedule(
                requester=wb_super_admin,
                data={
                    'course_name': '测试',
                    'laboratory_id': wb_laboratory.id,
                    'weekday': 8,
                    'time_slot': '1-2',
                    'weeks': '1-16',
                },
            )

    def test_create_weekday_zero(self, db, wb_super_admin, wb_laboratory):
        service = ScheduleService()
        with pytest.raises(ValidationError, match='星期'):
            service.create_schedule(
                requester=wb_super_admin,
                data={
                    'course_name': '测试',
                    'laboratory_id': wb_laboratory.id,
                    'weekday': 0,
                    'time_slot': '1-2',
                    'weeks': '1-16',
                },
            )

    def test_create_conflict_detected(self, db, wb_super_admin, wb_laboratory, wb_semester, wb_teacher, wb_schedule):
        service = ScheduleService()
        with pytest.raises(ScheduleConflictError):
            service.create_schedule(
                requester=wb_super_admin,
                data={
                    'course_name': '冲突课程',
                    'weekday': wb_schedule.weekday,
                    'time_slot': wb_schedule.time_slot,
                    'weeks': wb_schedule.weeks,
                    'laboratory_id': wb_laboratory.id,
                },
            )

    def test_create_unavailable_laboratory(self, db, wb_super_admin, wb_laboratory):
        wb_laboratory.status = LaboratoryStatus.MAINTENANCE
        wb_laboratory.is_available = False
        wb_laboratory.save()
        service = ScheduleService()
        with pytest.raises(ValidationError, match='不可使用'):
            service.create_schedule(
                requester=wb_super_admin,
                data={
                    'course_name': '测试',
                    'laboratory_id': wb_laboratory.id,
                    'weekday': 1,
                    'time_slot': '1-2',
                    'weeks': '1-16',
                },
            )

    def test_create_no_permission(self, db, wb_teacher, wb_laboratory):
        service = ScheduleService()
        with pytest.raises(PermissionDenied):
            service.create_schedule(
                requester=wb_teacher,
                data={
                    'course_name': '测试',
                    'laboratory_id': wb_laboratory.id,
                    'weekday': 1,
                    'time_slot': '1-2',
                    'weeks': '1-16',
                },
            )


class TestScheduleServiceUpdate:
    def test_update_course_name(self, db, wb_super_admin, wb_schedule, wb_mock_request):
        service = ScheduleService()
        schedule = service.update_schedule(
            requester=wb_super_admin,
            schedule_id=wb_schedule.id,
            data={'course_name': '更新后课程'},
            request=wb_mock_request,
        )
        assert schedule.course_name == '更新后课程'

    def test_update_empty_course_name(self, db, wb_super_admin, wb_schedule):
        service = ScheduleService()
        with pytest.raises(ValidationError, match='课程名称不能为空'):
            service.update_schedule(
                requester=wb_super_admin,
                schedule_id=wb_schedule.id,
                data={'course_name': ''},
            )

    def test_update_conflict_on_time_change(self, db, wb_super_admin, wb_laboratory, wb_semester, wb_teacher, wb_schedule):
        from apps.schedules.models import Schedule
        Schedule.objects.create(
            course_name='另一课程',
            weekday=1,
            time_slot='3-4',
            weeks='1-16',
            laboratory=wb_laboratory,
            semester=wb_semester,
            teacher=wb_teacher,
            is_active=True,
        )
        service = ScheduleService()
        with pytest.raises(ScheduleConflictError):
            service.update_schedule(
                requester=wb_super_admin,
                schedule_id=wb_schedule.id,
                data={'time_slot': '3-4'},
            )

    def test_update_no_conflict_with_self(self, db, wb_super_admin, wb_schedule, wb_mock_request):
        service = ScheduleService()
        schedule = service.update_schedule(
            requester=wb_super_admin,
            schedule_id=wb_schedule.id,
            data={'course_name': '自身更新不冲突'},
            request=wb_mock_request,
        )
        assert schedule.course_name == '自身更新不冲突'

    def test_update_nonexistent(self, db, wb_super_admin):
        service = ScheduleService()
        with pytest.raises(NotFoundError):
            service.update_schedule(
                requester=wb_super_admin,
                schedule_id=99999,
                data={'course_name': 'test'},
            )


class TestScheduleServiceDelete:
    def test_delete_unarchived_hard_delete(self, db, wb_super_admin, wb_schedule, wb_mock_request):
        service = ScheduleService()
        schedule_id = wb_schedule.id
        result = service.delete_schedule(
            requester=wb_super_admin,
            schedule_id=schedule_id,
            request=wb_mock_request,
        )
        assert result is True
        assert not Schedule.objects.filter(id=schedule_id).exists()

    def test_delete_archived_soft_delete(self, db, wb_super_admin, wb_schedule, wb_mock_request):
        wb_schedule.is_archived = True
        wb_schedule.save()
        service = ScheduleService()
        result = service.delete_schedule(
            requester=wb_super_admin,
            schedule_id=wb_schedule.id,
            request=wb_mock_request,
        )
        assert result is True
        wb_schedule.refresh_from_db()
        assert wb_schedule.is_deleted is True

    def test_delete_nonexistent(self, db, wb_super_admin):
        service = ScheduleService()
        with pytest.raises(NotFoundError):
            service.delete_schedule(
                requester=wb_super_admin,
                schedule_id=99999,
            )


class TestScheduleServiceCheckConflict:
    def test_check_conflict_no_conflict(self, db, wb_laboratory):
        service = ScheduleService()
        result = service.check_conflict(
            laboratory_id=wb_laboratory.id,
            weekday=1,
            time_slot='1-2',
            weeks='1-16',
        )
        assert result['has_conflict'] is False

    def test_check_conflict_with_conflict(self, db, wb_schedule):
        service = ScheduleService()
        result = service.check_conflict(
            laboratory_id=wb_schedule.laboratory_id,
            weekday=wb_schedule.weekday,
            time_slot=wb_schedule.time_slot,
            weeks=wb_schedule.weeks,
        )
        assert result['has_conflict'] is True
