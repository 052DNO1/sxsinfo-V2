import pytest
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def authenticated_client(api_client, super_admin_user):
    refresh = RefreshToken.for_user(super_admin_user)
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    return api_client


class TestLaboratoryAPIEndpoints:

    def test_get_laboratory_list_success(self, authenticated_client, test_laboratory):
        response = authenticated_client.get('/api/v1/laboratories/')
        assert response.status_code == 200
        data = response.json()
        inner = data.get('data', data)
        assert 'list' in inner or 'results' in inner or 'pagination' in inner

    def test_get_laboratory_list_with_pagination(self, authenticated_client):
        response = authenticated_client.get('/api/v1/laboratories/?page=1&page_size=10')
        assert response.status_code == 200
        data = response.json()
        inner = data.get('data', data)
        if 'pagination' in inner:
            assert 'total' in inner['pagination']

    def test_get_laboratory_detail_success(self, authenticated_client, test_laboratory):
        response = authenticated_client.get(f'/api/v1/laboratories/{test_laboratory.id}/')
        assert response.status_code == 200
        data = response.json()
        inner = data.get('data', data)
        assert 'id' in inner
        assert 'name' in inner

    def test_get_laboratory_detail_not_found(self, authenticated_client):
        response = authenticated_client.get('/api/v1/laboratories/99999/')
        assert response.status_code == 404

    def test_create_laboratory_success(self, authenticated_client, test_department, lab_admin_user):
        data = {
            'name': 'API测试实训室',
            'code': 'API_TEST_001',
            'building': 'API楼',
            'floor': 2,
            'room_number': '201',
            'capacity': 35,
            'laboratory_type': 'COMPUTER',
            'department': test_department.id,
            'admin': lab_admin_user.id,
            'description': '通过API创建',
        }
        response = authenticated_client.post('/api/v1/laboratories/', data, format='json')
        assert response.status_code == 201
        result = response.json()
        inner = result.get('data', result)
        assert 'id' in inner

    def test_create_laboratory_missing_required_field(self, authenticated_client):
        data = {
            'name': '',
            'code': '',
        }
        response = authenticated_client.post('/api/v1/laboratories/', data, format='json')
        assert response.status_code == 400

    def test_update_laboratory_success(self, authenticated_client, test_laboratory):
        data = {
            'name': 'API更新的名称',
            'code': test_laboratory.code,
            'capacity': 60,
            'note': '通过API更新',
        }
        response = authenticated_client.put(
            f'/api/v1/laboratories/{test_laboratory.id}/',
            data,
            format='json',
        )
        assert response.status_code == 200

    def test_update_laboratory_set_admin_to_none(
        self, authenticated_client, test_laboratory
    ):
        update_data = {
            'name': test_laboratory.name,
            'code': test_laboratory.code,
            'admin': None,
        }
        response = authenticated_client.put(
            f'/api/v1/laboratories/{test_laboratory.id}/',
            update_data,
            format='json',
        )
        assert response.status_code == 200, f"期望200，实际{response.status_code}，响应：{response.content}"

    def test_update_laboratory_set_admin_to_zero(
        self, authenticated_client, test_laboratory
    ):
        update_data = {
            'name': test_laboratory.name,
            'code': test_laboratory.code,
            'admin': 0,
        }
        response = authenticated_client.put(
            f'/api/v1/laboratories/{test_laboratory.id}/',
            update_data,
            format='json',
        )
        assert response.status_code == 200, f"期望200，实际{response.status_code}"

    def test_update_laboratory_invalid_admin_id(
        self, authenticated_client, test_laboratory
    ):
        update_data = {
            'name': test_laboratory.name,
            'code': test_laboratory.code,
            'admin': 99999,
        }
        response = authenticated_client.put(
            f'/api/v1/laboratories/{test_laboratory.id}/',
            update_data,
            format='json',
        )
        assert response.status_code == 400

    def test_delete_laboratory_success(self, authenticated_client, test_department):
        from apps.laboratories.models import Laboratory
        lab = Laboratory.objects.create(
            name='待删除API',
            code='DEL_API_001',
            building='测试楼',
            floor=1,
            room_number='101',
            capacity=20,
            laboratory_type='COMPUTER',
            department=test_department,
            status=1,
        )
        response = authenticated_client.delete(f'/api/v1/laboratories/{lab.id}/')
        assert response.status_code == 200 or response.status_code == 204

    def test_unauthenticated_access_denied(self, api_client):
        response = api_client.get('/api/v1/laboratories/')
        assert response.status_code == 401 or response.status_code == 403


class TestLaboratoryAPIErrorHandling:

    @pytest.fixture
    def authenticated_client(self, api_client, super_admin_user):
        refresh = RefreshToken.for_user(super_admin_user)
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        return api_client

    def test_validation_error_returns_400_not_500(
        self, authenticated_client, test_laboratory
    ):
        invalid_data = {
            'name': '',
            'code': '',
        }
        response = authenticated_client.put(
            f'/api/v1/laboratories/{test_laboratory.id}/',
            invalid_data,
            format='json',
        )
        assert response.status_code == 400, \
            f"验证错误应该返回400，但返回了{response.status_code}"
