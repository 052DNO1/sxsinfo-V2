import pytest
import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lims.settings.testing')
django.setup()

from django.contrib.auth import get_user_model
from apps.core.constants import UserRole, UserStatus

User = get_user_model()

WB_DEFAULT_PASSWORD = 'WbTest@123456'


@pytest.fixture
def wb_db(db):
    return db


@pytest.fixture
def wb_department(db):
    from apps.users.models import Department
    return Department.objects.create(
        name='白盒测试分院',
        code='WB_DEPT',
    )


@pytest.fixture
def wb_department_child(db, wb_department):
    from apps.users.models import Department
    return Department.objects.create(
        name='白盒测试子分院',
        code='WB_DEPT_CHILD',
        parent=wb_department,
    )


@pytest.fixture
def wb_system_admin(db):
    return User.objects.create_user(
        username='wb_sys_admin',
        password=WB_DEFAULT_PASSWORD,
        nickname='白盒系统管理员',
        email='wb_sys@test.com',
        is_superuser=True,
        role=UserRole.SYSTEM_ADMIN,
        is_active=True,
    )


@pytest.fixture
def wb_super_admin(db, wb_department):
    return User.objects.create_user(
        username='wb_super_admin',
        password=WB_DEFAULT_PASSWORD,
        nickname='白盒超级管理员',
        email='wb_super@test.com',
        is_superuser=False,
        role=UserRole.SUPER_ADMIN,
        department=wb_department,
        is_active=True,
    )


@pytest.fixture
def wb_dept_admin(db, wb_department):
    return User.objects.create_user(
        username='wb_dept_admin',
        password=WB_DEFAULT_PASSWORD,
        nickname='白盒分院管理员',
        email='wb_dept@test.com',
        is_superuser=False,
        role=UserRole.DEPARTMENT_ADMIN,
        department=wb_department,
        is_active=True,
    )


@pytest.fixture
def wb_lab_admin(db, wb_department):
    return User.objects.create_user(
        username='wb_lab_admin',
        password=WB_DEFAULT_PASSWORD,
        nickname='白盒实训室管理员',
        email='wb_lab@test.com',
        is_superuser=False,
        role=UserRole.LABORATORY_ADMIN,
        department=wb_department,
        is_active=True,
    )


@pytest.fixture
def wb_teacher(db, wb_department):
    return User.objects.create_user(
        username='wb_teacher',
        password=WB_DEFAULT_PASSWORD,
        nickname='白盒教师',
        email='wb_teacher@test.com',
        is_superuser=False,
        role=UserRole.TEACHER,
        department=wb_department,
        is_active=True,
    )


@pytest.fixture
def wb_inactive_user(db, wb_department):
    return User.objects.create_user(
        username='wb_inactive',
        password=WB_DEFAULT_PASSWORD,
        nickname='白盒停用用户',
        email='wb_inactive@test.com',
        is_superuser=False,
        role=UserRole.TEACHER,
        department=wb_department,
        is_active=False,
    )


@pytest.fixture
def wb_laboratory(db, wb_department, wb_lab_admin):
    from apps.laboratories.models import Laboratory
    return Laboratory.objects.create(
        name='白盒测试实训室',
        code='WB_LAB_001',
        building='白盒测试楼',
        floor=3,
        room_number='301',
        capacity=30,
        area=100.5,
        laboratory_type='COMPUTER',
        department=wb_department,
        admin=wb_lab_admin,
        status=1,
    )


@pytest.fixture
def wb_laboratory2(db, wb_department, wb_lab_admin):
    from apps.laboratories.models import Laboratory
    return Laboratory.objects.create(
        name='白盒测试实训室2',
        code='WB_LAB_002',
        building='白盒测试楼',
        floor=3,
        room_number='302',
        capacity=50,
        area=150.0,
        laboratory_type='COMPUTER',
        department=wb_department,
        admin=wb_lab_admin,
        status=1,
    )


@pytest.fixture
def wb_equipment(db, wb_laboratory):
    from apps.laboratories.models import Equipment
    return Equipment.objects.create(
        name='白盒测试设备',
        code='WB_EQ_001',
        category='COMPUTER',
        brand='测试品牌',
        model='WB-Model',
        laboratory=wb_laboratory,
        status='NORMAL',
    )


@pytest.fixture
def wb_semester(db):
    from apps.schedules.models import Semester
    return Semester.objects.create(
        name='白盒测试学期2025-2026-1',
        code='WB_2025_2026_1',
        start_date='2025-09-01',
        end_date='2026-01-15',
        is_current=True,
        total_weeks=20,
    )


@pytest.fixture
def wb_semester_not_current(db):
    from apps.schedules.models import Semester
    return Semester.objects.create(
        name='白盒测试学期2024-2025-2',
        code='WB_2024_2025_2',
        start_date='2025-02-01',
        end_date='2025-06-30',
        is_current=False,
        total_weeks=18,
    )


@pytest.fixture
def wb_schedule(db, wb_laboratory, wb_semester, wb_teacher):
    from apps.schedules.models import Schedule
    return Schedule.objects.create(
        course_name='白盒测试课程',
        course_code='WB_COURSE_001',
        weekday=1,
        time_slot='1-2',
        weeks='1-16',
        laboratory=wb_laboratory,
        semester=wb_semester,
        teacher=wb_teacher,
        teacher_name=wb_teacher.nickname,
        class_name='白盒测试班级',
        student_count=40,
        is_active=True,
    )


@pytest.fixture
def wb_usage_record(db, wb_laboratory, wb_semester, wb_teacher):
    from apps.records.models import UsageRecord
    return UsageRecord.objects.create(
        usage_date='2025-10-15',
        time_slot='1-2',
        class_hours=2,
        laboratory=wb_laboratory,
        laboratory_name=wb_laboratory.name,
        laboratory_code=wb_laboratory.code,
        semester=wb_semester,
        teacher=wb_teacher,
        class_name='白盒测试班级',
        student_count=40,
        content='白盒测试课程内容',
        device_status='NORMAL',
        laboratory_status='NORMAL',
    )


@pytest.fixture
def wb_work_order(db, wb_laboratory, wb_semester, wb_teacher, wb_lab_admin):
    from apps.maintenance.models import WorkOrder
    return WorkOrder.objects.create(
        title='白盒测试工单',
        description='白盒测试工单描述',
        laboratory=wb_laboratory,
        laboratory_name=wb_laboratory.name,
        laboratory_code=wb_laboratory.code,
        semester=wb_semester,
        maintenance_type=3,
        status='PENDING',
        priority=2,
        reporter=wb_teacher,
        handler=wb_lab_admin,
    )


@pytest.fixture
def wb_notification(db, wb_system_admin, wb_teacher):
    from apps.notifications.models import Notification, NotificationRecipient
    notif = Notification.objects.create(
        title='白盒测试通知',
        content='白盒测试通知内容',
        notification_type='SYSTEM',
        priority='NORMAL',
        sender=wb_system_admin,
    )
    NotificationRecipient.objects.create(
        notification=notif,
        user=wb_teacher,
    )
    return notif


@pytest.fixture
def wb_request_factory():
    from django.test import RequestFactory
    return RequestFactory()


@pytest.fixture
def wb_mock_request(wb_request_factory, wb_super_admin):
    request = wb_request_factory.get('/')
    request.user = wb_super_admin
    request.META['REMOTE_ADDR'] = '127.0.0.1'
    request.META['HTTP_USER_AGENT'] = 'WhiteboxTest/1.0'
    return request
