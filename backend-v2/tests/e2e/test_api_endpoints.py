import pytest
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def authed_client(db, wb_super_admin):
    client = APIClient()
    refresh = RefreshToken.for_user(wb_super_admin)
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    return client


class TestAuthAPI:
    def test_captcha(self, api_client):
        response = api_client.get('/api/v1/auth/captcha/')
        assert response.status_code == 200
        assert 'captcha_key' in response.data['data']
        assert 'captcha_image' in response.data['data']

    def test_login_missing_fields(self, api_client):
        response = api_client.post('/api/v1/auth/login/', {})
        assert response.status_code == 400

    def test_login_wrong_credentials(self, api_client, db, wb_teacher):
        response = api_client.post('/api/v1/auth/login/', {
            'username': wb_teacher.username,
            'password': 'wrongpassword',
        })
        assert response.status_code == 401

    def test_unauthenticated_access(self, api_client, db):
        response = api_client.get('/api/v1/users/')
        assert response.status_code in [401, 403]


class TestLaboratoryAPI:
    def test_list_laboratories(self, authed_client):
        response = authed_client.get('/api/v1/laboratories/')
        assert response.status_code == 200

    def test_create_laboratory(self, authed_client, wb_department):
        response = authed_client.post('/api/v1/laboratories/', {
            'name': 'API创建实训室',
            'code': 'API_LAB_001',
            'department': wb_department.id,
        })
        assert response.status_code in [200, 201]

    def test_create_laboratory_missing_fields(self, authed_client):
        response = authed_client.post('/api/v1/laboratories/', {})
        assert response.status_code == 400


class TestScheduleAPI:
    def test_list_schedules(self, authed_client):
        response = authed_client.get('/api/v1/schedules/')
        assert response.status_code == 200


class TestSemesterAPI:
    def test_list_semesters(self, authed_client):
        response = authed_client.get('/api/v1/semesters/')
        assert response.status_code == 200


class TestRecordAPI:
    def test_list_records(self, authed_client):
        response = authed_client.get('/api/v1/records/')
        assert response.status_code == 200


class TestWorkOrderAPI:
    def test_list_work_orders(self, authed_client):
        response = authed_client.get('/api/v1/work-orders/')
        assert response.status_code == 200


class TestNotificationAPI:
    def test_list_notifications(self, authed_client):
        response = authed_client.get('/api/v1/notifications/')
        assert response.status_code == 200

    def test_unread_count(self, authed_client):
        response = authed_client.get('/api/v1/notifications/unread-count/')
        assert response.status_code == 200


class TestStatisticsAPI:
    def test_dashboard(self, authed_client):
        response = authed_client.get('/api/v1/statistics/dashboard/')
        assert response.status_code == 200
