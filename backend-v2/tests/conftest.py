"""
全局 pytest 配置文件

功能：
1. 配置 Django 测试环境
2. 定义可复用的测试 fixtures（数据库、用户等）
3. 统一测试配置
"""

import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lims.settings.test')
django.setup()


import pytest
from django.contrib.auth import get_user_model
from django.test import RequestFactory

User = get_user_model()


@pytest.fixture(scope='session')
def django_db_setup():
    pass


@pytest.fixture
def system_admin_user(db):
    return User.objects.create_user(
        username='test_system_admin',
        password='test123456',
        nickname='测试系统管理员',
        email='test_sys@example.com',
        is_superuser=True,
        role=32,
        is_active=True
    )


@pytest.fixture
def super_admin_user(db):
    return User.objects.create_user(
        username='test_super_admin',
        password='test123456',
        nickname='测试管理员校长',
        email='test_super@example.com',
        is_superuser=False,
        role=16,
        is_active=True
    )


@pytest.fixture
def department_admin_user(db):
    from apps.users.models import Department
    dept = Department.objects.create(name='测试分院', code='TEST_DEPT')
    return User.objects.create_user(
        username='test_dept_admin',
        password='test123456',
        nickname='测试分院管理员',
        email='test_dept@example.com',
        is_superuser=False,
        role=4,
        department=dept,
        is_active=True
    )


@pytest.fixture
def lab_admin_user(db):
    return User.objects.create_user(
        username='test_lab_admin',
        password='test123456',
        nickname='测试实训室管理员',
        email='test_lab@example.com',
        is_superuser=False,
        role=2,
        is_active=True
    )


@pytest.fixture
def teacher_user(db):
    return User.objects.create_user(
        username='test_teacher',
        password='test123456',
        nickname='测试教师',
        email='test_teacher@example.com',
        is_superuser=False,
        role=1,
        is_active=True
    )


@pytest.fixture
def test_department(db):
    from apps.users.models import Department
    return Department.objects.create(name='计算机学院', code='CS_DEPT')


@pytest.fixture
def test_laboratory(db, test_department, lab_admin_user):
    from apps.laboratories.models import Laboratory
    return Laboratory.objects.create(
        name='测试实训室',
        code='TEST_LAB_001',
        building='测试楼',
        floor=3,
        room_number='301',
        capacity=30,
        laboratory_type='COMPUTER',
        department=test_department,
        admin=lab_admin_user,
        status=1
    )


@pytest.fixture
def wb_department(db):
    from apps.users.models import Department
    return Department.objects.create(name='白盒测试分院', code='WB_DEPT')


@pytest.fixture
def wb_system_admin(db):
    return User.objects.create_user(
        username='wb_sys_admin', password='WbTest@123456',
        nickname='白盒系统管理员', is_superuser=True, role=32, is_active=True,
    )


@pytest.fixture
def wb_super_admin(db, wb_department):
    return User.objects.create_user(
        username='wb_super_admin', password='WbTest@123456',
        nickname='白盒超级管理员', is_superuser=False, role=16,
        department=wb_department, is_active=True,
    )


@pytest.fixture
def wb_dept_admin(db, wb_department):
    return User.objects.create_user(
        username='wb_dept_admin', password='WbTest@123456',
        nickname='白盒分院管理员', is_superuser=False, role=4,
        department=wb_department, is_active=True,
    )


@pytest.fixture
def wb_lab_admin(db, wb_department):
    return User.objects.create_user(
        username='wb_lab_admin', password='WbTest@123456',
        nickname='白盒实训室管理员', is_superuser=False, role=2,
        department=wb_department, is_active=True,
    )


@pytest.fixture
def wb_teacher(db, wb_department):
    return User.objects.create_user(
        username='wb_teacher', password='WbTest@123456',
        nickname='白盒教师', is_superuser=False, role=1,
        department=wb_department, is_active=True,
    )


@pytest.fixture
def wb_inactive_user(db, wb_department):
    return User.objects.create_user(
        username='wb_inactive', password='WbTest@123456',
        nickname='白盒停用用户', is_superuser=False, role=1,
        department=wb_department, is_active=False,
    )


