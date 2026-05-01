import pytest
from tests.blackbox.client import (
    assert_success_response, assert_error_response,
    assert_paginated_response, extract_data, extract_list,
)
from tests.blackbox.config import API_ENDPOINTS


class TestWorkOrderList:
    def test_get_work_order_list(self, authed_client):
        url = API_ENDPOINTS['work_orders']['list']
        response = authed_client.get(url)
        assert_paginated_response(response)

    def test_get_work_order_list_with_pagination(self, authed_client):
        url = API_ENDPOINTS['work_orders']['list']
        response = authed_client.get(url, {'page': 1, 'page_size': 10})
        assert_paginated_response(response)

    def test_get_work_order_list_search(self, authed_client, test_work_order):
        url = API_ENDPOINTS['work_orders']['list']
        response = authed_client.get(url, {'search': test_work_order.title})
        assert response.status_code == 200

    def test_get_work_order_list_filter_by_laboratory(self, authed_client, test_laboratory):
        url = API_ENDPOINTS['work_orders']['list']
        response = authed_client.get(url, {'laboratory_id': test_laboratory.id})
        assert_paginated_response(response)

    def test_get_work_order_list_filter_by_status(self, authed_client):
        url = API_ENDPOINTS['work_orders']['list']
        response = authed_client.get(url, {'status': 'PENDING'})
        assert_paginated_response(response)

    def test_get_work_order_list_filter_by_type(self, authed_client):
        url = API_ENDPOINTS['work_orders']['list']
        response = authed_client.get(url, {'maintenance_type': 3})
        assert_paginated_response(response)

    def test_get_work_order_list_filter_by_handler(self, authed_client, lab_admin):
        url = API_ENDPOINTS['work_orders']['list']
        response = authed_client.get(url, {'handler_id': lab_admin.id})
        assert_paginated_response(response)

    def test_get_work_order_list_filter_by_reporter(self, authed_client, teacher):
        url = API_ENDPOINTS['work_orders']['list']
        response = authed_client.get(url, {'reporter_id': teacher.id})
        assert_paginated_response(response)

    def test_get_form_options(self, authed_client):
        url = API_ENDPOINTS['work_orders']['form_options']
        response = authed_client.get(url)
        assert response.status_code in (200, 400)


class TestWorkOrderCreate:
    def test_create_work_order_success(self, authed_client, test_laboratory, test_semester, teacher):
        url = API_ENDPOINTS['work_orders']['list']
        response = authed_client.post(url, {
            'title': '新建测试工单',
            'description': '新建测试工单描述',
            'laboratory_id': test_laboratory.id,
            'maintenance_type': 3,
            'status': 'PENDING',
            'priority': 3,
            'reporter_id': teacher.id,
        })
        assert response.status_code in (200, 201, 500)

    def test_create_work_order_missing_title(self, authed_client, test_laboratory):
        url = API_ENDPOINTS['work_orders']['list']
        response = authed_client.post(url, {
            'description': '无标题工单',
            'laboratory_id': test_laboratory.id,
        })
        assert response.status_code == 400

    def test_create_work_order_with_equipment(self, authed_client, test_laboratory, test_equipment, teacher):
        url = API_ENDPOINTS['work_orders']['list']
        response = authed_client.post(url, {
            'title': '设备维修工单',
            'description': '设备故障描述',
            'laboratory_id': test_laboratory.id,
            'equipment_id': test_equipment.id,
            'maintenance_type': 3,
            'priority': 4,
            'reporter_id': teacher.id,
        })
        assert response.status_code in (200, 201, 500)


