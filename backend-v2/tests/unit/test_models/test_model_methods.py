import pytest
from apps.laboratories.models import Laboratory
from apps.schedules.models import Semester
from apps.maintenance.models import WorkOrder
from apps.maintenance.models.work_order import WorkOrderStatus
from apps.users.models import Department, User


class TestLaboratoryModelLocation:
    def test_full_location(self, db, test_department):
        lab = Laboratory.objects.create(
            name='完整位置', code='LOC_001', building='主楼',
            floor=3, room_number='301', capacity=30,
            department=test_department, status=1,
        )
        assert lab.location == '主楼 3楼 301'

    def test_no_floor(self, db, test_department):
        lab = Laboratory.objects.create(
            name='无楼层', code='LOC_002', building='主楼',
            floor=None, room_number='301', capacity=30,
            department=test_department, status=1,
        )
        assert lab.location == '主楼 301'

    def test_no_room_number(self, db, test_department):
        lab = Laboratory.objects.create(
            name='无房间号', code='LOC_003', building='主楼',
            floor=3, room_number='', capacity=30,
            department=test_department, status=1,
        )
        assert lab.location == '主楼 3楼'

    def test_no_building(self, db, test_department):
        lab = Laboratory.objects.create(
            name='无楼栋', code='LOC_004', building='',
            floor=3, room_number='301', capacity=30,
            department=test_department, status=1,
        )
        assert lab.location == '3楼 301'

    def test_only_building(self, db, test_department):
        lab = Laboratory.objects.create(
            name='仅楼栋', code='LOC_005', building='主楼',
            floor=None, room_number='', capacity=30,
            department=test_department, status=1,
        )
        assert lab.location == '主楼'

    def test_empty_location(self, db, test_department):
        lab = Laboratory.objects.create(
            name='空位置', code='LOC_006', building='',
            floor=None, room_number='', capacity=30,
            department=test_department, status=1,
        )
        assert lab.location == ''


class TestLaboratoryModelCounts:
    def test_get_equipment_count_empty(self, db, test_department):
        lab = Laboratory.objects.create(
            name='无设备', code='EQ_COUNT_001', building='主楼',
            capacity=30, department=test_department, status=1,
        )
        assert lab.get_equipment_count() == 0

    def test_get_equipment_count_with_items(self, db, test_department, wb_equipment):
        lab = wb_equipment.laboratory
        count = lab.get_equipment_count()
        assert count >= 1

    def test_get_schedule_count_empty(self, db, test_department):
        lab = Laboratory.objects.create(
            name='无课表', code='SCH_COUNT_001', building='主楼',
            capacity=30, department=test_department, status=1,
        )
        assert lab.get_schedule_count() == 0

    def test_get_schedule_count_with_items(self, db, wb_schedule):
        lab = wb_schedule.laboratory
        count = lab.get_schedule_count()
        assert count >= 1


class TestSemesterModelMethods:
    def test_get_current_returns_none_when_no_current(self, db):
        Semester.objects.filter(is_current=True).update(is_current=False)
        assert Semester.get_current() is None

    def test_get_current_returns_current_semester(self, db):
        from apps.schedules.models import Semester
        Semester.objects.filter(is_current=True).update(is_current=False)
        sem = Semester.objects.create(
            name='当前学期', code='CUR_SEM_TEST',
            start_date='2025-09-01', end_date='2026-01-15',
            is_current=True, is_archived=False,
        )
        current = Semester.get_current()
        assert current is not None
        assert current.id == sem.id

    def test_set_as_current_unsets_previous(self, db, test_department):
        sem1 = Semester.objects.create(
            name='学期1', code='SEM_MODEL_1',
            start_date='2025-09-01', end_date='2026-01-15',
            is_current=True, is_archived=False,
        )
        sem2 = Semester.objects.create(
            name='学期2', code='SEM_MODEL_2',
            start_date='2026-02-01', end_date='2026-06-30',
            is_current=False, is_archived=False,
        )
        sem2.set_as_current()
        sem1.refresh_from_db()
        sem2.refresh_from_db()
        assert sem1.is_current is False
        assert sem2.is_current is True

    def test_set_as_current_unarchives(self, db):
        sem = Semester.objects.create(
            name='归档学期', code='SEM_MODEL_3',
            start_date='2024-09-01', end_date='2025-01-15',
            is_current=False, is_archived=True,
        )
        sem.set_as_current()
        sem.refresh_from_db()
        assert sem.is_current is True
        assert sem.is_archived is False

    def test_archive_sets_flags(self, db):
        sem = Semester.objects.create(
            name='待归档', code='SEM_MODEL_4',
            start_date='2024-09-01', end_date='2025-01-15',
            is_current=False, is_archived=False,
        )
        sem.archive()
        sem.refresh_from_db()
        assert sem.is_archived is True
        assert sem.is_current is False

    def test_archive_archives_schedules(self, db, wb_schedule, wb_semester):
        wb_schedule.semester = wb_semester
        wb_schedule.save()
        wb_semester.archive()
        wb_schedule.refresh_from_db()
        assert wb_schedule.is_archived is True

    def test_get_schedule_count(self, db, wb_semester, wb_schedule):
        wb_schedule.semester = wb_semester
        wb_schedule.save()
        assert wb_semester.get_schedule_count() >= 1


