import pytest
from tests.blackbox.client import (
    assert_success_response, assert_error_response,
    assert_paginated_response, extract_data, extract_list,
)
from tests.blackbox.config import API_ENDPOINTS


class TestDepartmentList:
    def test_get_department_list(self, authed_client):
        url = API_ENDPOINTS['departments']['list']
        response = authed_client.get(url)
        assert_success_response(response)

    def test_get_department_list_with_pagination(self, authed_client):
        url = API_ENDPOINTS['departments']['list']
        response = authed_client.get(url, {'page': 1, 'page_size': 10})
        assert_success_response(response)

    def test_get_department_list_search(self, authed_client, test_department):
        url = API_ENDPOINTS['departments']['list']
        response = authed_client.get(url, {'search': test_department.name})
        assert_success_response(response)

    def test_get_department_list_nopage(self, authed_client):
        url = API_ENDPOINTS['departments']['list']
        response = authed_client.get(url, {'nopage': True})
        assert_success_response(response)

    def test_get_department_options(self, authed_client):
        url = API_ENDPOINTS['departments']['options']
        response = authed_client.get(url)
        assert_success_response(response)


class TestDepartmentCreate:
    def test_create_department_success(self, authed_client):
        url = API_ENDPOINTS['departments']['list']
        response = authed_client.post(url, {
            'name': '新建测试分院',
            'code': 'BB_NEW_DEPT',
            'description': '黑盒测试创建',
        })
        assert response.status_code in (200, 201)
        data = extract_data(response)
        assert data.get('name') == '新建测试分院'

    def test_create_department_with_parent(self, authed_client, test_department):
        url = API_ENDPOINTS['departments']['list']
        response = authed_client.post(url, {
            'name': '子分院',
            'code': 'BB_CHILD_DEPT',
            'parent': test_department.id,
        })
        assert response.status_code in (200, 201)

    def test_create_department_duplicate_code(self, authed_client, test_department):
        url = API_ENDPOINTS['departments']['list']
        response = authed_client.post(url, {
            'name': '重复编码分院',
            'code': test_department.code,
        })
        assert response.status_code == 400

    def test_create_department_missing_name(self, authed_client):
        url = API_ENDPOINTS['departments']['list']
        response = authed_client.post(url, {
            'code': 'BB_NO_NAME',
        })
        assert response.status_code == 400

    def test_create_department_missing_code(self, authed_client):
        url = API_ENDPOINTS['departments']['list']
        response = authed_client.post(url, {
            'name': '无编码分院',
        })
        assert response.status_code in (400, 201)

    def test_create_department_empty_name(self, authed_client):
        url = API_ENDPOINTS['departments']['list']
        response = authed_client.post(url, {
            'name': '',
            'code': 'BB_EMPTY_NAME',
        })
        assert response.status_code == 400


class TestDepartmentDetail:
    def test_get_department_detail(self, authed_client, test_department):
        url = API_ENDPOINTS['departments']['detail'].format(id=test_department.id)
        response = authed_client.get(url)
        data = assert_success_response(response)
        dept_data = extract_data(response)
        assert dept_data.get('id') == test_department.id
        assert dept_data.get('name') == test_department.name

    def test_get_department_detail_not_found(self, authed_client):
        url = API_ENDPOINTS['departments']['detail'].format(id=99999)
        response = authed_client.get(url)
        assert response.status_code in (400, 404)

    def test_update_department_success(self, authed_client, test_department):
        url = API_ENDPOINTS['departments']['detail'].format(id=test_department.id)
        response = authed_client.put(url, {
            'name': '更新后分院名',
            'code': test_department.code,
            'description': '更新描述',
        })
        assert response.status_code == 200
        verify_url = API_ENDPOINTS['departments']['detail'].format(id=test_department.id)
        verify_resp = authed_client.get(verify_url)
        verify_data = extract_data(verify_resp)
        assert verify_data.get('name') == '更新后分院名'

    def test_delete_department_success(self, authed_client, db):
        from apps.users.models import Department
        dept = Department.objects.create(name='待删除分院', code='BB_DEL_DEPT')
        url = API_ENDPOINTS['departments']['detail'].format(id=dept.id)
        response = authed_client.delete(url)
        assert response.status_code == 200

    def test_delete_department_with_cascade(self, authed_client, db):
        from apps.users.models import Department
        dept = Department.objects.create(name='级联删除分院', code='BB_CASCADE_DEPT')
        url = API_ENDPOINTS['departments']['detail'].format(id=dept.id)
        response = authed_client.delete(url + '?cascade=true')
        assert response.status_code == 200


class TestDepartmentBatchDelete:
    def test_batch_delete_success(self, authed_client, db):
        from apps.users.models import Department
        d1 = Department.objects.create(name='批量删1', code='BB_BD1')
        d2 = Department.objects.create(name='批量删2', code='BB_BD2')
        url = API_ENDPOINTS['departments']['batch_delete']
        response = authed_client.post(url, {'ids': [d1.id, d2.id]})
        assert response.status_code == 200

    def test_batch_delete_empty_list(self, authed_client):
        url = API_ENDPOINTS['departments']['batch_delete']
        response = authed_client.post(url, {'ids': []})
        assert response.status_code in (200, 400)


class TestDepartmentCheckConflicts:
    def test_check_conflicts(self, authed_client, test_department, lab_admin):
        url = API_ENDPOINTS['departments']['check_conflicts']
        response = authed_client.post(url, {
            'department_id': test_department.id,
            'manager_ids': [lab_admin.id],
        })
        assert response.status_code == 200

    def test_check_conflicts_missing_params(self, authed_client):
        url = API_ENDPOINTS['departments']['check_conflicts']
        response = authed_client.post(url, {})
        assert response.status_code in (200, 400)


class TestDepartmentTreeStructure:
    def test_parent_child_relationship(self, authed_client, test_department, test_department_child):
        url = API_ENDPOINTS['departments']['detail'].format(id=test_department_child.id)
        response = authed_client.get(url)
        data = assert_success_response(response)
        dept_data = extract_data(response)
        assert dept_data.get('id') == test_department_child.id

    def test_create_deep_nested_department(self, authed_client, test_department_child):
        url = API_ENDPOINTS['departments']['list']
        response = authed_client.post(url, {
            'name': '三级子分院',
            'code': 'BB_DEEP_DEPT',
            'parent': test_department_child.id,
        })
        assert response.status_code in (200, 201)
