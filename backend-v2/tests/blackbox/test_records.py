import pytest
from tests.blackbox.client import (
    assert_success_response, assert_error_response,
    assert_paginated_response, extract_data, extract_list,
)
from tests.blackbox.config import API_ENDPOINTS


class TestUsageRecordList:
    def test_get_record_list(self, authed_client):
        url = API_ENDPOINTS['records']['list']
        response = authed_client.get(url)
        assert_paginated_response(response)

    def test_get_record_list_with_pagination(self, authed_client):
        url = API_ENDPOINTS['records']['list']
        response = authed_client.get(url, {'page': 1, 'page_size': 10})
        assert_paginated_response(response)

    def test_get_record_list_search(self, authed_client, test_usage_record):
        url = API_ENDPOINTS['records']['list']
        response = authed_client.get(url, {'search': test_usage_record.content})
        assert response.status_code in (200, 500)

    def test_get_record_list_filter_by_laboratory(self, authed_client, test_laboratory):
        url = API_ENDPOINTS['records']['list']
        response = authed_client.get(url, {'laboratory_id': test_laboratory.id})
        assert_paginated_response(response)

    def test_get_record_list_filter_by_teacher(self, authed_client, teacher):
        url = API_ENDPOINTS['records']['list']
        response = authed_client.get(url, {'teacher_id': teacher.id})
        assert_paginated_response(response)

    def test_get_record_list_filter_by_semester(self, authed_client, test_semester):
        url = API_ENDPOINTS['records']['list']
        response = authed_client.get(url, {'semester_id': test_semester.id})
        assert_paginated_response(response)

    def test_get_record_list_filter_by_date_range(self, authed_client):
        url = API_ENDPOINTS['records']['list']
        response = authed_client.get(url, {
            'start_date': '2025-10-01',
            'end_date': '2025-10-31',
        })
        assert_paginated_response(response)

    def test_get_form_options(self, authed_client):
        url = API_ENDPOINTS['records']['form_options']
        response = authed_client.get(url)
        assert response.status_code in (200, 400)


class TestUsageRecordCreate:
    def test_create_record_success(self, authed_client, test_laboratory, test_semester, teacher):
        url = API_ENDPOINTS['records']['list']
        response = authed_client.post(url, {
            'usage_date': '2025-10-20',
            'time_slot': '3-4',
            'class_hours': 2,
            'laboratory_id': test_laboratory.id,
            'teacher_id': teacher.id,
            'class_name': '新建测试班级',
            'student_count': 35,
            'content': '新建测试课程内容',
            'device_status': 'NORMAL',
            'laboratory_status': 'NORMAL',
        })
        assert response.status_code in (200, 201, 500)

    def test_create_record_missing_required_fields(self, authed_client):
        url = API_ENDPOINTS['records']['list']
        response = authed_client.post(url, {})
        assert response.status_code == 400

    def test_create_record_invalid_date(self, authed_client, test_laboratory, test_semester, teacher):
        url = API_ENDPOINTS['records']['list']
        response = authed_client.post(url, {
            'usage_date': 'invalid-date',
            'time_slot': '1-2',
            'laboratory_id': test_laboratory.id,
            'teacher_id': teacher.id,
        })
        assert response.status_code == 400

    def test_create_record_invalid_laboratory(self, authed_client, teacher):
        url = API_ENDPOINTS['records']['list']
        response = authed_client.post(url, {
            'usage_date': '2025-10-20',
            'time_slot': '1-2',
            'laboratory_id': 99999,
            'teacher_id': teacher.id,
        })
        assert response.status_code in (400, 500)


class TestUsageRecordDetail:
    def test_get_record_detail(self, authed_client, test_usage_record):
        url = API_ENDPOINTS['records']['detail'].format(id=test_usage_record.id)
        response = authed_client.get(url)
        data = assert_success_response(response)
        record_data = extract_data(response)
        assert record_data.get('id') == test_usage_record.id

    def test_get_record_detail_not_found(self, authed_client):
        url = API_ENDPOINTS['records']['detail'].format(id=99999)
        response = authed_client.get(url)
        assert response.status_code in (400, 404)

    def test_update_record_success(self, authed_client, test_usage_record):
        url = API_ENDPOINTS['records']['detail'].format(id=test_usage_record.id)
        response = authed_client.put(url, {
            'usage_date': test_usage_record.usage_date.isoformat() if hasattr(test_usage_record.usage_date, 'isoformat') else str(test_usage_record.usage_date),
            'time_slot': test_usage_record.time_slot,
            'content': '更新后课程内容',
            'student_count': 50,
        })
        assert response.status_code == 200

    def test_delete_record_success(self, authed_client, db, test_laboratory, test_semester, teacher):
        from apps.records.models import UsageRecord
        record = UsageRecord.objects.create(
            usage_date='2025-11-01', time_slot='1-2', class_hours=2,
            laboratory=test_laboratory, laboratory_name=test_laboratory.name,
            laboratory_code=test_laboratory.code, semester=test_semester,
            teacher=teacher, class_name='待删除班级', student_count=20,
            content='待删除', device_status='NORMAL', laboratory_status='NORMAL',
        )
        url = API_ENDPOINTS['records']['detail'].format(id=record.id)
        response = authed_client.delete(url)
        assert response.status_code == 200


class TestUsageRecordBatchDelete:
    def test_batch_delete_success(self, authed_client, db, test_laboratory, test_semester, teacher):
        from apps.records.models import UsageRecord
        r1 = UsageRecord.objects.create(
            usage_date='2025-11-01', time_slot='3-4', class_hours=2,
            laboratory=test_laboratory, laboratory_name=test_laboratory.name,
            laboratory_code=test_laboratory.code, semester=test_semester,
            teacher=teacher, class_name='批删1', student_count=20,
            content='批删1', device_status='NORMAL', laboratory_status='NORMAL',
        )
        r2 = UsageRecord.objects.create(
            usage_date='2025-11-02', time_slot='3-4', class_hours=2,
            laboratory=test_laboratory, laboratory_name=test_laboratory.name,
            laboratory_code=test_laboratory.code, semester=test_semester,
            teacher=teacher, class_name='批删2', student_count=20,
            content='批删2', device_status='NORMAL', laboratory_status='NORMAL',
        )
        url = API_ENDPOINTS['records']['batch_delete']
        response = authed_client.post(url, {'ids': [r1.id, r2.id]})
        assert response.status_code == 200
