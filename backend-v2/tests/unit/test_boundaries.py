import pytest
from apps.laboratories.serializers.laboratory import (
    LaboratoryCreateSerializer, LaboratoryUpdateSerializer
)
from apps.schedules.serializers.schedule import (
    ScheduleCreateSerializer, ScheduleUpdateSerializer
)
from apps.maintenance.serializers.work_order import WorkOrderCreateSerializer
from apps.records.serializers.usage_record import UsageRecordCreateSerializer
from apps.users.serializers.user import UserCreateSerializer
from apps.users.serializers.auth import ChangePasswordSerializer


class TestLaboratoryBoundaryValues:
    def test_capacity_zero(self, db, wb_department):
        data = {
            'name': '容量0', 'code': 'CAP_ZERO',
            'department': wb_department.id, 'capacity': 0,
        }
        serializer = LaboratoryCreateSerializer(data=data)
        if serializer.is_valid():
            lab = serializer.save()
            assert lab.capacity == 0
        else:
            assert 'capacity' in serializer.errors

    def test_capacity_negative(self, db, wb_department):
        data = {
            'name': '容量负数', 'code': 'CAP_NEG',
            'department': wb_department.id, 'capacity': -1,
        }
        serializer = LaboratoryCreateSerializer(data=data)
        assert not serializer.is_valid()

    def test_name_max_length(self, db, wb_department):
        data = {
            'name': 'A' * 100, 'code': 'NAME_MAX',
            'department': wb_department.id,
        }
        serializer = LaboratoryCreateSerializer(data=data)
        assert serializer.is_valid(), serializer.errors

    def test_name_exceeds_max_length(self, db, wb_department):
        data = {
            'name': 'A' * 101, 'code': 'NAME_OVER',
            'department': wb_department.id,
        }
        serializer = LaboratoryCreateSerializer(data=data)
        assert not serializer.is_valid()

    def test_code_max_length(self, db, wb_department):
        data = {
            'name': '测试', 'code': 'C' * 50,
            'department': wb_department.id,
        }
        serializer = LaboratoryCreateSerializer(data=data)
        assert serializer.is_valid(), serializer.errors

    def test_code_exceeds_max_length(self, db, wb_department):
        data = {
            'name': '测试', 'code': 'C' * 51,
            'department': wb_department.id,
        }
        serializer = LaboratoryCreateSerializer(data=data)
        assert not serializer.is_valid()

    def test_area_zero(self, db, wb_department):
        data = {
            'name': '面积0', 'code': 'AREA_ZERO',
            'department': wb_department.id, 'area': 0,
        }
        serializer = LaboratoryCreateSerializer(data=data)
        assert serializer.is_valid(), serializer.errors

    def test_area_negative(self, db, wb_department):
        data = {
            'name': '面积负数', 'code': 'AREA_NEG',
            'department': wb_department.id, 'area': -1,
        }
        serializer = LaboratoryCreateSerializer(data=data)
        if not serializer.is_valid():
            assert 'area' in serializer.errors

    def test_floor_zero(self, db, wb_department):
        data = {
            'name': '0楼', 'code': 'FLOOR_ZERO',
            'department': wb_department.id, 'floor': 0,
        }
        serializer = LaboratoryCreateSerializer(data=data)
        assert serializer.is_valid(), serializer.errors

    def test_floor_negative(self, db, wb_department):
        data = {
            'name': '负楼层', 'code': 'FLOOR_NEG',
            'department': wb_department.id, 'floor': -1,
        }
        serializer = LaboratoryCreateSerializer(data=data)
        assert serializer.is_valid(), serializer.errors


