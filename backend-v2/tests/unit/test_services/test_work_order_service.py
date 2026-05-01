import pytest
from apps.maintenance.services.work_order_service import WorkOrderService
from apps.maintenance.models import WorkOrder
from apps.core.exceptions import ValidationError


@pytest.fixture
def wo_service():
    return WorkOrderService()


class TestWorkOrderStateMachine:
    def test_assign_pending_to_processing(self, db, wb_super_admin, wb_work_order, wb_lab_admin):
        service = WorkOrderService()
        order = service.assign_order(wb_super_admin, wb_work_order.id, wb_lab_admin.id)
        assert order.status == 'PROCESSING'

    def test_assign_non_pending_fails(self, db, wb_super_admin, wb_work_order):
        wb_work_order.status = 'PROCESSING'
        wb_work_order.save()
        service = WorkOrderService()
        with pytest.raises(ValidationError):
            service.assign_order(wb_super_admin, wb_work_order.id, 1)

    def test_complete_processing(self, db, wb_super_admin, wb_work_order):
        wb_work_order.status = 'PROCESSING'
        wb_work_order.save()
        service = WorkOrderService()
        order = service.complete_order(wb_super_admin, wb_work_order.id, '已修复')
        assert order.status == 'COMPLETED'

    def test_complete_non_processing_fails(self, db, wb_super_admin, wb_work_order):
        service = WorkOrderService()
        with pytest.raises(ValidationError):
            service.complete_order(wb_super_admin, wb_work_order.id, 'test')

    def test_close_completed(self, db, wb_super_admin, wb_work_order):
        wb_work_order.status = 'COMPLETED'
        wb_work_order.save()
        service = WorkOrderService()
        order = service.close_order(wb_super_admin, wb_work_order.id, '满意')
        assert order.status == 'CLOSED'

    def test_close_non_completed_fails(self, db, wb_super_admin, wb_work_order):
        service = WorkOrderService()
        with pytest.raises(ValidationError):
            service.close_order(wb_super_admin, wb_work_order.id)

    def test_full_lifecycle(self, db, wb_super_admin, wb_work_order, wb_lab_admin):
        service = WorkOrderService()
        order = service.assign_order(wb_super_admin, wb_work_order.id, wb_lab_admin.id)
        assert order.status == 'PROCESSING'
        order = service.complete_order(wb_super_admin, wb_work_order.id, '修复完成')
        assert order.status == 'COMPLETED'
        order = service.close_order(wb_super_admin, wb_work_order.id, '很好')
        assert order.status == 'CLOSED'

    def test_delete_pending(self, db, wb_super_admin, wb_work_order):
        service = WorkOrderService()
        result = service.delete_work_order(wb_super_admin, wb_work_order.id)
        assert result is True

    def test_delete_processing_fails(self, db, wb_super_admin, wb_work_order):
        wb_work_order.status = 'PROCESSING'
        wb_work_order.save()
        service = WorkOrderService()
        with pytest.raises(ValidationError):
            service.delete_work_order(wb_super_admin, wb_work_order.id)

    def test_update_closed_fails(self, db, wb_super_admin, wb_work_order):
        wb_work_order.status = 'CLOSED'
        wb_work_order.save()
        service = WorkOrderService()
        with pytest.raises(ValidationError):
            service.update_work_order(wb_super_admin, wb_work_order.id, {'title': 'test'})
