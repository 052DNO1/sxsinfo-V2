import pytest
from apps.records.serializers.usage_record import (
    UsageRecordSerializer, UsageRecordCreateSerializer,
    UsageRecordUpdateSerializer, BatchDeleteSerializer
)


class TestUsageRecordCreateSerializer:
    def test_valid_data(self, db, wb_laboratory):
        data = {
            'usage_date': '2025-10-20',
            'time_slot': '1-2',
            'class_hours': 2,
            'laboratory_id': wb_laboratory.id,
            'content': '课程内容',
            'device_status': 'NORMAL',
            'laboratory_status': 'NORMAL',
        }
        serializer = UsageRecordCreateSerializer(data=data)
        assert serializer.is_valid(), serializer.errors

    def test_missing_laboratory_id(self, db):
        data = {
            'usage_date': '2025-10-20',
            'time_slot': '1-2',
            'class_hours': 2,
        }
        serializer = UsageRecordCreateSerializer(data=data)
        assert not serializer.is_valid()
        assert 'laboratory_id' in serializer.errors

    def test_negative_student_count(self, db, wb_laboratory):
        data = {
            'usage_date': '2025-10-20',
            'time_slot': '1-2',
            'class_hours': 2,
            'laboratory_id': wb_laboratory.id,
            'student_count': -1,
        }
        serializer = UsageRecordCreateSerializer(data=data)
        assert not serializer.is_valid()

    def test_zero_student_count(self, db, wb_laboratory):
        data = {
            'usage_date': '2025-10-20',
            'time_slot': '1-2',
            'class_hours': 2,
            'laboratory_id': wb_laboratory.id,
            'student_count': 0,
        }
        serializer = UsageRecordCreateSerializer(data=data)
        assert serializer.is_valid()

    def test_optional_teacher_id(self, db, wb_laboratory):
        data = {
            'usage_date': '2025-10-20',
            'time_slot': '1-2',
            'class_hours': 2,
            'laboratory_id': wb_laboratory.id,
        }
        serializer = UsageRecordCreateSerializer(data=data)
        assert serializer.is_valid()


class TestUsageRecordUpdateSerializer:
    def test_update_content(self, db, wb_usage_record):
        data = {'content': '更新内容'}
        serializer = UsageRecordUpdateSerializer(instance=wb_usage_record, data=data, partial=True)
        assert serializer.is_valid(), serializer.errors

    def test_update_student_count(self, db, wb_usage_record):
        data = {'student_count': 50}
        serializer = UsageRecordUpdateSerializer(instance=wb_usage_record, data=data, partial=True)
        assert serializer.is_valid(), serializer.errors

    def test_negative_student_count_fails(self, db, wb_usage_record):
        data = {'student_count': -1}
        serializer = UsageRecordUpdateSerializer(instance=wb_usage_record, data=data, partial=True)
        assert not serializer.is_valid()


class TestUsageRecordSerializer:
    def test_includes_laboratory_info(self, db, wb_usage_record):
        serializer = UsageRecordSerializer(wb_usage_record)
        assert 'laboratory_name' in serializer.data
        assert 'laboratory_code' in serializer.data

    def test_includes_teacher_name(self, db, wb_usage_record):
        serializer = UsageRecordSerializer(wb_usage_record)
        assert 'teacher_name' in serializer.data

    def test_includes_semester_name(self, db, wb_usage_record):
        serializer = UsageRecordSerializer(wb_usage_record)
        assert 'semester_name' in serializer.data

    def test_laboratory_name_from_relation(self, db, wb_usage_record):
        serializer = UsageRecordSerializer(wb_usage_record)
        assert serializer.data['laboratory_name'] == wb_usage_record.laboratory.name

    def test_laboratory_name_from_stored(self, db, wb_usage_record):
        lab_name = wb_usage_record.laboratory.name
        wb_usage_record.laboratory = None
        wb_usage_record.save()
        serializer = UsageRecordSerializer(wb_usage_record)
        assert serializer.data['laboratory_name'] == lab_name


class TestBatchDeleteSerializer:
    def test_valid_ids(self):
        data = {'ids': [1, 2, 3]}
        serializer = BatchDeleteSerializer(data=data)
        assert serializer.is_valid()

    def test_empty_ids(self):
        data = {'ids': []}
        serializer = BatchDeleteSerializer(data=data)
        assert not serializer.is_valid()

    def test_missing_ids(self):
        data = {}
        serializer = BatchDeleteSerializer(data=data)
        assert not serializer.is_valid()

    def test_zero_id_fails(self):
        data = {'ids': [0]}
        serializer = BatchDeleteSerializer(data=data)
        assert not serializer.is_valid()

    def test_negative_id_fails(self):
        data = {'ids': [-1]}
        serializer = BatchDeleteSerializer(data=data)
        assert not serializer.is_valid()
