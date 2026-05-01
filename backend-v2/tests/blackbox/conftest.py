import pytest
import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lims.settings.testing')
django.setup()

from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from tests.blackbox.client import BlackboxAPIClient
from tests.blackbox.config import (
    DEFAULT_PASSWORD, ROLE_TEACHER, ROLE_LAB_ADMIN,
    ROLE_DEPT_ADMIN, ROLE_SUPER_ADMIN, ROLE_SYSTEM_ADMIN,
)

User = get_user_model()


@pytest.fixture
def api_client():
    return BlackboxAPIClient()


@pytest.fixture
def raw_client():
    return APIClient()


@pytest.fixture
def db_objects(db):
    class DBObjects:
        pass
    return DBObjects()


@pytest.fixture
def system_admin(db):
    return User.objects.create_user(
        username='bb_sys_admin',
        password=DEFAULT_PASSWORD,
        nickname='黑盒系统管理员',
        email='bb_sys@test.com',
        is_superuser=True,
        role=ROLE_SYSTEM_ADMIN,
        is_active=True,
    )


@pytest.fixture
def super_admin(db):
    return User.objects.create_user(
        username='bb_super_admin',
        password=DEFAULT_PASSWORD,
        nickname='黑盒超级管理员',
        email='bb_super@test.com',
        is_superuser=False,
        role=ROLE_SUPER_ADMIN,
        is_active=True,
    )


@pytest.fixture
def dept_admin(db, test_department):
    return User.objects.create_user(
        username='bb_dept_admin',
        password=DEFAULT_PASSWORD,
        nickname='黑盒分院管理员',
        email='bb_dept@test.com',
        is_superuser=False,
        role=ROLE_DEPT_ADMIN,
        department=test_department,
        is_active=True,
    )


@pytest.fixture
def lab_admin(db):
    return User.objects.create_user(
        username='bb_lab_admin',
        password=DEFAULT_PASSWORD,
        nickname='黑盒实训室管理员',
        email='bb_lab@test.com',
        is_superuser=False,
        role=ROLE_LAB_ADMIN,
        is_active=True,
    )


@pytest.fixture
def teacher(db, test_department):
    return User.objects.create_user(
        username='bb_teacher',
        password=DEFAULT_PASSWORD,
        nickname='黑盒教师',
        email='bb_teacher@test.com',
        is_superuser=False,
        role=ROLE_TEACHER,
        department=test_department,
        is_active=True,
    )


@pytest.fixture
def inactive_user(db):
    return User.objects.create_user(
        username='bb_inactive',
        password=DEFAULT_PASSWORD,
        nickname='黑盒停用用户',
        email='bb_inactive@test.com',
        is_superuser=False,
        role=ROLE_TEACHER,
        is_active=False,
    )


@pytest.fixture
def test_department(db):
    from apps.users.models import Department
    return Department.objects.create(
        name='黑盒测试分院',
        code='BB_DEPT',
    )


@pytest.fixture
def test_department_child(db, test_department):
    from apps.users.models import Department
    return Department.objects.create(
        name='黑盒测试子分院',
        code='BB_DEPT_CHILD',
        parent=test_department,
    )


@pytest.fixture
def test_laboratory(db, test_department, lab_admin):
    from apps.laboratories.models import Laboratory
    return Laboratory.objects.create(
        name='黑盒测试实训室',
        code='BB_LAB_001',
        building='黑盒测试楼',
        floor=3,
        room_number='301',
        capacity=30,
        area=100.5,
        laboratory_type='COMPUTER',
        department=test_department,
        admin=lab_admin,
        status=1,
    )


@pytest.fixture
def test_equipment(db, test_laboratory):
    from apps.laboratories.models import Equipment
    return Equipment.objects.create(
        name='黑盒测试设备',
        code='BB_EQ_001',
        category='COMPUTER',
        brand='测试品牌',
        model='Test-Model',
        laboratory=test_laboratory,
        status='NORMAL',
    )


@pytest.fixture
def test_semester(db):
    from apps.schedules.models import Semester
    Semester.objects.filter(is_current=True).update(is_current=False)
    return Semester.objects.create(
        name='黑盒测试学期2025-2026-1',
        code='BB_2025_2026_1',
        start_date='2025-09-01',
        end_date='2026-01-15',
        is_current=True,
        total_weeks=20,
    )


@pytest.fixture
def test_schedule(db, test_laboratory, test_semester, teacher):
    from apps.schedules.models import Schedule
    return Schedule.objects.create(
        course_name='黑盒测试课程',
        course_code='BB_COURSE_001',
        weekday=1,
        time_slot='1-2',
        weeks='1-16',
        laboratory=test_laboratory,
        semester=test_semester,
        teacher=teacher,
        teacher_name=teacher.nickname,
        class_name='黑盒测试班级',
        student_count=40,
        is_active=True,
    )


@pytest.fixture
def test_usage_record(db, test_laboratory, test_semester, teacher):
    from apps.records.models import UsageRecord
    return UsageRecord.objects.create(
        usage_date='2025-10-15',
        time_slot='1-2',
        class_hours=2,
        laboratory=test_laboratory,
        laboratory_name=test_laboratory.name,
        laboratory_code=test_laboratory.code,
        semester=test_semester,
        teacher=teacher,
        class_name='黑盒测试班级',
        student_count=40,
        content='黑盒测试课程内容',
        device_status='NORMAL',
        laboratory_status='NORMAL',
    )


@pytest.fixture
def test_work_order(db, test_laboratory, test_semester, teacher, lab_admin):
    from apps.maintenance.models import WorkOrder
    return WorkOrder.objects.create(
        title='黑盒测试工单',
        description='黑盒测试工单描述',
        laboratory=test_laboratory,
        laboratory_name=test_laboratory.name,
        laboratory_code=test_laboratory.code,
        semester=test_semester,
        maintenance_type=3,
        status='PENDING',
        priority=2,
        reporter=teacher,
        handler=lab_admin,
    )


@pytest.fixture
def authed_client(api_client, system_admin):
    api_client.authenticate(system_admin.username)
    return api_client


@pytest.fixture
def authed_super_admin(api_client, super_admin):
    api_client.authenticate(super_admin.username)
    return api_client


@pytest.fixture
def authed_dept_admin(api_client, dept_admin):
    api_client.authenticate(dept_admin.username)
    return api_client


@pytest.fixture
def authed_lab_admin(api_client, lab_admin):
    api_client.authenticate(lab_admin.username)
    return api_client


@pytest.fixture
def authed_teacher(api_client, teacher):
    api_client.authenticate(teacher.username)
    return api_client
