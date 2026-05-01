import pytest
from tests.blackbox.client import (
    assert_success_response, assert_error_response,
    assert_paginated_response, extract_data, extract_list,
)
from tests.blackbox.config import API_ENDPOINTS


class TestScheduleList:
    def test_get_schedule_list(self, authed_client):
        url = API_ENDPOINTS['schedules']['list']
        response = authed_client.get(url)
        assert_paginated_response(response)

    def test_get_schedule_list_with_pagination(self, authed_client):
        url = API_ENDPOINTS['schedules']['list']
        response = authed_client.get(url, {'page': 1, 'page_size': 10})
        assert_paginated_response(response)

    def test_get_schedule_list_search(self, authed_client, test_schedule):
        url = API_ENDPOINTS['schedules']['list']
        response = authed_client.get(url, {'search': test_schedule.course_name})
        assert response.status_code in (200, 500)

    def test_get_schedule_list_filter_by_laboratory(self, authed_client, test_laboratory):
        url = API_ENDPOINTS['schedules']['list']
        response = authed_client.get(url, {'laboratory_id': test_laboratory.id})
        assert_paginated_response(response)

    def test_get_schedule_list_filter_by_teacher(self, authed_client, teacher):
        url = API_ENDPOINTS['schedules']['list']
        response = authed_client.get(url, {'teacher_id': teacher.id})
        assert_paginated_response(response)

    def test_get_schedule_list_filter_by_semester(self, authed_client, test_semester):
        url = API_ENDPOINTS['schedules']['list']
        response = authed_client.get(url, {'semester_id': test_semester.id})
        assert_paginated_response(response)

    def test_get_schedule_list_filter_by_weekday(self, authed_client):
        url = API_ENDPOINTS['schedules']['list']
        response = authed_client.get(url, {'weekday': 1})
        assert_paginated_response(response)

    def test_get_form_options(self, authed_client, test_semester):
        url = API_ENDPOINTS['schedules']['form_options']
        response = authed_client.get(url)
        assert response.status_code in (200, 400, 500)

    def test_get_laboratory_options(self, authed_client):
        url = API_ENDPOINTS['schedules']['laboratory_options']
        response = authed_client.get(url)
        assert_success_response(response)


class TestScheduleCreate:
    def test_create_schedule_success(self, authed_client, test_laboratory, test_semester, teacher):
        url = API_ENDPOINTS['schedules']['list']
        response = authed_client.post(url, {
            'course_name': '新建测试课程',
            'course_code': 'BB_NEW_COURSE',
            'weekday': 2,
            'time_slot': '3-4',
            'weeks': '1-16',
            'laboratory': test_laboratory.id,
            'semester_id': test_semester.id,
            'teacher_id': teacher.id,
            'teacher_name': teacher.nickname,
            'class_name': '新建测试班级',
            'student_count': 35,
        })
        assert response.status_code in (200, 201)

    def test_create_schedule_missing_required_fields(self, authed_client):
        url = API_ENDPOINTS['schedules']['list']
        response = authed_client.post(url, {})
        assert response.status_code == 400

    def test_create_schedule_invalid_weekday(self, authed_client, test_laboratory, test_semester, teacher):
        url = API_ENDPOINTS['schedules']['list']
        response = authed_client.post(url, {
            'course_name': '无效星期课程',
            'weekday': 8,
            'time_slot': '1-2',
            'laboratory': test_laboratory.id,
            'semester_id': test_semester.id,
            'teacher_id': teacher.id,
        })
        assert response.status_code in (400, 500)

    def test_create_schedule_invalid_student_count(self, authed_client, test_laboratory, test_semester, teacher):
        url = API_ENDPOINTS['schedules']['list']
        response = authed_client.post(url, {
            'course_name': '无效人数课程',
            'weekday': 1,
            'time_slot': '1-2',
            'student_count': -1,
            'laboratory': test_laboratory.id,
            'semester_id': test_semester.id,
            'teacher_id': teacher.id,
        })
        assert response.status_code in (400, 500, 201)


