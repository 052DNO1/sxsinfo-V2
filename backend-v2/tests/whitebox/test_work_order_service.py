import pytest
from apps.maintenance.services.work_order_service import WorkOrderService
from apps.maintenance.models import WorkOrder
from apps.core.exceptions import ValidationError, NotFoundError, PermissionDenied
from apps.core.constants import WorkOrderStatus, MaintenanceType


@pytest.fixture
def wo_service():
    return WorkOrderService()


class TestWorkOrderServiceCreate:
    def test_create_success(self, db, wb_lab_admin, wb_laboratory, wb_semester):
        wb_semester.is_current = True
        wb_semester.save()
        service = WorkOrderService()
        order = service.create_work_order(
            requester=wb_lab_admin,
            data={
                'title': '白盒创建工单',
                'description': '设备故障描述',
                'laboratory_id': wb_laboratory.id,
                'maintenance_type': MaintenanceType.REPAIR,
            },
        )
        assert order.title == '白盒创建工单'
        assert order.status == WorkOrderStatus.PENDING

    def test_create_no_laboratory(self, db, wb_lab_admin):
        service = WorkOrderService()
        with pytest.raises(ValidationError, match='实训室为必填项'):
            service.create_work_order(
                requester=wb_lab_admin,
                data={'title': '测试', 'description': '描述'},
            )

    def test_create_no_title(self, db, wb_lab_admin, wb_laboratory, wb_semester):
        service = WorkOrderService()
        with pytest.raises(ValidationError, match='工单标题为必填项'):
            service.create_work_order(
                requester=wb_lab_admin,
                data={
                    'description': '描述',
                    'laboratory_id': wb_laboratory.id,
                },
            )

    def test_create_no_description(self, db, wb_lab_admin, wb_laboratory, wb_semester):
        service = WorkOrderService()
        with pytest.raises(ValidationError, match='问题描述为必填项'):
            service.create_work_order(
                requester=wb_lab_admin,
                data={
                    'title': '标题',
                    'laboratory_id': wb_laboratory.id,
                },
            )


class TestWorkOrderServiceStateMachine:
    def test_assign_pending_to_processing(self, db, wb_super_admin, wb_work_order, wb_lab_admin):
        service = WorkOrderService()
        order = service.assign_order(
            requester=wb_super_admin,
            order_id=wb_work_order.id,
            handler_id=wb_lab_admin.id,
        )
        assert order.status == WorkOrderStatus.PROCESSING

    def test_assign_non_pending_fails(self, db, wb_super_admin, wb_work_order):
        wb_work_order.status = WorkOrderStatus.PROCESSING
        wb_work_order.save()
        service = WorkOrderService()
        with pytest.raises(ValidationError, match='只能分配待处理的工单'):
            service.assign_order(
                requester=wb_super_admin,
                order_id=wb_work_order.id,
                handler_id=1,
            )

    def test_start_handle_pending(self, db, wb_super_admin, wb_work_order):
        service = WorkOrderService()
        order = service.start_handle(
            requester=wb_super_admin,
            order_id=wb_work_order.id,
        )
        assert order.status == WorkOrderStatus.PROCESSING

    def test_complete_processing(self, db, wb_super_admin, wb_work_order):
        wb_work_order.status = WorkOrderStatus.PROCESSING
        wb_work_order.save()
        service = WorkOrderService()
        order = service.complete_order(
            requester=wb_super_admin,
            order_id=wb_work_order.id,
            solution='已修复',
        )
        assert order.status == WorkOrderStatus.COMPLETED
        assert order.solution == '已修复'

    def test_complete_non_processing_fails(self, db, wb_super_admin, wb_work_order):
        service = WorkOrderService()
        with pytest.raises(ValidationError, match='只能完成处理中的工单'):
            service.complete_order(
                requester=wb_super_admin,
                order_id=wb_work_order.id,
                solution='test',
            )

    def test_close_completed(self, db, wb_super_admin, wb_work_order):
        wb_work_order.status = WorkOrderStatus.COMPLETED
        wb_work_order.save()
        service = WorkOrderService()
        order = service.close_order(
            requester=wb_super_admin,
            order_id=wb_work_order.id,
            feedback='满意',
        )
        assert order.status == WorkOrderStatus.CLOSED
        assert order.feedback == '满意'

    def test_close_non_completed_fails(self, db, wb_super_admin, wb_work_order):
        service = WorkOrderService()
        with pytest.raises(ValidationError, match='只能关闭已完成的工单'):
            service.close_order(
                requester=wb_super_admin,
                order_id=wb_work_order.id,
            )

    def test_full_lifecycle(self, db, wb_super_admin, wb_work_order, wb_lab_admin):
        service = WorkOrderService()
        order = service.assign_order(
            requester=wb_super_admin,
            order_id=wb_work_order.id,
            handler_id=wb_lab_admin.id,
        )
        assert order.status == WorkOrderStatus.PROCESSING

        order = service.complete_order(
            requester=wb_super_admin,
            order_id=wb_work_order.id,
            solution='修复完成',
        )
        assert order.status == WorkOrderStatus.COMPLETED

        order = service.close_order(
            requester=wb_super_admin,
            order_id=wb_work_order.id,
            feedback='很好',
        )
        assert order.status == WorkOrderStatus.CLOSED


