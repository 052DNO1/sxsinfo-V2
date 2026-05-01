import pytest
from apps.schedules.services.conflict_checker import ConflictChecker
from apps.schedules.models import Schedule


class TestConflictCheckerLabNoConflict:
    def test_empty_schedule(self, db, wb_laboratory):
        has_conflict, conflicts = ConflictChecker.check_laboratory_conflict(
            laboratory_id=wb_laboratory.id, weekday=1, time_slot='1-2', weeks='1-16'
        )
        assert has_conflict is False
        assert conflicts == []

    def test_different_weekday(self, db, wb_schedule):
        has_conflict, _ = ConflictChecker.check_laboratory_conflict(
            laboratory_id=wb_schedule.laboratory_id,
            weekday=wb_schedule.weekday + 1,
            time_slot=wb_schedule.time_slot,
            weeks=wb_schedule.weeks,
        )
        assert has_conflict is False

    def test_different_time(self, db, wb_schedule):
        has_conflict, _ = ConflictChecker.check_laboratory_conflict(
            laboratory_id=wb_schedule.laboratory_id,
            weekday=wb_schedule.weekday,
            time_slot='5-6',
            weeks=wb_schedule.weeks,
        )
        assert has_conflict is False

    def test_different_weeks(self, db, wb_schedule):
        has_conflict, _ = ConflictChecker.check_laboratory_conflict(
            laboratory_id=wb_schedule.laboratory_id,
            weekday=wb_schedule.weekday,
            time_slot=wb_schedule.time_slot,
            weeks='17-20',
        )
        assert has_conflict is False

    def test_exclude_self(self, db, wb_schedule):
        has_conflict, _ = ConflictChecker.check_laboratory_conflict(
            laboratory_id=wb_schedule.laboratory_id,
            weekday=wb_schedule.weekday,
            time_slot=wb_schedule.time_slot,
            weeks=wb_schedule.weeks,
            exclude_schedule_id=wb_schedule.id,
        )
        assert has_conflict is False


class TestConflictCheckerLabHasConflict:
    def test_full_overlap(self, db, wb_schedule):
        has_conflict, conflicts = ConflictChecker.check_laboratory_conflict(
            laboratory_id=wb_schedule.laboratory_id,
            weekday=wb_schedule.weekday,
            time_slot=wb_schedule.time_slot,
            weeks=wb_schedule.weeks,
        )
        assert has_conflict is True
        assert len(conflicts) >= 1

    def test_partial_time_overlap(self, db, wb_laboratory, wb_semester, wb_teacher):
        Schedule.objects.create(
            course_name='大课', weekday=1, time_slot='1-4', weeks='1-16',
            laboratory=wb_laboratory, semester=wb_semester, teacher=wb_teacher, is_active=True,
        )
        has_conflict, conflicts = ConflictChecker.check_laboratory_conflict(
            laboratory_id=wb_laboratory.id, weekday=1, time_slot='3-6', weeks='1-16'
        )
        assert has_conflict is True

    def test_partial_week_overlap(self, db, wb_laboratory, wb_semester, wb_teacher):
        Schedule.objects.create(
            course_name='前半学期', weekday=1, time_slot='1-2', weeks='1-10',
            laboratory=wb_laboratory, semester=wb_semester, teacher=wb_teacher, is_active=True,
        )
        has_conflict, conflicts = ConflictChecker.check_laboratory_conflict(
            laboratory_id=wb_laboratory.id, weekday=1, time_slot='1-2', weeks='8-16'
        )
        assert has_conflict is True


class TestConflictCheckerTeacher:
    def test_teacher_conflict(self, db, wb_schedule):
        has_conflict, _ = ConflictChecker.check_teacher_conflict(
            teacher_id=wb_schedule.teacher_id,
            weekday=wb_schedule.weekday,
            time_slot=wb_schedule.time_slot,
            weeks=wb_schedule.weeks,
        )
        assert has_conflict is True

    def test_teacher_no_conflict(self, db, wb_teacher):
        has_conflict, _ = ConflictChecker.check_teacher_conflict(
            teacher_id=wb_teacher.id, weekday=1, time_slot='1-2', weeks='1-16'
        )
        assert has_conflict is False

    def test_teacher_exclude_self(self, db, wb_schedule):
        has_conflict, _ = ConflictChecker.check_teacher_conflict(
            teacher_id=wb_schedule.teacher_id,
            weekday=wb_schedule.weekday,
            time_slot=wb_schedule.time_slot,
            weeks=wb_schedule.weeks,
            exclude_schedule_id=wb_schedule.id,
        )
        assert has_conflict is False