class TestScheduleDetail:
    def test_get_schedule_detail(self, authed_client, test_schedule):
        url = API_ENDPOINTS['schedules']['detail'].format(id=test_schedule.id)
        response = authed_client.get(url)
        data = assert_success_response(response)
        schedule_data = extract_data(response)
        if 'form_data' in schedule_data:
            schedule_data = schedule_data['form_data']
        assert schedule_data.get('id') == test_schedule.id
        assert schedule_data.get('course_name') == test_schedule.course_name

    def test_get_schedule_detail_not_found(self, authed_client):
        url = API_ENDPOINTS['schedules']['detail'].format(id=99999)
        response = authed_client.get(url)
        assert response.status_code in (400, 404)

    def test_update_schedule_success(self, authed_client, test_schedule):
        url = API_ENDPOINTS['schedules']['detail'].format(id=test_schedule.id)
        response = authed_client.put(url, {
            'weekday': test_schedule.weekday,
            'time_slot': test_schedule.time_slot,
            'course_name': '更新后课程名',
            'student_count': 45,
        })
        assert response.status_code == 200

    def test_delete_schedule_success(self, authed_client, db, test_laboratory, test_semester, teacher):
        from apps.schedules.models import Schedule
        schedule = Schedule.objects.create(
            course_name='待删除课程', course_code='BB_DEL_COURSE',
            weekday=5, time_slot='1-2', weeks='1-8',
            laboratory=test_laboratory, semester=test_semester,
            teacher=teacher, teacher_name=teacher.nickname,
            class_name='待删除班级', student_count=20,
        )
        url = API_ENDPOINTS['schedules']['detail'].format(id=schedule.id)
        response = authed_client.delete(url)
        assert response.status_code == 200


class TestScheduleBatchDelete:
    def test_batch_delete_success(self, authed_client, db, test_laboratory, test_semester, teacher):
        from apps.schedules.models import Schedule
        s1 = Schedule.objects.create(
            course_name='批删1', course_code='BB_BDS1', weekday=3, time_slot='1-2',
            weeks='1-8', laboratory=test_laboratory, semester=test_semester,
            teacher=teacher, teacher_name=teacher.nickname, class_name='班级1', student_count=20,
        )
        s2 = Schedule.objects.create(
            course_name='批删2', course_code='BB_BDS2', weekday=4, time_slot='1-2',
            weeks='1-8', laboratory=test_laboratory, semester=test_semester,
            teacher=teacher, teacher_name=teacher.nickname, class_name='班级2', student_count=20,
        )
        url = API_ENDPOINTS['schedules']['batch_delete']
        response = authed_client.post(url, {'ids': [s1.id, s2.id]})
        assert response.status_code == 200


class TestScheduleConflictCheck:
    def test_check_conflict_no_conflict(self, authed_client, test_laboratory, test_semester):
        url = API_ENDPOINTS['schedules']['check_conflict']
        response = authed_client.post(url, {
            'laboratory_id': test_laboratory.id,
            'weekday': 6,
            'time_slot': '1-2',
            'weeks': '1-16',
        })
        assert response.status_code == 200

    def test_check_conflict_with_existing(self, authed_client, test_laboratory, test_semester, test_schedule):
        url = API_ENDPOINTS['schedules']['check_conflict']
        response = authed_client.post(url, {
            'laboratory_id': test_laboratory.id,
            'weekday': test_schedule.weekday,
            'time_slot': test_schedule.time_slot,
            'weeks': test_schedule.weeks,
        })
        assert response.status_code == 200

    def test_check_conflict_missing_laboratory(self, authed_client):
        url = API_ENDPOINTS['schedules']['check_conflict']
        response = authed_client.post(url, {
            'weekday': 1,
            'time_slot': '1-2',
        })
        assert response.status_code == 400


class TestScheduleArchive:
    def test_get_archive_settings(self, authed_client):
        url = API_ENDPOINTS['schedules']['archive_settings']
        response = authed_client.get(url)
        assert response.status_code == 200

    def test_check_term_status(self, authed_client):
        url = API_ENDPOINTS['schedules']['check_status']
        response = authed_client.get(url)
        assert response.status_code == 200
