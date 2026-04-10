"""
初始化数据脚本
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lims.settings.development')
django.setup()

from apps.users.models import User, Department
from apps.schedules.models import Semester


def create_departments():
    """创建部门"""
    departments = [
        {'name': '信息工程学院', 'code': 'INFO'},
        {'name': '机械工程学院', 'code': 'MECH'},
        {'name': '电气工程学院', 'code': 'ELEC'},
    ]
    
    for dept_data in departments:
        Department.objects.get_or_create(
            code=dept_data['code'],
            defaults=dept_data
        )
    print(f"创建了 {len(departments)} 个部门")


def create_super_admin():
    """创建超级管理员"""
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser(
            username='admin',
            password='admin123',
            nickname='超级管理员',
            role=16
        )
        print("创建了超级管理员: admin / admin123")


def create_semester():
    """创建当前学期"""
    from datetime import date
    
    semester, created = Semester.objects.get_or_create(
        code='2024-1',
        defaults={
            'name': '2024年第一学期',
            'start_date': date(2024, 2, 26),
            'end_date': date(2024, 7, 5),
            'is_current': True,
            'total_weeks': 18
        }
    )
    
    if created:
        print(f"创建了学期: {semester.name}")
    else:
        print(f"学期已存在: {semester.name}")


def main():
    print("开始初始化数据...")
    create_departments()
    create_super_admin()
    create_semester()
    print("初始化完成!")


if __name__ == '__main__':
    main()
