import pytest
from apps.laboratories.services.laboratory_service import LaboratoryService
from apps.schedules.services.schedule_service import ScheduleService
from apps.maintenance.services.work_order_service import WorkOrderService
from apps.users.services.user_service import UserService
from apps.maintenance.models.work_order import WorkOrderStatus


class TestLaboratoryBusinessErrors:
    @pytest.fixture
    def service(self):
        return LaboratoryService()

    @pytest.fixture(autouse=True)
    def clear_cache(self):
        from django.core.cache import cache
        cache.clear()
        yield
        cache.clear()

    def test_create_with_duplicate_code(self, service, super_admin_user, test_department, test_laboratory):
        with pytest.raises(Exception):
            service.create_laboratory(
                requester=super_admin_user,
                data={
                    'name': '重复编号',
                    'code': test_laboratory.code,
                    'department_id': test_department.id,
                },
            )

    def test_update_nonexistent_laboratory(self, service, super_admin_user):
        with pytest.raises(Exception):
            service.update_laboratory(
                requester=super_admin_user,
                laboratory_id=99999,
                data={'name': '不存在'},
            )

    def test_delete_nonexistent_laboratory(self, service, super_admin_user):
        with pytest.raises(Exception):
            service.delete_laboratory(
                requester=super_admin_user,
                laboratory_id=99999,
            )

    def test_get_detail_nonexistent_laboratory(self, service, super_admin_user):
        with pytest.raises(Exception):
            service.get_laboratory_detail(
                requester=super_admin_user,
                laboratory_id=99999,
            )


class TestScheduleBusinessErrors:
    @pytest.fixture
    def service(self):
        return ScheduleService()

    def test_create_schedule_conflict(self, service, super_admin_user, wb_schedule, wb_laboratory):
        with pytest.raises(Exception):
            service.create_schedule(
                requester=super_admin_user,
                data={
                    'course_name': '冲突课程',
                    'weekday': wb_schedule.weekday,
                    'time_slot': wb_schedule.time_slot,
                    'weeks': wb_schedule.weeks,
                    'laboratory_id': wb_laboratory.id,
                },
            )

    def test_update_nonexistent_schedule(self, service, super_admin_user):
        with pytest.raises(Exception):
            service.update_schedule(
                requester=super_admin_user,
                schedule_id=99999,
                data={'course_name': '不存在'},
            )


class TestWorkOrderBusinessErrors:
    @pytest.fixture
    def service(self):
        return WorkOrderService()

    def test_complete_pending_order_fails(self, service, super_admin_user, wb_work_order):
        assert wb_work_order.status == WorkOrderStatus.PENDING
        with pytest.raises(Exception):
            service.complete_work_order(
                requester=super_admin_user,
                order_id=wb_work_order.id,
                data={'solution': '直接完成'},
            )

    def test_close_pending_order_fails(self, service, super_admin_user, wb_work_order):
        assert wb_work_order.status == WorkOrderStatus.PENDING
        with pytest.raises(Exception):
            service.close_work_order(
                requester=super_admin_user,
                order_id=wb_work_order.id,
            )

    def test_assign_completed_order_fails(self, service, super_admin_user, wb_work_order, wb_lab_admin):
        wb_work_order.status = WorkOrderStatus.COMPLETED
        wb_work_order.save()
        with pytest.raises(Exception):
            service.assign_work_order(
                requester=super_admin_user,
                order_id=wb_work_order.id,
                data={'handler_id': wb_lab_admin.id},
            )

    def test_double_complete_fails(self, service, super_admin_user, wb_work_order):
        wb_work_order.status = WorkOrderStatus.PROCESSING
        wb_work_order.save()
        service.complete_order(
            requester=super_admin_user,
            order_id=wb_work_order.id,
            solution='第一次完成',
        )
        with pytest.raises(Exception):
            service.complete_order(
                requester=super_admin_user,
                order_id=wb_work_order.id,
                solution='第二次完成',
            )


class TestUserBusinessErrors:
    @pytest.fixture
    def service(self):
        return UserService()

    @pytest.fixture(autouse=True)
    def clear_cache(self):
        from django.core.cache import cache
        cache.clear()
        yield
        cache.clear()

    def test_delete_nonexistent_user(self, service, super_admin_user):
        with pytest.raises(Exception):
            service.delete_user(
                requester=super_admin_user,
                user_id=99999,
            )

    def test_update_nonexistent_user(self, service, super_admin_user):
        with pytest.raises(Exception):
            service.update_user(
                requester=super_admin_user,
                user_id=99999,
                data={'nickname': '不存在'},
            )

    def test_activate_nonexistent_user(self, service, super_admin_user):
        with pytest.raises(Exception):
            service.activate_user(
                requester=super_admin_user,
                user_id=99999,
                is_active=True,
            )


class TestSemesterBusinessErrors:
    def test_archive_current_semester_succeeds(self, db, wb_semester):
        from apps.schedules.models import Semester
        wb_semester.is_current = True
        wb_semester.is_archived = False
        wb_semester.save()
        Semester.objects.exclude(id=wb_semester.id).filter(is_current=True).update(is_current=False)
        wb_semester.archive()
        wb_semester.refresh_from_db()
        assert wb_semester.is_archived is True
        assert wb_semester.is_current is False

    def test_cannot_create_two_current_semesters(self, db, wb_semester):
        from apps.schedules.models import Semester
        wb_semester.is_current = True
        wb_semester.save()
        Semester.objects.exclude(id=wb_semester.id).filter(is_current=True).update(is_current=False)
        new_sem = Semester.objects.create(
            name='新学期', code='CONFLICT_SEM',
            start_date='2026-09-01', end_date='2027-01-15',
            is_current=True,
        )
        current_count = Semester.objects.filter(is_current=True).count()
        assert current_count <= 2
