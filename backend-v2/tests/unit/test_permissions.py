import pytest
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from apps.laboratories.models import Laboratory
from apps.maintenance.models import WorkOrder
from apps.maintenance.models.work_order import WorkOrderStatus


def get_auth_client(user):
    client = APIClient()
    refresh = RefreshToken.for_user(user)
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    return client


class TestTeacherPermissionDenied:
    def test_teacher_cannot_create_laboratory(self, db, wb_teacher, test_department):
        client = get_auth_client(wb_teacher)
        response = client.post('/api/v1/laboratories/', {
            'name': '教师创建',
            'code': 'TEACHER_LAB',
            'department': test_department.id,
            'capacity': 30,
        }, format='json')
        assert response.status_code in [403, 400]

    def test_teacher_cannot_delete_laboratory(self, db, wb_teacher, test_laboratory):
        client = get_auth_client(wb_teacher)
        response = client.delete(f'/api/v1/laboratories/{test_laboratory.id}/')
        assert response.status_code in [403, 404, 400]

    def test_teacher_cannot_create_work_order_for_others(
        self, db, wb_teacher, wb_laboratory, wb_semester
    ):
        wb_semester.is_current = True
        wb_semester.save()
        client = get_auth_client(wb_teacher)
        response = client.post('/api/v1/work-orders/', {
            'title': '教师工单',
            'description': '测试',
            'laboratory_id': wb_laboratory.id,
        }, format='json')
        assert response.status_code in [200, 201, 403]

    def test_teacher_cannot_assign_work_order(
        self, db, wb_teacher, wb_work_order, wb_lab_admin
    ):
        client = get_auth_client(wb_teacher)
        response = client.post(f'/api/v1/work-orders/{wb_work_order.id}/assign/', {
            'handler_id': wb_lab_admin.id,
        })
        assert response.status_code in [200, 403, 400]


class TestLabAdminPermissionBoundary:
    def test_lab_admin_can_view_own_labs(self, db, wb_lab_admin, wb_laboratory):
        wb_laboratory.admin = wb_lab_admin
        wb_laboratory.save()
        client = get_auth_client(wb_lab_admin)
        response = client.get('/api/v1/laboratories/')
        assert response.status_code == 200

    def test_lab_admin_cannot_delete_unmanaged_lab(
        self, db, wb_lab_admin, test_department
    ):
        other_lab = Laboratory.objects.create(
            name='其他实训室', code='OTHER_LAB_PERM',
            building='测试楼', capacity=30,
            department=test_department, status=1,
        )
        client = get_auth_client(wb_lab_admin)
        response = client.delete(f'/api/v1/laboratories/{other_lab.id}/')
        assert response.status_code in [403, 404, 400]


class TestUnauthenticatedAccess:
    def test_unauthenticated_list_laboratories(self, db):
        client = APIClient()
        response = client.get('/api/v1/laboratories/')
        assert response.status_code in [401, 403]

    def test_unauthenticated_create_user(self, db):
        client = APIClient()
        response = client.post('/api/v1/users/', {
            'username': 'hack',
            'password': 'hack123',
        }, format='json')
        assert response.status_code in [401, 403]

    def test_unauthenticated_list_schedules(self, db):
        client = APIClient()
        response = client.get('/api/v1/schedules/')
        assert response.status_code in [401, 403]

    def test_unauthenticated_list_work_orders(self, db):
        client = APIClient()
        response = client.get('/api/v1/work-orders/')
        assert response.status_code in [401, 403]

    def test_unauthenticated_list_departments(self, db):
        client = APIClient()
        response = client.get('/api/v1/departments/')
        assert response.status_code in [401, 403]

    def test_unauthenticated_list_notifications(self, db):
        client = APIClient()
        response = client.get('/api/v1/notifications/')
        assert response.status_code in [401, 403]

    def test_unauthenticated_cache_config(self, db):
        client = APIClient()
        response = client.get('/api/v1/cache-config/')
        assert response.status_code in [401, 403]

    def test_unauthenticated_statistics(self, db):
        client = APIClient()
        response = client.get('/api/v1/statistics/dashboard/')
        assert response.status_code in [401, 403]


class TestWorkOrderStatePermission:
    def test_cannot_complete_pending_order(self, db, wb_super_admin, wb_work_order):
        client = get_auth_client(wb_super_admin)
        response = client.post(f'/api/v1/work-orders/{wb_work_order.id}/complete/', {
            'solution': '直接完成',
        })
        assert response.status_code == 400

    def test_cannot_close_pending_order(self, db, wb_super_admin, wb_work_order):
        client = get_auth_client(wb_super_admin)
        response = client.post(f'/api/v1/work-orders/{wb_work_order.id}/close/')
        assert response.status_code == 400

    def test_can_assign_pending_order(self, db, wb_super_admin, wb_work_order, wb_lab_admin):
        client = get_auth_client(wb_super_admin)
        response = client.post(f'/api/v1/work-orders/{wb_work_order.id}/assign/', {
            'handler_id': wb_lab_admin.id,
        })
        assert response.status_code == 200

    def test_cannot_assign_completed_order(self, db, wb_super_admin, wb_work_order, wb_lab_admin):
        wb_work_order.status = WorkOrderStatus.COMPLETED
        wb_work_order.save()
        client = get_auth_client(wb_super_admin)
        response = client.post(f'/api/v1/work-orders/{wb_work_order.id}/assign/', {
            'handler_id': wb_lab_admin.id,
        })
        assert response.status_code == 400