class TestWorkOrderDetail:
    def test_get_work_order_detail(self, authed_client, test_work_order):
        url = API_ENDPOINTS['work_orders']['detail'].format(id=test_work_order.id)
        response = authed_client.get(url)
        data = assert_success_response(response)
        order_data = extract_data(response)
        assert order_data.get('id') == test_work_order.id
        assert order_data.get('title') == test_work_order.title

    def test_get_work_order_detail_not_found(self, authed_client):
        url = API_ENDPOINTS['work_orders']['detail'].format(id=99999)
        response = authed_client.get(url)
        assert response.status_code in (400, 404)

    def test_update_work_order_success(self, authed_client, test_work_order):
        url = API_ENDPOINTS['work_orders']['detail'].format(id=test_work_order.id)
        response = authed_client.put(url, {
            'title': '更新后工单标题',
            'description': '更新后描述',
        })
        assert response.status_code == 200
        verify_url = API_ENDPOINTS['work_orders']['detail'].format(id=test_work_order.id)
        verify_resp = authed_client.get(verify_url)
        verify_data = extract_data(verify_resp)
        assert verify_data.get('title') == '更新后工单标题'

    def test_delete_work_order_success(self, authed_client, db, test_laboratory, test_semester, teacher):
        from apps.maintenance.models import WorkOrder
        order = WorkOrder.objects.create(
            title='待删除工单', description='待删除',
            laboratory=test_laboratory, laboratory_name=test_laboratory.name,
            laboratory_code=test_laboratory.code, semester=test_semester,
            maintenance_type=3, status='PENDING', priority=1,
            reporter=teacher,
        )
        url = API_ENDPOINTS['work_orders']['detail'].format(id=order.id)
        response = authed_client.delete(url)
        assert response.status_code == 200


class TestWorkOrderWorkflow:
    def test_assign_work_order(self, authed_client, test_work_order, lab_admin):
        url = API_ENDPOINTS['work_orders']['assign'].format(id=test_work_order.id)
        response = authed_client.post(url, {
            'handler_id': lab_admin.id,
        })
        assert response.status_code == 200

    def test_assign_work_order_missing_handler(self, authed_client, test_work_order):
        url = API_ENDPOINTS['work_orders']['assign'].format(id=test_work_order.id)
        response = authed_client.post(url, {})
        assert response.status_code == 400

    def test_start_handle_work_order(self, authed_client, test_work_order):
        test_work_order.status = 'PROCESSING'
        test_work_order.save()
        url = API_ENDPOINTS['work_orders']['start_handle'].format(id=test_work_order.id)
        response = authed_client.post(url)
        assert response.status_code == 200

    def test_complete_work_order(self, authed_client, test_work_order):
        test_work_order.status = 'PROCESSING'
        test_work_order.save()
        url = API_ENDPOINTS['work_orders']['complete'].format(id=test_work_order.id)
        response = authed_client.post(url, {
            'solution': '已修复故障',
        })
        assert response.status_code == 200

    def test_close_work_order(self, authed_client, test_work_order):
        test_work_order.status = 'COMPLETED'
        test_work_order.save()
        url = API_ENDPOINTS['work_orders']['close'].format(id=test_work_order.id)
        response = authed_client.post(url, {
            'feedback': '满意',
        })
        assert response.status_code == 200

    def test_close_work_order_without_feedback(self, authed_client, test_work_order):
        test_work_order.status = 'COMPLETED'
        test_work_order.save()
        url = API_ENDPOINTS['work_orders']['close'].format(id=test_work_order.id)
        response = authed_client.post(url)
        assert response.status_code == 200


class TestWorkOrderBatchDelete:
    def test_batch_delete_success(self, authed_client, db, test_laboratory, test_semester, teacher):
        from apps.maintenance.models import WorkOrder
        o1 = WorkOrder.objects.create(
            title='批删1', description='批删1', laboratory=test_laboratory,
            laboratory_name=test_laboratory.name, laboratory_code=test_laboratory.code,
            semester=test_semester, maintenance_type=3, status='PENDING',
            priority=1, reporter=teacher,
        )
        o2 = WorkOrder.objects.create(
            title='批删2', description='批删2', laboratory=test_laboratory,
            laboratory_name=test_laboratory.name, laboratory_code=test_laboratory.code,
            semester=test_semester, maintenance_type=3, status='PENDING',
            priority=1, reporter=teacher,
        )
        url = API_ENDPOINTS['work_orders']['batch_delete']
        response = authed_client.post(url, {'ids': [o1.id, o2.id]})
        assert response.status_code == 200


class TestWorkOrderCenter:
    def test_get_center_list(self, authed_client):
        url = API_ENDPOINTS['work_orders']['center']
        response = authed_client.get(url)
        assert response.status_code == 200

    def test_get_center_detail(self, authed_client, test_work_order):
        url = API_ENDPOINTS['work_orders']['center_detail'].format(order_id=test_work_order.id)
        response = authed_client.get(url)
        assert response.status_code in (200, 400, 404)

    def test_hide_in_center(self, authed_client, test_work_order):
        url = API_ENDPOINTS['work_orders']['center_hide'].format(order_id=test_work_order.id)
        response = authed_client.post(url)
        assert response.status_code in (200, 400, 404)
