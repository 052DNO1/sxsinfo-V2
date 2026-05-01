import pytest
from apps.schedules.services.conflict_checker import ConflictChecker
from apps.schedules.models import Schedule
from apps.core.constants import UserRole


class TestConflictCheckerLaboratory:
    def test_no_conflict_empty_schedule(self, db, wb_laboratory, wb_semester, wb_teacher):
        has_conflict, conflicts = ConflictChecker.check_laboratory_conflict(
            laboratory_id=wb_laboratory.id,
            weekday=1,
            time_slot='1-2',
            weeks='1-16',
        )
        assert has_conflict is False
        assert conflicts == []

    def test_full_overlap_conflict(self, db, wb_laboratory, wb_semester, wb_teacher):
        Schedule.objects.create(
            course_name='已有课程',
            weekday=1,
            time_slot='1-2',
            weeks='1-16',
            laboratory=wb_laboratory,
            semester=wb_semester,
            teacher=wb_teacher,
            is_active=True,
        )
        has_conflict, conflicts = ConflictChecker.check_laboratory_conflict(
            laboratory_id=wb_laboratory.id,
            weekday=1,
            time_slot='1-2',
            weeks='1-16',
        )
        assert has_conflict is True
        assert len(conflicts) == 1
        assert conflicts[0]['course_name'] == '已有课程'

    def test_time_overlap_week_no_overlap(self, db, wb_laboratory, wb_semester, wb_teacher):
        Schedule.objects.create(
            course_name='已有课程',
            weekday=1,
            time_slot='1-2',
            weeks='1-8',
            laboratory=wb_laboratory,
            semester=wb_semester,
            teacher=wb_teacher,
            is_active=True,
        )
        has_conflict, conflicts = ConflictChecker.check_laboratory_conflict(
            laboratory_id=wb_laboratory.id,
            weekday=1,
            time_slot='1-2',
            weeks='9-16',
        )
        assert has_conflict is False

    def test_week_overlap_time_no_overlap(self, db, wb_laboratory, wb_semester, wb_teacher):
        Schedule.objects.create(
            course_name='已有课程',
            weekday=1,
            time_slot='1-2',
            weeks='1-16',
            laboratory=wb_laboratory,
            semester=wb_semester,
            teacher=wb_teacher,
            is_active=True,
        )
        has_conflict, conflicts = ConflictChecker.check_laboratory_conflict(
            laboratory_id=wb_laboratory.id,
            weekday=1,
            time_slot='3-4',
            weeks='1-16',
        )
        assert has_conflict is False

    def test_partial_time_overlap(self, db, wb_laboratory, wb_semester, wb_teacher):
        Schedule.objects.create(
            course_name='已有课程',
            weekday=1,
            time_slot='1-4',
            weeks='1-16',
            laboratory=wb_laboratory,
            semester=wb_semester,
            teacher=wb_teacher,
            is_active=True,
        )
        has_conflict, conflicts = ConflictChecker.check_laboratory_conflict(
            laboratory_id=wb_laboratory.id,
            weekday=1,
            time_slot='3-6',
            weeks='1-16',
        )
        assert has_conflict is True
        assert 3 in conflicts[0]['conflict_time']
        assert 4 in conflicts[0]['conflict_time']

    def test_partial_week_overlap(self, db, wb_laboratory, wb_semester, wb_teacher):
        Schedule.objects.create(
            course_name='已有课程',
            weekday=1,
            time_slot='1-2',
            weeks='1-10',
            laboratory=wb_laboratory,
            semester=wb_semester,
            teacher=wb_teacher,
            is_active=True,
        )
        has_conflict, conflicts = ConflictChecker.check_laboratory_conflict(
            laboratory_id=wb_laboratory.id,
            weekday=1,
            time_slot='1-2',
            weeks='8-16',
        )
        assert has_conflict is True
        assert 8 in conflicts[0]['conflict_weeks']
        assert 9 in conflicts[0]['conflict_weeks']
        assert 10 in conflicts[0]['conflict_weeks']

    def test_different_weekday_no_conflict(self, db, wb_laboratory, wb_semester, wb_teacher):
        Schedule.objects.create(
            course_name='已有课程',
            weekday=1,
            time_slot='1-2',
            weeks='1-16',
            laboratory=wb_laboratory,
            semester=wb_semester,
            teacher=wb_teacher,
            is_active=True,
        )
        has_conflict, conflicts = ConflictChecker.check_laboratory_conflict(
            laboratory_id=wb_laboratory.id,
            weekday=2,
            time_slot='1-2',
            weeks='1-16',
        )
        assert has_conflict is False

    def test_different_laboratory_no_conflict(self, db, wb_laboratory, wb_laboratory2, wb_semester, wb_teacher):
        Schedule.objects.create(
            course_name='已有课程',
            weekday=1,
            time_slot='1-2',
            weeks='1-16',
            laboratory=wb_laboratory,
            semester=wb_semester,
            teacher=wb_teacher,
            is_active=True,
        )
        has_conflict, conflicts = ConflictChecker.check_laboratory_conflict(
            laboratory_id=wb_laboratory2.id,
            weekday=1,
            time_slot='1-2',
            weeks='1-16',
        )
        assert has_conflict is False

    def test_exclude_self(self, db, wb_schedule):
        has_conflict, conflicts = ConflictChecker.check_laboratory_conflict(
            laboratory_id=wb_schedule.laboratory_id,
            weekday=wb_schedule.weekday,
            time_slot=wb_schedule.time_slot,
            weeks=wb_schedule.weeks,
            exclude_schedule_id=wb_schedule.id,
        )
        assert has_conflict is False

    def test_not_exclude_self(self, db, wb_schedule):
        has_conflict, conflicts = ConflictChecker.check_laboratory_conflict(
            laboratory_id=wb_schedule.laboratory_id,
            weekday=wb_schedule.weekday,
            time_slot=wb_schedule.time_slot,
            weeks=wb_schedule.weeks,
        )
        assert has_conflict is True

    def test_multiple_conflicts(self, db, wb_laboratory, wb_semester, wb_teacher):
        Schedule.objects.create(
            course_name='课程A',
            weekday=1,
            time_slot='1-4',
            weeks='1-16',
            laboratory=wb_laboratory,
            semester=wb_semester,
            teacher=wb_teacher,
            is_active=True,
        )
        Schedule.objects.create(
            course_name='课程B',
            weekday=1,
            time_slot='3-6',
            weeks='1-8',
            laboratory=wb_laboratory,
            semester=wb_semester,
            teacher=wb_teacher,
            is_active=True,
        )
        has_conflict, conflicts = ConflictChecker.check_laboratory_conflict(
            laboratory_id=wb_laboratory.id,
            weekday=1,
            time_slot='3-4',
            weeks='1-8',
        )
        assert has_conflict is True
        assert len(conflicts) == 2

    def test_deleted_schedule_not_checked(self, db, wb_laboratory, wb_semester, wb_teacher):
        Schedule.objects.create(
            course_name='已删除课程',
            weekday=1,
            time_slot='1-2',
            weeks='1-16',
            laboratory=wb_laboratory,
            semester=wb_semester,
            teacher=wb_teacher,
            is_active=True,
            is_deleted=True,
        )
        has_conflict, conflicts = ConflictChecker.check_laboratory_conflict(
            laboratory_id=wb_laboratory.id,
            weekday=1,
            time_slot='1-2',
            weeks='1-16',
        )
        assert has_conflict is False

    def test_archived_schedule_not_checked(self, db, wb_laboratory, wb_semester, wb_teacher):
        Schedule.objects.create(
            course_name='已归档课程',
            weekday=1,
            time_slot='1-2',
            weeks='1-16',
            laboratory=wb_laboratory,
            semester=wb_semester,
            teacher=wb_teacher,
            is_active=True,
            is_archived=True,
        )
        has_conflict, conflicts = ConflictChecker.check_laboratory_conflict(
            laboratory_id=wb_laboratory.id,
            weekday=1,
            time_slot='1-2',
            weeks='1-16',
        )
        assert has_conflict is False

    def test_conflict_contains_detail_info(self, db, wb_laboratory, wb_semester, wb_teacher):
        Schedule.objects.create(
            course_name='已有课程',
            weekday=1,
            time_slot='1-4',
            weeks='1-10',
            laboratory=wb_laboratory,
            semester=wb_semester,
            teacher=wb_teacher,
            teacher_name='测试教师',
            is_active=True,
        )
        has_conflict, conflicts = ConflictChecker.check_laboratory_conflict(
            laboratory_id=wb_laboratory.id,
            weekday=1,
            time_slot='3-6',
            weeks='8-16',
        )
        assert has_conflict is True
        conflict = conflicts[0]
        assert 'schedule_id' in conflict
        assert 'course_name' in conflict
        assert 'conflict_time' in conflict
        assert 'conflict_weeks' in conflict
        assert conflict['conflict_time'] == [3, 4]
        assert conflict['conflict_weeks'] == [8, 9, 10]

    def test_single_time_slot_conflict(self, db, wb_laboratory, wb_semester, wb_teacher):
        Schedule.objects.create(
            course_name='已有课程',
            weekday=1,
            time_slot='1,3,5',
            weeks='1-16',
            laboratory=wb_laboratory,
            semester=wb_semester,
            teacher=wb_teacher,
            is_active=True,
        )
        has_conflict, conflicts = ConflictChecker.check_laboratory_conflict(
            laboratory_id=wb_laboratory.id,
            weekday=1,
            time_slot='3',
            weeks='1-16',
        )
        assert has_conflict is True

    def test_comma_separated_weeks_conflict(self, db, wb_laboratory, wb_semester, wb_teacher):
        Schedule.objects.create(
            course_name='已有课程',
            weekday=1,
            time_slot='1-2',
            weeks='1,3,5,7,9,11,13,15',
            laboratory=wb_laboratory,
            semester=wb_semester,
            teacher=wb_teacher,
            is_active=True,
        )
        has_conflict, conflicts = ConflictChecker.check_laboratory_conflict(
            laboratory_id=wb_laboratory.id,
            weekday=1,
            time_slot='1-2',
            weeks='2,4,6,8,10,12,14,16',
        )
        assert has_conflict is False