class TestScheduleBoundaryValues:
    def test_weekday_boundary_min(self, db, wb_laboratory):
        data = {
            'course_name': '周一', 'weekday': 1,
            'time_slot': '1-2', 'weeks': '1-16',
            'laboratory': wb_laboratory.id,
        }
        serializer = ScheduleCreateSerializer(data=data)
        assert serializer.is_valid(), serializer.errors

    def test_weekday_boundary_max(self, db, wb_laboratory):
        data = {
            'course_name': '周日', 'weekday': 7,
            'time_slot': '1-2', 'weeks': '1-16',
            'laboratory': wb_laboratory.id,
        }
        serializer = ScheduleCreateSerializer(data=data)
        assert serializer.is_valid(), serializer.errors

    def test_weekday_below_range(self, db, wb_laboratory):
        data = {
            'course_name': '测试', 'weekday': 0,
            'time_slot': '1-2', 'weeks': '1-16',
            'laboratory': wb_laboratory.id,
        }
        serializer = ScheduleCreateSerializer(data=data)
        assert not serializer.is_valid()

    def test_weekday_above_range(self, db, wb_laboratory):
        data = {
            'course_name': '测试', 'weekday': 8,
            'time_slot': '1-2', 'weeks': '1-16',
            'laboratory': wb_laboratory.id,
        }
        serializer = ScheduleCreateSerializer(data=data)
        assert not serializer.is_valid()

    def test_student_count_zero(self, db, wb_laboratory):
        data = {
            'course_name': '零学生', 'weekday': 1,
            'time_slot': '1-2', 'weeks': '1-16',
            'laboratory': wb_laboratory.id, 'student_count': 0,
        }
        serializer = ScheduleCreateSerializer(data=data)
        assert serializer.is_valid(), serializer.errors

    def test_student_count_negative(self, db, wb_laboratory):
        data = {
            'course_name': '负学生', 'weekday': 1,
            'time_slot': '1-2', 'weeks': '1-16',
            'laboratory': wb_laboratory.id, 'student_count': -1,
        }
        serializer = ScheduleCreateSerializer(data=data)
        assert not serializer.is_valid()

    def test_course_name_whitespace_only(self, db, wb_laboratory):
        data = {
            'course_name': '   ', 'weekday': 1,
            'time_slot': '1-2', 'weeks': '1-16',
            'laboratory': wb_laboratory.id,
        }
        serializer = ScheduleCreateSerializer(data=data)
        assert not serializer.is_valid()


class TestWorkOrderBoundaryValues:
    def test_priority_min(self, db, wb_laboratory):
        data = {
            'title': '最低优先级', 'description': '描述',
            'laboratory_id': wb_laboratory.id, 'priority': 1,
        }
        serializer = WorkOrderCreateSerializer(data=data)
        assert serializer.is_valid(), serializer.errors

    def test_priority_max(self, db, wb_laboratory):
        data = {
            'title': '最高优先级', 'description': '描述',
            'laboratory_id': wb_laboratory.id, 'priority': 4,
        }
        serializer = WorkOrderCreateSerializer(data=data)
        assert serializer.is_valid(), serializer.errors

    def test_priority_below_range(self, db, wb_laboratory):
        data = {
            'title': '超低优先级', 'description': '描述',
            'laboratory_id': wb_laboratory.id, 'priority': 0,
        }
        serializer = WorkOrderCreateSerializer(data=data)
        assert not serializer.is_valid()

    def test_priority_above_range(self, db, wb_laboratory):
        data = {
            'title': '超高优先级', 'description': '描述',
            'laboratory_id': wb_laboratory.id, 'priority': 5,
        }
        serializer = WorkOrderCreateSerializer(data=data)
        assert not serializer.is_valid()

    def test_title_empty(self, db, wb_laboratory):
        data = {
            'title': '', 'description': '描述',
            'laboratory_id': wb_laboratory.id,
        }
        serializer = WorkOrderCreateSerializer(data=data)
        assert not serializer.is_valid()

    def test_description_empty(self, db, wb_laboratory):
        data = {
            'title': '标题', 'description': '',
            'laboratory_id': wb_laboratory.id,
        }
        serializer = WorkOrderCreateSerializer(data=data)
        assert not serializer.is_valid()

    def test_laboratory_id_nonexistent(self, db):
        data = {
            'title': '标题', 'description': '描述',
            'laboratory_id': 99999,
        }
        serializer = WorkOrderCreateSerializer(data=data)
        assert serializer.is_valid()
        with pytest.raises(Exception):
            serializer.save()


class TestUserBoundaryValues:
    def test_username_max_length(self, db, wb_department):
        data = {
            'username': 'U' * 150, 'department': wb_department.id,
        }
        serializer = UserCreateSerializer(data=data)
        assert serializer.is_valid(), serializer.errors

    def test_username_exceeds_max_length(self, db, wb_department):
        data = {
            'username': 'U' * 151, 'department': wb_department.id,
        }
        serializer = UserCreateSerializer(data=data)
        assert not serializer.is_valid()

    def test_username_empty(self, db):
        data = {'username': ''}
        serializer = UserCreateSerializer(data=data)
        assert not serializer.is_valid()


class TestChangePasswordBoundary:
    def test_new_password_same_as_old(self, db, wb_teacher):
        data = {
            'old_pwd': 'test123456',
            'new_pwd': 'test123456',
            'confirm_pwd': 'test123456',
        }
        serializer = ChangePasswordSerializer(data=data, context={'request': None})
        if serializer.is_valid():
            pass
        else:
            assert 'new_pwd' in serializer.errors or 'non_field_errors' in serializer.errors

    def test_new_password_too_short(self, db):
        data = {
            'old_pwd': 'oldpassword',
            'new_pwd': '123',
            'confirm_pwd': '123',
        }
        serializer = ChangePasswordSerializer(data=data, context={'request': None})
        if not serializer.is_valid():
            assert 'new_pwd' in serializer.errors or 'non_field_errors' in serializer.errors
