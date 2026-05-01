import pytest
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken


@pytest.fixture
def authed_client(db, wb_super_admin):
    client = APIClient()
    refresh = RefreshToken.for_user(wb_super_admin)
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    return client


@pytest.fixture
def teacher_client(db, wb_teacher):
    client = APIClient()
    refresh = RefreshToken.for_user(wb_teacher)
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    return client


@pytest.fixture
def dept_admin_client(db, wb_dept_admin):
    client = APIClient()
    refresh = RefreshToken.for_user(wb_dept_admin)
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    return client


class TestUserAPI:
    def test_list_users(self, authed_client):
        response = authed_client.get('/api/v1/users/')
        assert response.status_code == 200

    def test_create_user(self, authed_client, wb_department):
        import uuid
        response = authed_client.post('/api/v1/users/', {
            'username': f'api_user_{uuid.uuid4().hex[:6]}',
            'nickname': 'API创建用户',
            'role': 1,
            'department': wb_department.id,
        })
        assert response.status_code in [200, 201]

    def test_create_user_missing_fields(self, authed_client):
        response = authed_client.post('/api/v1/users/', {})
        assert response.status_code == 400

    def test_get_user_detail(self, authed_client, wb_teacher):
        response = authed_client.get(f'/api/v1/users/{wb_teacher.id}/')
        assert response.status_code == 200

    def test_delete_user(self, authed_client, wb_teacher):
        response = authed_client.delete(f'/api/v1/users/{wb_teacher.id}/')
        assert response.status_code in [200, 204]

    def test_teacher_cannot_create_user(self, teacher_client, wb_department):
        response = teacher_client.post('/api/v1/users/', {
            'username': 'unauthorized_user',
            'nickname': '未授权创建',
            'role': 1,
            'department': wb_department.id,
        })
        assert response.status_code in [403, 405]


class TestDepartmentAPI:
    def test_list_departments(self, authed_client):
        response = authed_client.get('/api/v1/departments/')
        assert response.status_code == 200

    def test_create_department(self, authed_client):
        import uuid
        response = authed_client.post('/api/v1/departments/', {
            'name': f'API创建分院_{uuid.uuid4().hex[:4]}',
        })
        assert response.status_code in [200, 201]


class TestScheduleAPI:
    def test_list_schedules(self, authed_client):
        response = authed_client.get('/api/v1/schedules/')
        assert response.status_code == 200

    def test_create_schedule(self, authed_client, wb_laboratory, wb_teacher):
        response = authed_client.post('/api/v1/schedules/', {
            'course_name': 'API创建课程',
            'weekday': 3,
            'time_slot': '5-6',
            'weeks': '1-16',
            'laboratory': wb_laboratory.id,
            'teacher_name': wb_teacher.nickname,
        })
        assert response.status_code in [200, 201]

    def test_delete_schedule(self, authed_client, wb_schedule):
        response = authed_client.delete(f'/api/v1/schedules/{wb_schedule.id}/')
        assert response.status_code in [200, 204]


class TestSemesterAPI:
    def test_list_semesters(self, authed_client):
        response = authed_client.get('/api/v1/semesters/')
        assert response.status_code == 200

    def test_get_current_semester(self, authed_client):
        response = authed_client.get('/api/v1/semesters/current/')
        assert response.status_code == 200


class TestRecordAPI:
    def test_list_records(self, authed_client):
        response = authed_client.get('/api/v1/records/')
        assert response.status_code == 200

    def test_create_record(self, authed_client, wb_laboratory, wb_semester):
        response = authed_client.post('/api/v1/records/', {
            'usage_date': '2025-10-20',
            'time_slot': '3-4',
            'class_hours': 2,
            'laboratory_id': wb_laboratory.id,
            'content': 'API测试内容',
            'device_status': 'NORMAL',
            'laboratory_status': 'NORMAL',
        })
        assert response.status_code in [200, 201]

    def test_teacher_create_record(self, teacher_client, wb_laboratory, wb_semester):
        response = teacher_client.post('/api/v1/records/', {
            'usage_date': '2025-10-20',
            'time_slot': '3-4',
            'class_hours': 2,
            'laboratory_id': wb_laboratory.id,
            'content': '教师创建记录',
            'device_status': 'NORMAL',
            'laboratory_status': 'NORMAL',
        })
        assert response.status_code in [200, 201]


class TestWorkOrderAPI:
    def test_list_work_orders(self, authed_client):
        response = authed_client.get('/api/v1/work-orders/')
        assert response.status_code == 200

    def test_create_work_order(self, authed_client, wb_laboratory, wb_semester):
        wb_semester.is_current = True
        wb_semester.save()
        response = authed_client.post('/api/v1/work-orders/', {
            'title': 'API创建工单',
            'description': '设备故障',
            'laboratory_id': wb_laboratory.id,
            'maintenance_type': 3,
        })
        assert response.status_code in [200, 201]


class TestNotificationAPI:
    def test_list_notifications(self, authed_client):
        response = authed_client.get('/api/v1/notifications/')
        assert response.status_code == 200

    def test_unread_count(self, authed_client):
        response = authed_client.get('/api/v1/notifications/unread-count/')
        assert response.status_code == 200


class TestEquipmentAPI:
    def test_list_equipment(self, authed_client):
        response = authed_client.get('/api/v1/equipments/')
        assert response.status_code == 200

    def test_create_equipment(self, authed_client, wb_laboratory):
        response = authed_client.post('/api/v1/equipments/', {
            'name': 'API创建设备',
            'code': 'API_EQ_001',
            'category': 'COMPUTER',
            'laboratory': wb_laboratory.id,
        })
        assert response.status_code in [200, 201]


class TestStatisticsAPI:
    def test_dashboard(self, authed_client):
        response = authed_client.get('/api/v1/statistics/dashboard/')
        assert response.status_code == 200

    def test_teacher_stats(self, teacher_client):
        response = teacher_client.get('/api/v1/statistics/teacher/')
        assert response.status_code == 200


class TestAuthFlow:
    def test_captcha_and_login(self, db, wb_teacher):
        client = APIClient()
        captcha_resp = client.get('/api/v1/auth/captcha/')
        assert captcha_resp.status_code == 200
        login_resp = client.post('/api/v1/auth/login/', {
            'username': wb_teacher.username,
            'password': 'WbTest@123456',
        })
        assert login_resp.status_code == 200
        assert 'access_token' in login_resp.data['data']

    def test_unauthenticated_denied(self, db):
        client = APIClient()
        response = client.get('/api/v1/users/')
        assert response.status_code in [401, 403]

    def test_change_password(self, authed_client):
        response = authed_client.post('/api/v1/auth/password/change/', {
            'old_pwd': 'WbTest@123456',
            'new_pwd': 'NewPass@123',
            'confirm_pwd': 'NewPass@123',
        })
        assert response.status_code == 200
