import pytest
from apps.schedules.serializers.schedule import (
    ScheduleSerializer, ScheduleCreateSerializer, ScheduleUpdateSerializer,
    ScheduleConflictCheckSerializer, SemesterSerializer, SemesterCreateSerializer
)


class TestScheduleCreateSerializer:
    def test_valid_data(self, db, wb_laboratory):
        data = {
            'course_name': '测试课程',
            'weekday': 1,
            'time_slot': '1-2',
            'weeks': '1-16',
            'laboratory': wb_laboratory.id,
        }
        serializer = ScheduleCreateSerializer(data=data)
        assert serializer.is_valid(), serializer.errors

    def test_empty_course_name(self, db):
        data = {
            'course_name': '',
            'weekday': 1,
            'time_slot': '1-2',
            'weeks': '1-16',
            'laboratory': 1,
        }
        serializer = ScheduleCreateSerializer(data=data)
        assert not serializer.is_valid()
        assert 'course_name' in serializer.errors

    def test_whitespace_course_name(self, db):
        data = {
            'course_name': '   ',
            'weekday': 1,
            'time_slot': '1-2',
            'weeks': '1-16',
            'laboratory': 1,
        }
        serializer = ScheduleCreateSerializer(data=data)
        assert not serializer.is_valid()

    def test_invalid_weekday_zero(self, db):
        data = {
            'course_name': '测试',
            'weekday': 0,
            'time_slot': '1-2',
            'weeks': '1-16',
            'laboratory': 1,
        }
        serializer = ScheduleCreateSerializer(data=data)
        assert not serializer.is_valid()

    def test_invalid_weekday_eight(self, db):
        data = {
            'course_name': '测试',
            'weekday': 8,
            'time_slot': '1-2',
            'weeks': '1-16',
            'laboratory': 1,
        }
        serializer = ScheduleCreateSerializer(data=data)
        assert not serializer.is_valid()

    def test_missing_laboratory(self, db):
        data = {
            'course_name': '测试',
            'weekday': 1,
            'time_slot': '1-2',
            'weeks': '1-16',
        }
        serializer = ScheduleCreateSerializer(data=data)
        assert not serializer.is_valid()

    def test_laboratory_id_as_alias(self, db, wb_laboratory):
        data = {
            'course_name': '测试',
            'weekday': 1,
            'time_slot': '1-2',
            'weeks': '1-16',
            'laboratory_id': wb_laboratory.id,
            'laboratory': wb_laboratory.id,
        }
        serializer = ScheduleCreateSerializer(data=data)
        assert serializer.is_valid(), serializer.errors

    def test_default_student_count(self, db, wb_laboratory):
        data = {
            'course_name': '测试',
            'weekday': 1,
            'time_slot': '1-2',
            'weeks': '1-16',
            'laboratory': wb_laboratory.id,
        }
        serializer = ScheduleCreateSerializer(data=data)
        assert serializer.is_valid()
        assert serializer.validated_data.get('student_count', 0) == 0


class TestScheduleUpdateSerializer:
    def test_update_course_name(self, db, wb_schedule):
        data = {'course_name': '更新课程'}
        serializer = ScheduleUpdateSerializer(instance=wb_schedule, data=data, partial=True)
        assert serializer.is_valid(), serializer.errors

    def test_empty_course_name_fails(self, db, wb_schedule):
        data = {'course_name': ''}
        serializer = ScheduleUpdateSerializer(instance=wb_schedule, data=data, partial=True)
        assert not serializer.is_valid()

    def test_update_weekday(self, db, wb_schedule):
        data = {'weekday': 3}
        serializer = ScheduleUpdateSerializer(instance=wb_schedule, data=data, partial=True)
        assert serializer.is_valid(), serializer.errors

    def test_invalid_weekday(self, db, wb_schedule):
        data = {'weekday': 9}
        serializer = ScheduleUpdateSerializer(instance=wb_schedule, data=data, partial=True)
        assert not serializer.is_valid()

    def test_teacher_id_null_is_valid(self, db, wb_schedule):
        data = {'teacher_id': None}
        serializer = ScheduleUpdateSerializer(instance=wb_schedule, data=data, partial=True)
        assert serializer.is_valid()
        assert serializer.validated_data.get('teacher_id') is None