@pytest.fixture
def wb_laboratory(db, wb_department, wb_lab_admin):
    from apps.laboratories.models import Laboratory
    return Laboratory.objects.create(
        name='白盒测试实训室', code='WB_LAB_001', building='白盒测试楼',
        floor=3, room_number='301', capacity=30, area=100.5,
        laboratory_type='COMPUTER', department=wb_department,
        admin=wb_lab_admin, status=1,
    )


@pytest.fixture
def wb_laboratory2(db, wb_department, wb_lab_admin):
    from apps.laboratories.models import Laboratory
    return Laboratory.objects.create(
        name='白盒测试实训室2', code='WB_LAB_002', building='白盒测试楼',
        floor=3, room_number='302', capacity=50, area=150.0,
        laboratory_type='COMPUTER', department=wb_department,
        admin=wb_lab_admin, status=1,
    )


@pytest.fixture
def wb_equipment(db, wb_laboratory):
    from apps.laboratories.models import Equipment
    return Equipment.objects.create(
        name='白盒测试设备', code='WB_EQ_001', category='COMPUTER',
        brand='测试品牌', model='WB-Model', laboratory=wb_laboratory, status='NORMAL',
    )


@pytest.fixture
def wb_semester(db):
    from apps.schedules.models import Semester
    return Semester.objects.create(
        name='白盒测试学期2025-2026-1', code='WB_2025_2026_1',
        start_date='2025-09-01', end_date='2026-01-15',
        is_current=True, total_weeks=20,
    )


@pytest.fixture
def wb_semester_not_current(db):
    from apps.schedules.models import Semester
    return Semester.objects.create(
        name='白盒测试学期2024-2025-2', code='WB_2024_2025_2',
        start_date='2025-02-01', end_date='2025-06-30',
        is_current=False, total_weeks=18,
    )


@pytest.fixture
def wb_schedule(db, wb_laboratory, wb_semester, wb_teacher):
    from apps.schedules.models import Schedule
    return Schedule.objects.create(
        course_name='白盒测试课程', course_code='WB_COURSE_001',
        weekday=1, time_slot='1-2', weeks='1-16',
        laboratory=wb_laboratory, semester=wb_semester,
        teacher=wb_teacher, teacher_name=wb_teacher.nickname,
        class_name='白盒测试班级', student_count=40, is_active=True,
    )


@pytest.fixture
def wb_usage_record(db, wb_laboratory, wb_semester, wb_teacher):
    from apps.records.models import UsageRecord
    return UsageRecord.objects.create(
        usage_date='2025-10-15', time_slot='1-2', class_hours=2,
        laboratory=wb_laboratory, laboratory_name=wb_laboratory.name,
        laboratory_code=wb_laboratory.code, semester=wb_semester,
        teacher=wb_teacher, class_name='白盒测试班级', student_count=40,
        content='白盒测试课程内容', device_status='NORMAL', laboratory_status='NORMAL',
    )


@pytest.fixture
def wb_work_order(db, wb_laboratory, wb_semester, wb_teacher, wb_lab_admin):
    from apps.maintenance.models import WorkOrder
    return WorkOrder.objects.create(
        title='白盒测试工单', description='白盒测试工单描述',
        laboratory=wb_laboratory, laboratory_name=wb_laboratory.name,
        laboratory_code=wb_laboratory.code, semester=wb_semester,
        maintenance_type=3, status='PENDING', priority=2,
        reporter=wb_teacher, handler=wb_lab_admin,
    )


@pytest.fixture
def wb_notification(db, wb_system_admin, wb_teacher):
    from apps.notifications.models import Notification, NotificationRecipient
    notif = Notification.objects.create(
        title='白盒测试通知', content='白盒测试通知内容',
        notification_type='SYSTEM', priority='NORMAL', sender=wb_system_admin,
    )
    NotificationRecipient.objects.create(notification=notif, user=wb_teacher)
    return notif


@pytest.fixture
def wb_request_factory():
    return RequestFactory()


@pytest.fixture
def wb_mock_request(wb_request_factory, wb_super_admin):
    request = wb_request_factory.get('/')
    request.user = wb_super_admin
    request.META['REMOTE_ADDR'] = '127.0.0.1'
    request.META['HTTP_USER_AGENT'] = 'WhiteboxTest/1.0'
    return request
