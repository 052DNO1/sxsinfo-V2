import pytest
from apps.schedules.services.schedule_service import ScheduleService
from apps.schedules.services.conflict_checker import ConflictChecker
from apps.schedules.models import Schedule
from apps.core.exceptions import ScheduleConflictError


class TestScheduleConflictIntegration:
    def test_create_with_conflict_fails(self, db, wb_super_admin, wb_laboratory, wb_semester, wb_teacher, wb_schedule, wb_mock_request):
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

    def test_create_no_conflict_succeeds(self, db, wb_super_admin, wb_laboratory, wb_semester, wb_teacher, wb_schedule, wb_mock_request):
        service = ScheduleService()
        schedule = service.create_schedule(
            requester=wb_super_admin,
            data={
                'course_name': '不冲突课程',
                'weekday': wb_schedule.weekday,
                'time_slot': '5-6',
                'weeks': wb_schedule.weeks,
                'laboratory_id': wb_laboratory.id,
            },
            request=wb_mock_request,
        )
        assert schedule.course_name == '不冲突课程'

    def test_update_time_rechecks_conflict(self, db, wb_super_admin, wb_laboratory, wb_semester, wb_teacher, wb_schedule, wb_mock_request):
        Schedule.objects.create(
            course_name='占位课程', weekday=1, time_slot='3-4', weeks='1-16',
            laboratory=wb_laboratory, semester=wb_semester, teacher=wb_teacher, is_active=True,
        )
        service = ScheduleService()
        with pytest.raises(ScheduleConflictError):
            service.update_schedule(
                requester=wb_super_admin,
                schedule_id=wb_schedule.id,
                data={'time_slot': '3-4'},
            )

    def test_update_self_no_conflict(self, db, wb_super_admin, wb_schedule, wb_mock_request):
        service = ScheduleService()
        schedule = service.update_schedule(
            requester=wb_super_admin,
            schedule_id=wb_schedule.id,
            data={'course_name': '自身更新'},
            request=wb_mock_request,
        )
        assert schedule.course_name == '自身更新'

    def test_delete_and_recreate(self, db, wb_super_admin, wb_laboratory, wb_semester, wb_teacher, wb_schedule, wb_mock_request):
        service = ScheduleService()
        service.delete_schedule(wb_super_admin, wb_schedule.id, request=wb_mock_request)
        new_schedule = service.create_schedule(
            requester=wb_super_admin,
            data={
                'course_name': '重建课程',
                'weekday': 1,
                'time_slot': '1-2',
                'weeks': '1-16',
                'laboratory_id': wb_laboratory.id,
            },
            request=wb_mock_request,
        )
        assert new_schedule.course_name == '重建课程'


class TestScheduleFullWorkflow:
    def test_create_read_update_delete(self, db, wb_super_admin, wb_laboratory, wb_semester, wb_teacher, wb_mock_request):
        service = ScheduleService()
        schedule = service.create_schedule(
            requester=wb_super_admin,
            data={
                'course_name': '工作流课程',
                'weekday': 2,
                'time_slot': '3-4',
                'weeks': '1-18',
                'laboratory_id': wb_laboratory.id,
                'teacher_id': wb_teacher.id,
            },
            request=wb_mock_request,
        )
        assert schedule.course_name == '工作流课程'

        schedule = service.update_schedule(
            requester=wb_super_admin,
            schedule_id=schedule.id,
            data={'course_name': '更新后课程'},
            request=wb_mock_request,
        )
        assert schedule.course_name == '更新后课程'

        result = service.delete_schedule(
            requester=wb_super_admin,
            schedule_id=schedule.id,
            request=wb_mock_request,
        )
        assert result is True
