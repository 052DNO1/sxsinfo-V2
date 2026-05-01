import pytest
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken


@pytest.fixture
def authed_client(db, wb_super_admin):
    client = APIClient()
    refresh = RefreshToken.for_user(wb_super_admin)
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    return client


class TestScheduleAPI:
    def test_create_schedule(self, authed_client, wb_laboratory, wb_semester, wb_teacher):
        response = authed_client.post('/api/v1/schedules/', {
            'course_name': 'API创建课程',
            'weekday': 3,
            'time_slot': '1-2',
            'weeks': '1-16',
            'laboratory': wb_laboratory.id,
            'teacher_name': wb_teacher.nickname,
        })
        assert response.status_code in [200, 201]

    def test_create_schedule_conflict(self, authed_client, wb_schedule):
        response = authed_client.post('/api/v1/schedules/', {
            'course_name': '冲突课程',
            'weekday': wb_schedule.weekday,
            'time_slot': wb_schedule.time_slot,
            'weeks': wb_schedule.weeks,
            'laboratory': wb_schedule.laboratory_id,
        })
        assert response.status_code == 400

    def test_update_schedule(self, authed_client, wb_schedule):
        response = authed_client.put(f'/api/v1/schedules/{wb_schedule.id}/', {
            'course_name': 'API更新课程',
            'weekday': wb_schedule.weekday,
            'time_slot': wb_schedule.time_slot,
            'weeks': wb_schedule.weeks,
            'laboratory': wb_schedule.laboratory_id,
        })
        assert response.status_code == 200

    def test_delete_schedule(self, authed_client, wb_schedule):
        response = authed_client.delete(f'/api/v1/schedules/{wb_schedule.id}/')
        assert response.status_code in [200, 204]

    def test_check_conflict(self, authed_client, wb_laboratory):
        response = authed_client.post('/api/v1/schedules/check_conflict/', {
            'laboratory_id': wb_laboratory.id,
            'weekday': 1,
            'time_slot': '1-2',
            'weeks': '1-16',
        })
        assert response.status_code == 200


class TestWorkOrderAPI:
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

    def test_assign_work_order(self, authed_client, wb_work_order, wb_lab_admin):
        response = authed_client.post(f'/api/v1/work-orders/{wb_work_order.id}/assign/', {
            'handler_id': wb_lab_admin.id,
        })
        assert response.status_code == 200

    def test_complete_work_order_not_processing(self, authed_client, wb_work_order):
        response = authed_client.post(f'/api/v1/work-orders/{wb_work_order.id}/complete/', {
            'solution': '已修复',
        })
        assert response.status_code == 400
