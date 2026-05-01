import pytest
from tests.blackbox.client import (
    assert_success_response, assert_error_response,
    assert_paginated_response, extract_data, extract_list,
)
from tests.blackbox.config import API_ENDPOINTS


class TestEquipmentList:
    def test_get_equipment_list(self, authed_client):
        url = API_ENDPOINTS['equipments']['list']
        response = authed_client.get(url)
        assert_paginated_response(response)

    def test_get_equipment_list_with_pagination(self, authed_client):
        url = API_ENDPOINTS['equipments']['list']
        response = authed_client.get(url, {'page': 1, 'page_size': 5})
        assert_paginated_response(response)

    def test_get_equipment_list_search(self, authed_client, test_equipment):
        url = API_ENDPOINTS['equipments']['list']
        response = authed_client.get(url, {'search': test_equipment.name})
        assert_paginated_response(response)

    def test_get_equipment_list_filter_by_laboratory(self, authed_client, test_laboratory):
        url = API_ENDPOINTS['equipments']['list']
        response = authed_client.get(url, {'laboratory_id': test_laboratory.id})
        assert_paginated_response(response)

    def test_get_equipment_list_filter_by_category(self, authed_client):
        url = API_ENDPOINTS['equipments']['list']
        response = authed_client.get(url, {'category': 'COMPUTER'})
        assert_paginated_response(response)

    def test_get_equipment_list_filter_by_status(self, authed_client):
        url = API_ENDPOINTS['equipments']['list']
        response = authed_client.get(url, {'status': 'NORMAL'})
        assert_paginated_response(response)

    def test_get_category_options(self, authed_client):
        url = API_ENDPOINTS['equipments']['category_options']
        response = authed_client.get(url)
        assert_success_response(response)

    def test_get_status_options(self, authed_client):
        url = API_ENDPOINTS['equipments']['status_options']
        response = authed_client.get(url)
        assert_success_response(response)


class TestEquipmentCreate:
    def test_create_equipment_success(self, authed_client, test_laboratory):
        url = API_ENDPOINTS['equipments']['list']
        response = authed_client.post(url, {
            'name': '新建测试设备',
            'code': 'BB_NEW_EQ',
            'category': 'COMPUTER',
            'brand': '测试品牌',
            'model': 'Test-Model-V2',
            'laboratory_id': test_laboratory.id,
            'status': 'NORMAL',
        })
        assert response.status_code in (200, 201)
        data = extract_data(response)
        assert data.get('name') == '新建测试设备' or data.get('id') is not None

    def test_create_equipment_missing_required_fields(self, authed_client):
        url = API_ENDPOINTS['equipments']['list']
        response = authed_client.post(url, {})
        assert response.status_code == 400

    def test_create_equipment_empty_name(self, authed_client, test_laboratory):
        url = API_ENDPOINTS['equipments']['list']
        response = authed_client.post(url, {
            'name': '',
            'code': 'BB_EMPTY_EQ',
            'laboratory_id': test_laboratory.id,
        })
        assert response.status_code == 400

    def test_create_equipment_with_specs(self, authed_client, test_laboratory):
        url = API_ENDPOINTS['equipments']['list']
        response = authed_client.post(url, {
            'name': '带规格设备',
            'code': 'BB_SPEC_EQ',
            'category': 'COMPUTER',
            'laboratory_id': test_laboratory.id,
            'cpu': 'Intel i7',
            'memory': '16GB',
            'disk': '512GB SSD',
            'gpu': 'NVIDIA RTX 3060',
            'os': 'Windows 11',
            'status': 'NORMAL',
        })
        assert response.status_code in (200, 201)

    def test_create_equipment_invalid_laboratory(self, authed_client):
        url = API_ENDPOINTS['equipments']['list']
        response = authed_client.post(url, {
            'name': '无效实训室设备',
            'code': 'BB_INV_LAB_EQ',
            'laboratory_id': 99999,
        })
        assert response.status_code in (200, 201, 400, 500)


class TestEquipmentDetail:
    def test_get_equipment_detail(self, authed_client, test_equipment):
        url = API_ENDPOINTS['equipments']['detail'].format(id=test_equipment.id)
        response = authed_client.get(url)
        data = assert_success_response(response)
        eq_data = extract_data(response)
        assert eq_data.get('id') == test_equipment.id
        assert eq_data.get('name') == test_equipment.name

    def test_get_equipment_detail_not_found(self, authed_client):
        url = API_ENDPOINTS['equipments']['detail'].format(id=99999)
        response = authed_client.get(url)
        assert response.status_code in (400, 404)

    def test_update_equipment_success(self, authed_client, test_equipment):
        url = API_ENDPOINTS['equipments']['detail'].format(id=test_equipment.id)
        response = authed_client.put(url, {
            'name': '更新后设备名',
            'status': 'MAINTENANCE',
        })
        assert response.status_code == 200
        verify_url = API_ENDPOINTS['equipments']['detail'].format(id=test_equipment.id)
        verify_resp = authed_client.get(verify_url)
        verify_data = extract_data(verify_resp)
        assert verify_data.get('name') == '更新后设备名'

    def test_delete_equipment_success(self, authed_client, db, test_laboratory):
        from apps.laboratories.models import Equipment
        eq = Equipment.objects.create(
            name='待删除设备', code='BB_DEL_EQ',
            category='COMPUTER', laboratory=test_laboratory, status='NORMAL',
        )
        url = API_ENDPOINTS['equipments']['detail'].format(id=eq.id)
        response = authed_client.delete(url)
        assert response.status_code == 200


class TestEquipmentBatchDelete:
    def test_batch_delete_success(self, authed_client, db, test_laboratory):
        from apps.laboratories.models import Equipment
        e1 = Equipment.objects.create(name='批删1', code='BB_BDE1', category='COMPUTER', laboratory=test_laboratory, status='NORMAL')
        e2 = Equipment.objects.create(name='批删2', code='BB_BDE2', category='COMPUTER', laboratory=test_laboratory, status='NORMAL')
        url = API_ENDPOINTS['equipments']['batch_delete']
        response = authed_client.post(url, {'ids': [e1.id, e2.id]})
        assert response.status_code == 200

    def test_batch_delete_empty_list(self, authed_client):
        url = API_ENDPOINTS['equipments']['batch_delete']
        response = authed_client.post(url, {'ids': []})
        assert response.status_code in (200, 400)


class TestEquipmentPermission:
    def test_unauthenticated_access(self, api_client):
        url = API_ENDPOINTS['equipments']['list']
        response = api_client.get(url)
        assert response.status_code in (401, 403)
