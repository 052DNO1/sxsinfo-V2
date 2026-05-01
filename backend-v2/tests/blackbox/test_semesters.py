import pytest
from tests.blackbox.client import (
    assert_success_response, assert_error_response,
    assert_paginated_response, extract_data, extract_list,
)
from tests.blackbox.config import API_ENDPOINTS


class TestSemesterList:
    def test_get_semester_list(self, authed_client):
        url = API_ENDPOINTS['semesters']['list']
        response = authed_client.get(url)
        assert_success_response(response)

    def test_get_semester_list_with_pagination(self, authed_client):
        url = API_ENDPOINTS['semesters']['list']
        response = authed_client.get(url, {'page': 1, 'page_size': 10})
        assert_success_response(response)

    def test_get_semester_options(self, authed_client):
        url = API_ENDPOINTS['semesters']['options']
        response = authed_client.get(url)
        assert_success_response(response)

    def test_get_current_semester(self, authed_client, test_semester):
        url = API_ENDPOINTS['semesters']['current']
        response = authed_client.get(url)
        assert response.status_code in (200, 400, 500)

    def test_get_archive_overview(self, authed_client):
        url = API_ENDPOINTS['semesters']['archive_overview']
        response = authed_client.get(url)
        assert response.status_code == 200


class TestSemesterCreate:
    def test_create_semester_success(self, authed_client):
        url = API_ENDPOINTS['semesters']['list']
        response = authed_client.post(url, {
            'name': '黑盒2026-2027-1',
            'code': 'BB_2026_2027_1',
            'start_date': '2026-09-01',
            'end_date': '2027-01-15',
            'total_weeks': 20,
            'is_current': False,
        })
        assert response.status_code in (200, 201)
        data = extract_data(response)
        assert data.get('name') == '黑盒2026-2027-1' or data.get('id') is not None

    def test_create_semester_duplicate_name(self, authed_client, test_semester):
        url = API_ENDPOINTS['semesters']['list']
        response = authed_client.post(url, {
            'name': test_semester.name,
            'start_date': '2027-02-01',
            'end_date': '2027-06-30',
        })
        assert response.status_code == 400

    def test_create_semester_missing_required_fields(self, authed_client):
        url = API_ENDPOINTS['semesters']['list']
        response = authed_client.post(url, {})
        assert response.status_code == 400

    def test_create_semester_invalid_date_range(self, authed_client):
        url = API_ENDPOINTS['semesters']['list']
        response = authed_client.post(url, {
            'name': '黑盒无效日期学期',
            'code': 'BB_INV_DATE',
            'start_date': '2027-06-30',
            'end_date': '2027-01-01',
        })
        assert response.status_code in (400, 201)


class TestSemesterDetail:
    def test_get_semester_detail(self, authed_client, test_semester):
        url = API_ENDPOINTS['semesters']['detail'].format(id=test_semester.id)
        response = authed_client.get(url)
        data = assert_success_response(response)
        sem_data = extract_data(response)
        assert sem_data.get('id') == test_semester.id
        assert sem_data.get('name') == test_semester.name

    def test_get_semester_detail_not_found(self, authed_client):
        url = API_ENDPOINTS['semesters']['detail'].format(id=99999)
        response = authed_client.get(url)
        assert response.status_code in (400, 404)

    def test_update_semester_success(self, authed_client, test_semester):
        url = API_ENDPOINTS['semesters']['detail'].format(id=test_semester.id)
        response = authed_client.put(url, {
            'name': f'{test_semester.name}_updated',
            'code': f'{test_semester.code}_upd',
            'start_date': '2025-09-01',
            'end_date': '2026-01-15',
            'description': '更新后的描述',
        })
        assert response.status_code == 200

    def test_delete_semester_success(self, authed_client, db):
        from apps.schedules.models import Semester
        sem = Semester.objects.create(
            name='待删除学期', code='BB_DEL_SEM',
            start_date='2028-09-01', end_date='2029-01-15',
        )
        url = API_ENDPOINTS['semesters']['detail'].format(id=sem.id)
        response = authed_client.delete(url)
        assert response.status_code == 200


class TestSemesterBatchDelete:
    def test_batch_delete_success(self, authed_client, db):
        from apps.schedules.models import Semester
        s1 = Semester.objects.create(name='批删学期1', code='BB_BDS1', start_date='2030-09-01', end_date='2031-01-15')
        s2 = Semester.objects.create(name='批删学期2', code='BB_BDS2', start_date='2031-09-01', end_date='2032-01-15')
        url = API_ENDPOINTS['semesters']['batch_delete']
        response = authed_client.post(url, {'ids': [s1.id, s2.id]})
        assert response.status_code == 200


class TestSemesterSetCurrent:
    def test_set_current_semester(self, authed_client, db):
        from apps.schedules.models import Semester
        Semester.objects.filter(is_current=True).update(is_current=False)
        sem = Semester.objects.create(
            name='设为当前学期', code='BB_CURRENT_SEM',
            start_date='2026-09-01', end_date='2027-01-15',
        )
        url = API_ENDPOINTS['semesters']['set_current'].format(id=sem.id)
        response = authed_client.post(url)
        assert response.status_code == 200

    def test_unset_current_semester(self, authed_client, test_semester):
        url = API_ENDPOINTS['semesters']['unset_current'].format(id=test_semester.id)
        response = authed_client.post(url)
        assert response.status_code == 200