class TestWorkOrderServiceUpdate:
    def test_update_pending(self, db, wb_super_admin, wb_work_order):
        service = WorkOrderService()
        order = service.update_work_order(
            requester=wb_super_admin,
            order_id=wb_work_order.id,
            data={'title': '更新标题'},
        )
        assert order.title == '更新标题'

    def test_update_closed_fails(self, db, wb_super_admin, wb_work_order):
        wb_work_order.status = WorkOrderStatus.CLOSED
        wb_work_order.save()
        service = WorkOrderService()
        with pytest.raises(ValidationError, match='工单已关闭，无法修改'):
            service.update_work_order(
                requester=wb_super_admin,
                order_id=wb_work_order.id,
                data={'title': '尝试修改'},
            )


class TestWorkOrderServiceDelete:
    def test_delete_pending(self, db, wb_super_admin, wb_work_order):
        service = WorkOrderService()
        result = service.delete_work_order(
            requester=wb_super_admin,
            order_id=wb_work_order.id,
        )
        assert result is True

    def test_delete_closed(self, db, wb_super_admin, wb_work_order):
        wb_work_order.status = WorkOrderStatus.CLOSED
        wb_work_order.save()
        service = WorkOrderService()
        result = service.delete_work_order(
            requester=wb_super_admin,
            order_id=wb_work_order.id,
        )
        assert result is True

    def test_delete_processing_fails(self, db, wb_super_admin, wb_work_order):
        wb_work_order.status = WorkOrderStatus.PROCESSING
        wb_work_order.save()
        service = WorkOrderService()
        with pytest.raises(ValidationError, match='只能删除待处理或已关闭的工单'):
            service.delete_work_order(
                requester=wb_super_admin,
                order_id=wb_work_order.id,
            )

    def test_delete_completed_fails(self, db, wb_super_admin, wb_work_order):
        wb_work_order.status = WorkOrderStatus.COMPLETED
        wb_work_order.save()
        service = WorkOrderService()
        with pytest.raises(ValidationError, match='只能删除待处理或已关闭的工单'):
            service.delete_work_order(
                requester=wb_super_admin,
                order_id=wb_work_order.id,
            )

    def test_delete_archived_soft_delete(self, db, wb_super_admin, wb_work_order):
        wb_work_order.is_archived = True
        wb_work_order.save()
        service = WorkOrderService()
        result = service.delete_work_order(
            requester=wb_super_admin,
            order_id=wb_work_order.id,
        )
        assert result is True
        wb_work_order.refresh_from_db()
        assert wb_work_order.is_deleted is True
