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

# 确保项目根目录在 Python 路径中
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 设置 Django 环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lims.settings.test')
django.setup()


import pytest
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.fixture(scope='session')
def django_db_setup():
    """
    会话级别的数据库设置
    只在所有测试开始前执行一次
    """
    pass


@pytest.fixture
def system_admin_user(db):
    """创建系统管理员用户 (is_superuser=True)"""
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
    """创建管理员-校长用户 (role=16)"""
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
    """创建分院管理员用户"""
    from apps.users.models import Department

    dept = Department.objects.create(
        name='测试分院',
        code='TEST_DEPT'
    )
    
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
    """创建实训室管理员用户"""
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
    """创建普通教师用户"""
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
    """创建测试用的分院"""
    from apps.users.models import Department
    return Department.objects.create(
        name='计算机学院',
        code='CS_DEPT'
    )


@pytest.fixture
def test_laboratory(db, test_department, lab_admin_user):
    """创建测试用的实训室"""
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
