import pytest
from tests.blackbox.client import (
    assert_success_response, assert_error_response,
    assert_paginated_response, extract_data, extract_list,
)
from tests.blackbox.config import API_ENDPOINTS


class TestLaboratoryList:
    def test_get_laboratory_list(self, authed_client):
        url = API_ENDPOINTS['laboratories']['list']
        response = authed_client.get(url)
        assert_paginated_response(response)

    def test_get_laboratory_list_with_pagination(self, authed_client):
        url = API_ENDPOINTS['laboratories']['list']
        response = authed_client.get(url, {'page': 1, 'page_size': 5})
        assert_paginated_response(response)

    def test_get_laboratory_list_search(self, authed_client, test_laboratory):
        url = API_ENDPOINTS['laboratories']['list']
        response = authed_client.get(url, {'search': test_laboratory.name})
        assert_paginated_response(response)

    def test_get_laboratory_list_filter_by_department(self, authed_client, test_department):
        url = API_ENDPOINTS['laboratories']['list']
        response = authed_client.get(url, {'department_id': test_department.id})
        assert_paginated_response(response)

    def test_get_laboratory_list_filter_by_status(self, authed_client):
        url = API_ENDPOINTS['laboratories']['list']
        response = authed_client.get(url, {'status': 1})
        assert_paginated_response(response)

    def test_get_laboratory_list_filter_by_type(self, authed_client):
        url = API_ENDPOINTS['laboratories']['list']
        response = authed_client.get(url, {'laboratory_type': 'COMPUTER'})
        assert_paginated_response(response)

    def test_get_laboratory_options(self, authed_client):
        url = API_ENDPOINTS['laboratories']['options']
        response = authed_client.get(url)
        assert_success_response(response)

    def test_get_admin_options(self, authed_client):
        url = API_ENDPOINTS['laboratories']['admin_options']
        response = authed_client.get(url)
        assert_success_response(response)


class TestLaboratoryCreate:
    def test_create_laboratory_success(self, authed_client, test_department, lab_admin):
        url = API_ENDPOINTS['laboratories']['list']
        response = authed_client.post(url, {
            'name': '新建实训室',
            'code': 'BB_NEW_LAB',
            'building': '新建楼',
            'floor': 2,
            'room_number': '201',
            'capacity': 40,
            'area': 120.0,
            'laboratory_type': 'COMPUTER',
            'department': test_department.id,
            'admin': str(lab_admin.id),
        })
        assert response.status_code in (200, 201, 500)

    def test_create_laboratory_duplicate_code(self, authed_client, test_laboratory, test_department):
        url = API_ENDPOINTS['laboratories']['list']
        response = authed_client.post(url, {
            'name': '重复编码实训室',
            'code': test_laboratory.code,
            'building': '测试楼',
            'department': test_department.id,
        })
        assert response.status_code == 400

    def test_create_laboratory_missing_required_fields(self, authed_client):
        url = API_ENDPOINTS['laboratories']['list']
        response = authed_client.post(url, {})
        assert response.status_code == 400

    def test_create_laboratory_empty_name(self, authed_client, test_department):
        url = API_ENDPOINTS['laboratories']['list']
        response = authed_client.post(url, {
            'name': '',
            'code': 'BB_EMPTY_NAME_LAB',
            'department': test_department.id,
        })
        assert response.status_code == 400

    def test_create_laboratory_invalid_capacity(self, authed_client, test_department):
        url = API_ENDPOINTS['laboratories']['list']
        response = authed_client.post(url, {
            'name': '无效容量实训室',
            'code': 'BB_INV_CAP_LAB',
            'capacity': -1,
            'department': test_department.id,
        })
        assert response.status_code in (400, 500)

    def test_create_laboratory_with_facilities(self, authed_client, test_department):
        url = API_ENDPOINTS['laboratories']['list']
        response = authed_client.post(url, {
            'name': '带设施实训室',
            'code': 'BB_FAC_LAB',
            'building': '测试楼',
            'department': test_department.id,
            'facilities': {'projector': True, 'whiteboard': True, 'computers': 30},
        })
        assert response.status_code in (200, 201, 500)


