import pytest
from tests.blackbox.config import API_ENDPOINTS


class TestDashboardStats:
    def test_get_dashboard(self, authed_client):
        url = API_ENDPOINTS['statistics']['dashboard']
        response = authed_client.get(url)
        assert response.status_code in (200, 403, 400)

    def test_get_teacher_stats(self, authed_teacher):
        url = API_ENDPOINTS['statistics']['teacher']
        response = authed_teacher.get(url)
        assert response.status_code in (200, 403, 400)

    def test_get_lab_admin_stats(self, authed_lab_admin):
        url = API_ENDPOINTS['statistics']['lab_admin']
        response = authed_lab_admin.get(url)
        assert response.status_code in (200, 403, 400)

    def test_get_super_admin_stats(self, authed_super_admin):
        url = API_ENDPOINTS['statistics']['super_admin']
        response = authed_super_admin.get(url)
        assert response.status_code in (200, 403, 400)

    def test_get_system_superuser_stats(self, authed_client):
        url = API_ENDPOINTS['statistics']['system_superuser']
        response = authed_client.get(url)
        assert response.status_code in (200, 403, 400)


class TestSpecializedDashboards:
    def test_get_user_management_dashboard(self, authed_client):
        url = API_ENDPOINTS['statistics']['user_management']
        response = authed_client.get(url)
        assert response.status_code in (200, 403, 400)

    def test_get_lab_resource_dashboard(self, authed_client):
        url = API_ENDPOINTS['statistics']['lab_resource']
        response = authed_client.get(url)
        assert response.status_code in (200, 403, 400)

    def test_get_scheduling_dashboard(self, authed_client):
        url = API_ENDPOINTS['statistics']['scheduling']
        response = authed_client.get(url)
        assert response.status_code in (200, 403, 400)

    def test_get_personal_teaching_dashboard(self, authed_teacher):
        url = API_ENDPOINTS['statistics']['personal_teaching']
        response = authed_teacher.get(url)
        assert response.status_code in (200, 403, 400)


class TestComprehensiveStats:
    def test_get_comprehensive_stats(self, authed_client):
        url = API_ENDPOINTS['statistics']['comprehensive']
        response = authed_client.get(url)
        assert response.status_code in (200, 403, 400)

    def test_export_comprehensive_stats(self, authed_client):
        url = API_ENDPOINTS['statistics']['comprehensive_export']
        response = authed_client.post(url)
        assert response.status_code in (200, 201, 202, 403, 400)


class TestStatsPermission:
    def test_unauthenticated_cannot_access_stats(self, api_client):
        url = API_ENDPOINTS['statistics']['dashboard']
        response = api_client.get(url)
        assert response.status_code in (401, 403)