class TestScheduleConflictCheckSerializer:
    def test_valid_data(self, db):
        data = {
            'laboratory_id': 1,
            'weekday': 1,
            'time_slot': '1-2',
            'weeks': '1-16',
        }
        serializer = ScheduleConflictCheckSerializer(data=data)
        assert serializer.is_valid()

    def test_missing_required_fields(self, db):
        data = {}
        serializer = ScheduleConflictCheckSerializer(data=data)
        assert not serializer.is_valid()
        assert 'laboratory_id' in serializer.errors
        assert 'weekday' in serializer.errors
        assert 'time_slot' in serializer.errors
        assert 'weeks' in serializer.errors

    def test_weekday_out_of_range(self, db):
        data = {'laboratory_id': 1, 'weekday': 8, 'time_slot': '1-2', 'weeks': '1-16'}
        serializer = ScheduleConflictCheckSerializer(data=data)
        assert not serializer.is_valid()

    def test_optional_exclude_id(self, db):
        data = {
            'laboratory_id': 1,
            'weekday': 1,
            'time_slot': '1-2',
            'weeks': '1-16',
            'exclude_id': 5,
        }
        serializer = ScheduleConflictCheckSerializer(data=data)
        assert serializer.is_valid()


class TestScheduleSerializer:
    def test_weekday_display(self, db, wb_schedule):
        serializer = ScheduleSerializer(wb_schedule)
        weekday_map = {1: '周一', 2: '周二', 3: '周三', 4: '周四', 5: '周五', 6: '周六', 7: '周日'}
        assert serializer.data['weekday_display'] == weekday_map.get(wb_schedule.weekday)

    def test_teacher_name_display(self, db, wb_schedule):
        serializer = ScheduleSerializer(wb_schedule)
        assert serializer.data['teacher_name_display'] == wb_schedule.teacher_name

    def test_includes_laboratory_info(self, db, wb_schedule):
        serializer = ScheduleSerializer(wb_schedule)
        assert 'laboratory_name' in serializer.data


class TestSemesterSerializer:
    def test_includes_schedule_count(self, db, wb_semester):
        serializer = SemesterSerializer(wb_semester)
        assert 'schedule_count' in serializer.data


class TestSemesterCreateSerializer:
    def test_valid_data(self, db):
        data = {
            'name': '测试学期',
            'start_date': '2025-09-01',
            'end_date': '2026-01-15',
        }
        serializer = SemesterCreateSerializer(data=data)
        assert serializer.is_valid(), serializer.errors

    def test_empty_name(self, db):
        data = {'name': ''}
        serializer = SemesterCreateSerializer(data=data)
        assert not serializer.is_valid()

    def test_whitespace_name(self, db):
        data = {'name': '   '}
        serializer = SemesterCreateSerializer(data=data)
        assert not serializer.is_valid()

    def test_code_optional(self, db):
        data = {
            'name': '无编码学期',
            'start_date': '2025-09-01',
            'end_date': '2026-01-15',
        }
        serializer = SemesterCreateSerializer(data=data)
        assert serializer.is_valid()

    def test_is_current_default_false(self, db):
        data = {
            'name': '默认非当前学期',
            'start_date': '2025-09-01',
            'end_date': '2026-01-15',
        }
        serializer = SemesterCreateSerializer(data=data)
        assert serializer.is_valid()
        assert serializer.validated_data.get('is_current') is False

    def test_auto_generate_code_on_create(self, db):
        data = {
            'name': '自动编码学期',
            'start_date': '2025-09-01',
            'end_date': '2026-01-15',
        }
        serializer = SemesterCreateSerializer(data=data)
        assert serializer.is_valid()
        semester = serializer.save()
        assert semester.code != ''
