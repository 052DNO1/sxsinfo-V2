import pytest
from apps.maintenance.serializers.work_order import (
    WorkOrderSerializer, WorkOrderCreateSerializer, WorkOrderUpdateSerializer,
    WorkOrderAssignSerializer, WorkOrderCompleteSerializer, WorkOrderCloseSerializer
)


class TestWorkOrderCreateSerializer:
    def test_valid_data(self, db, wb_laboratory):
        data = {
            'title': '序列化器创建工单',
            'description': '设备故障描述',
            'laboratory_id': wb_laboratory.id,
            'maintenance_type': 3,
        }
        serializer = WorkOrderCreateSerializer(data=data)
        assert serializer.is_valid(), serializer.errors

    def test_empty_title(self, db):
        data = {'title': '', 'description': '描述', 'laboratory_id': 1}
        serializer = WorkOrderCreateSerializer(data=data)
        assert not serializer.is_valid()
        assert 'title' in serializer.errors

    def test_empty_description(self, db):
        data = {'title': '标题', 'description': '', 'laboratory_id': 1}
        serializer = WorkOrderCreateSerializer(data=data)
        assert not serializer.is_valid()
        assert 'description' in serializer.errors

    def test_missing_laboratory(self, db):
        data = {'title': '标题', 'description': '描述'}
        serializer = WorkOrderCreateSerializer(data=data)
        assert not serializer.is_valid()


class TestWorkOrderUpdateSerializer:
    def test_update_title(self, db, wb_work_order):
        data = {'title': '更新标题'}
        serializer = WorkOrderUpdateSerializer(instance=wb_work_order, data=data, partial=True)
        assert serializer.is_valid(), serializer.errors

    def test_update_description(self, db, wb_work_order):
        data = {'description': '更新描述'}
        serializer = WorkOrderUpdateSerializer(instance=wb_work_order, data=data, partial=True)
        assert serializer.is_valid(), serializer.errors


class TestWorkOrderAssignSerializer:
    def test_valid_data(self, db, wb_lab_admin):
        data = {'handler_id': wb_lab_admin.id}
        serializer = WorkOrderAssignSerializer(data=data)
        assert serializer.is_valid(), serializer.errors

    def test_missing_handler(self, db):
        data = {}
        serializer = WorkOrderAssignSerializer(data=data)
        assert not serializer.is_valid()


class TestWorkOrderCompleteSerializer:
    def test_valid_data(self, db):
        data = {'solution': '已修复设备'}
        serializer = WorkOrderCompleteSerializer(data=data)
        assert serializer.is_valid(), serializer.errors

    def test_empty_solution(self, db):
        data = {'solution': ''}
        serializer = WorkOrderCompleteSerializer(data=data)
        assert not serializer.is_valid()


class TestWorkOrderCloseSerializer:
    def test_valid_data(self, db):
        data = {'feedback': '满意'}
        serializer = WorkOrderCloseSerializer(data=data)
        assert serializer.is_valid(), serializer.errors

    def test_empty_feedback(self, db):
        data = {'feedback': ''}
        serializer = WorkOrderCloseSerializer(data=data)
        assert serializer.is_valid()


class TestWorkOrderSerializer:
    def test_includes_laboratory_info(self, db, wb_work_order):
        serializer = WorkOrderSerializer(wb_work_order)
        assert 'laboratory_name' in serializer.data

    def test_includes_status_display(self, db, wb_work_order):
        serializer = WorkOrderSerializer(wb_work_order)
        assert 'status' in serializer.data

    def test_includes_reporter_info(self, db, wb_work_order):
        serializer = WorkOrderSerializer(wb_work_order)
        assert 'reporter' in serializer.data