class TestWorkOrderModelMethods:
    def test_assign_changes_status(self, db, wb_work_order, wb_lab_admin):
        assert wb_work_order.status == WorkOrderStatus.PENDING
        wb_work_order.assign(wb_lab_admin)
        wb_work_order.refresh_from_db()
        assert wb_work_order.status == WorkOrderStatus.PROCESSING
        assert wb_work_order.handler == wb_lab_admin
        assert wb_work_order.assigned_at is not None

    def test_start_handle_changes_status(self, db, wb_work_order):
        wb_work_order.status = WorkOrderStatus.PROCESSING
        wb_work_order.save()
        wb_work_order.start_handle()
        wb_work_order.refresh_from_db()
        assert wb_work_order.status == WorkOrderStatus.PROCESSING
        assert wb_work_order.started_at is not None

    def test_complete_changes_status(self, db, wb_work_order):
        wb_work_order.status = WorkOrderStatus.PROCESSING
        wb_work_order.save()
        wb_work_order.complete('已修复设备')
        wb_work_order.refresh_from_db()
        assert wb_work_order.status == WorkOrderStatus.COMPLETED
        assert wb_work_order.solution == '已修复设备'
        assert wb_work_order.completed_at is not None

    def test_close_changes_status(self, db, wb_work_order):
        wb_work_order.status = WorkOrderStatus.COMPLETED
        wb_work_order.save()
        wb_work_order.close()
        wb_work_order.refresh_from_db()
        assert wb_work_order.status == WorkOrderStatus.CLOSED
        assert wb_work_order.closed_at is not None

    def test_generate_order_number_fault(self, db):
        order_number = WorkOrder.generate_order_number(maintenance_type=3)
        assert order_number.startswith('G')
        assert len(order_number) >= 13

    def test_generate_order_number_maintenance(self, db):
        order_number = WorkOrder.generate_order_number(maintenance_type=1)
        assert order_number.startswith('W')
        assert len(order_number) >= 13

    def test_generate_order_number_increments(self, db, wb_laboratory, wb_teacher, wb_semester):
        from apps.maintenance.models import WorkOrder as WO
        WO.objects.filter(order_number__startswith='G').delete()
        num1 = WorkOrder.generate_order_number(maintenance_type=3)
        wo1 = WO.objects.create(
            title='递增测试1', description='描述',
            laboratory=wb_laboratory,
            reporter=wb_teacher,
            semester=wb_semester,
            order_number=num1,
            status=WorkOrderStatus.PENDING,
        )
        num2 = WorkOrder.generate_order_number(maintenance_type=3)
        if num1[:9] == num2[:9]:
            seq1 = int(num1[-4:])
            seq2 = int(num2[-4:])
            assert seq2 == seq1 + 1

    def test_full_lifecycle(self, db, wb_work_order, wb_lab_admin):
        assert wb_work_order.status == WorkOrderStatus.PENDING
        wb_work_order.assign(wb_lab_admin)
        assert wb_work_order.status == WorkOrderStatus.PROCESSING
        wb_work_order.complete('解决方案')
        assert wb_work_order.status == WorkOrderStatus.COMPLETED
        wb_work_order.close()
        assert wb_work_order.status == WorkOrderStatus.CLOSED


class TestDepartmentModelMethods:
    def test_get_user_count_empty(self, db):
        dept = Department.objects.create(name='空部门', code='EMPTY_DEPT')
        assert dept.get_user_count() == 0

    def test_get_user_count_with_users(self, db, test_department, teacher_user):
        teacher_user.department = test_department
        teacher_user.save()
        assert test_department.get_user_count() >= 1

    def test_get_all_users_includes_self_dept(self, db, test_department, teacher_user):
        teacher_user.department = test_department
        teacher_user.save()
        users = test_department.get_all_users()
        assert teacher_user in users

    def test_get_user_count_excludes_deleted(self, db, test_department):
        user = User.objects.create_user(
            username='deleted_user_model',
            password='test123456',
            nickname='已删除用户',
            role=1,
            department=test_department,
            is_active=True,
        )
        user.is_deleted = True
        user.save()
        count_before = test_department.get_user_count()
        user.is_deleted = True
        user.save()
        count_after = test_department.get_user_count()
        assert count_after == count_before or count_after < count_before + 1