class TestConflictCheckerTeacher:
    def test_teacher_no_conflict(self, db, wb_laboratory, wb_semester, wb_teacher):
        has_conflict, conflicts = ConflictChecker.check_teacher_conflict(
            teacher_id=wb_teacher.id,
            weekday=1,
            time_slot='1-2',
            weeks='1-16',
        )
        assert has_conflict is False

    def test_teacher_conflict(self, db, wb_laboratory, wb_semester, wb_teacher):
        Schedule.objects.create(
            course_name='已有课程',
            weekday=1,
            time_slot='1-2',
            weeks='1-16',
            laboratory=wb_laboratory,
            semester=wb_semester,
            teacher=wb_teacher,
            is_active=True,
        )
        has_conflict, conflicts = ConflictChecker.check_teacher_conflict(
            teacher_id=wb_teacher.id,
            weekday=1,
            time_slot='1-2',
            weeks='1-16',
        )
        assert has_conflict is True

    def test_teacher_exclude_self(self, db, wb_schedule):
        has_conflict, conflicts = ConflictChecker.check_teacher_conflict(
            teacher_id=wb_schedule.teacher_id,
            weekday=wb_schedule.weekday,
            time_slot=wb_schedule.time_slot,
            weeks=wb_schedule.weeks,
            exclude_schedule_id=wb_schedule.id,
        )
        assert has_conflict is False

    def test_different_teacher_no_conflict(self, db, wb_laboratory, wb_semester, wb_teacher, wb_lab_admin):
        Schedule.objects.create(
            course_name='已有课程',
            weekday=1,
            time_slot='1-2',
            weeks='1-16',
            laboratory=wb_laboratory,
            semester=wb_semester,
            teacher=wb_teacher,
            is_active=True,
        )
        has_conflict, conflicts = ConflictChecker.check_teacher_conflict(
            teacher_id=wb_lab_admin.id,
            weekday=1,
            time_slot='1-2',
            weeks='1-16',
        )
        assert has_conflict is False
