import pytest
from apps.maintenance.services.work_order_service import WorkOrderService
from apps.maintenance.models import WorkOrder
from apps.core.exceptions import ValidationError


class TestWorkOrderFullLifecycle:
    def test_pending_to_closed(self, db, wb_super_admin, wb_work_order, wb_lab_admin):
        service = WorkOrderService()
        order = service.assign_order(wb_super_admin, wb_work_order.id, wb_lab_admin.id)
        assert order.status == 'PROCESSING'
        order = service.complete_order(wb_super_admin, wb_work_order.id, '修复完成')
        assert order.status == 'COMPLETED'
        order = service.close_order(wb_super_admin, wb_work_order.id, '满意')
        assert order.status == 'CLOSED'

    def test_create_assign_complete_close_delete(self, db, wb_super_admin, wb_laboratory, wb_semester, wb_teacher, wb_lab_admin):
        service = WorkOrderService()
        wb_semester.is_current = True
        wb_semester.save()
        order = service.create_work_order(
            requester=wb_teacher,
            data={
                'title': '集成测试工单',
                'description': '设备故障',
                'laboratory_id': wb_laboratory.id,
                'maintenance_type': 3,
            },
        )
        assert order.status == 'PENDING'

        order = service.assign_order(wb_super_admin, order.id, wb_lab_admin.id)
        assert order.status == 'PROCESSING'

        order = service.complete_order(wb_super_admin, order.id, '已修复')
        assert order.status == 'COMPLETED'

        order = service.close_order(wb_super_admin, order.id, '很好')
        assert order.status == 'CLOSED'

        result = service.delete_work_order(wb_super_admin, order.id)
        assert result is True

    def test_invalid_transitions(self, db, wb_super_admin, wb_work_order):
        service = WorkOrderService()
        with pytest.raises(ValidationError):
            service.complete_order(wb_super_admin, wb_work_order.id, 'test')
        with pytest.raises(ValidationError):
            service.close_order(wb_super_admin, wb_work_order.id)