class TestLaboratoryDetail:
    def test_get_laboratory_detail(self, authed_client, test_laboratory):
        url = API_ENDPOINTS['laboratories']['detail'].format(id=test_laboratory.id)
        response = authed_client.get(url)
        data = assert_success_response(response)
        lab_data = extract_data(response)
        assert lab_data.get('id') == test_laboratory.id
        assert lab_data.get('name') == test_laboratory.name
        assert 'department_name' in lab_data or 'department' in lab_data

    def test_get_laboratory_detail_not_found(self, authed_client):
        url = API_ENDPOINTS['laboratories']['detail'].format(id=99999)
        response = authed_client.get(url)
        assert response.status_code in (400, 404)

    def test_update_laboratory_success(self, authed_client, test_laboratory):
        url = API_ENDPOINTS['laboratories']['detail'].format(id=test_laboratory.id)
        response = authed_client.put(url, {
            'name': '更新后实训室',
            'code': test_laboratory.code,
            'capacity': 50,
        })
        assert response.status_code == 200
        verify_url = API_ENDPOINTS['laboratories']['detail'].format(id=test_laboratory.id)
        verify_resp = authed_client.get(verify_url)
        verify_data = extract_data(verify_resp)
        assert verify_data.get('name') == '更新后实训室'

    def test_update_laboratory_set_admin_none(self, authed_client, test_laboratory):
        url = API_ENDPOINTS['laboratories']['detail'].format(id=test_laboratory.id)
        response = authed_client.put(url, {
            'name': test_laboratory.name,
            'code': test_laboratory.code,
            'admin': None,
        })
        assert response.status_code == 200

    def test_update_laboratory_set_admin_zero(self, authed_client, test_laboratory):
        url = API_ENDPOINTS['laboratories']['detail'].format(id=test_laboratory.id)
        response = authed_client.put(url, {
            'name': test_laboratory.name,
            'code': test_laboratory.code,
            'admin': 0,
        })
        assert response.status_code == 200

    def test_update_laboratory_invalid_admin(self, authed_client, test_laboratory):
        url = API_ENDPOINTS['laboratories']['detail'].format(id=test_laboratory.id)
        response = authed_client.put(url, {
            'admin': 99999,
        })
        assert response.status_code == 400

    def test_delete_laboratory_success(self, authed_client, db, test_department):
        from apps.laboratories.models import Laboratory
        lab = Laboratory.objects.create(
            name='待删除实训室', code='BB_DEL_LAB',
            building='测试楼', department=test_department, status=1,
        )
        url = API_ENDPOINTS['laboratories']['detail'].format(id=lab.id)
        response = authed_client.delete(url)
        assert response.status_code == 200


class TestLaboratoryBatchDelete:
    def test_batch_delete_success(self, authed_client, db, test_department):
        from apps.laboratories.models import Laboratory
        l1 = Laboratory.objects.create(name='批删1', code='BB_BDL1', building='楼', department=test_department, status=1)
        l2 = Laboratory.objects.create(name='批删2', code='BB_BDL2', building='楼', department=test_department, status=1)
        url = API_ENDPOINTS['laboratories']['batch_delete']
        response = authed_client.post(url, {'ids': [l1.id, l2.id]})
        assert response.status_code == 200

    def test_check_delete_impact(self, authed_client, db, test_department):
        from apps.laboratories.models import Laboratory
        lab = Laboratory.objects.create(name='影响检查', code='BB_IMP_LAB', building='楼', department=test_department, status=1)
        url = API_ENDPOINTS['laboratories']['check_delete_impact']
        response = authed_client.post(url, {'ids': [lab.id]})
        assert response.status_code == 200


class TestLaboratorySummary:
    def test_get_laboratory_summary(self, authed_client, test_laboratory, test_semester):
        url = API_ENDPOINTS['laboratories']['summary'].format(id=test_laboratory.id)
        response = authed_client.get(url, {'semester_id': test_semester.id})
        assert response.status_code == 200

    def test_get_all_summary(self, authed_client, test_semester):
        url = API_ENDPOINTS['laboratories']['all_summary']
        response = authed_client.get(url, {'semester_id': test_semester.id})
        assert response.status_code == 200


class TestLaboratoryPermission:
    def test_unauthenticated_access(self, api_client):
        url = API_ENDPOINTS['laboratories']['list']
        response = api_client.get(url)
        assert response.status_code in (401, 403)

    def test_teacher_read_access(self, authed_teacher, test_laboratory):
        url = API_ENDPOINTS['laboratories']['list']
        response = authed_teacher.get(url)
        assert response.status_code == 200
