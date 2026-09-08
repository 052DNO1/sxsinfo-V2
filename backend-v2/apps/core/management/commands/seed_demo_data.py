"""
初始化/重建演示数据命令（V0.1.3 schema 专用）
用法: python manage.py seed_demo_data
生成: 3 个学院部门 + admin 超管 + 各角色账号 + 当前学期 + 实训室/设备/课表/记录/工单
说明: 全部密码统一 Lims@2026（仅演示环境）；当前学期取真实日期避免"过期当前学期"。
"""

from datetime import date, time, datetime
from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.users.models import User, Department
from apps.schedules.models import Semester, Schedule
from apps.laboratories.models import Laboratory, Equipment
from apps.records.models import UsageRecord
from apps.maintenance.models import WorkOrder
from apps.core.constants import (
    UserRole, UserStatus, LaboratoryStatus, EquipmentStatus,
    WorkOrderStatus, MaintenanceType, WeekDay,
)

DEMO_PASSWORD = 'Lims@2026'

DEPARTMENTS = [
    {'name': '信息工程学院', 'code': 'INFO'},
    {'name': '机械工程学院', 'code': 'MECH'},
    {'name': '电气工程学院', 'code': 'ELEC'},
]

SEMESTER = {
    'name': '2026-2027学年第一学期',
    'code': '2026-2027-1',
    'start_date': date(2026, 9, 1),
    'end_date': date(2027, 1, 20),
    'total_weeks': 20,
}

LABS = [
    # (名称, 门牌, 部门code, 工位数)
    ('软件工程实训室', 'A101', 'INFO', 48),
    ('网络技术实训室', 'A102', 'INFO', 40),
    ('智能制造实训室', 'B201', 'MECH', 32),
    ('数控加工实训室', 'B202', 'MECH', 24),
    ('电气自动化实训室', 'C301', 'ELEC', 36),
    ('PLC 控制实训室', 'C302', 'ELEC', 28),
]

EQUIPMENT_TEMPLATES = [
    # (名称, 品牌, 型号)
    ('教师工作站', 'Dell', 'OptiPlex 7010'),
    ('学生终端', 'Lenovo', 'ThinkCentre M75'),
    ('网络交换机', 'H3C', 'S5130'),
    ('投影仪', 'Epson', 'CB-X49'),
    ('实验台', '定制', 'XTL-2'),
]

TEACHER_NAMES = ['张伟', '李娜', '王强', '刘洋', '陈静']


class Command(BaseCommand):
    help = '生成演示数据（V0.1.3）'

    def handle(self, *args, **options):
        created = {'departments': 0, 'users': 0, 'semester': 0,
                   'labs': 0, 'equipments': 0, 'schedules': 0,
                   'records': 0, 'work_orders': 0}

        # ---- 部门 ----
        dept_map = {}
        for d in DEPARTMENTS:
            obj, was_created = Department.objects.get_or_create(
                code=d['code'], defaults=d)
            dept_map[d['code']] = obj
            created['departments'] += int(was_created)

        # ---- 超管 ----
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser(
                username='admin', password=DEMO_PASSWORD,
                nickname='系统管理员', role=UserRole.SUPER_ADMIN,
                department=None)
            created['users'] += 1

        # ---- 分院管理员 & 教师 ----
        teacher_idx = 0
        for code, dept in dept_map.items():
            admin_name = f'admin_{code.lower()}'
            if not User.objects.filter(username=admin_name).exists():
                User.objects.create_user(
                    username=admin_name, password=DEMO_PASSWORD,
                    nickname=f'{dept.name}管理员',
                    role=UserRole.DEPARTMENT_ADMIN, department=dept,
                    is_active=True)
                created['users'] += 1
            # 每学院 2 名教师
            for i in range(2):
                if teacher_idx >= len(TEACHER_NAMES):
                    break
                username = f'teacher{code.lower()}{i+1}'
                if not User.objects.filter(username=username).exists():
                    User.objects.create_user(
                        username=username, password=DEMO_PASSWORD,
                        nickname=TEACHER_NAMES[teacher_idx],
                        role=UserRole.TEACHER, department=dept,
                        is_active=True)
                    created['users'] += 1
                teacher_idx += 1

        # ---- 当前学期（先清掉旧 current）----
        Semester.objects.filter(is_current=True).update(is_current=False)
        sem, was_created = Semester.objects.update_or_create(
            code=SEMESTER['code'],
            defaults={**SEMESTER, 'is_current': True, 'is_archived': False})
        created['semester'] += int(was_created)

        # ---- 实训室 & 设备 ----
        admin_user = User.objects.filter(username='admin').first()
        for name, room, dept_code, seats in LABS:
            dept = dept_map[dept_code]
            lab, was_created = Laboratory.objects.get_or_create(
                code=room,
                defaults={
                    'name': name, 'room_number': room, 'capacity': seats,
                    'department': dept, 'admin': admin_user,
                    'status': LaboratoryStatus.AVAILABLE,
                    'is_available': True,
                })
            created['labs'] += int(was_created)
            for eidx, (ename, brand, model) in enumerate(EQUIPMENT_TEMPLATES):
                eq_code = f'{room}-{eidx+1:02d}'
                if not Equipment.objects.filter(code=eq_code, laboratory=lab).exists():
                    Equipment.objects.create(
                        code=eq_code, name=ename, brand=brand, model=model,
                        laboratory=lab, status=EquipmentStatus.NORMAL)
                    created['equipments'] += 1

        # ---- 课表 / 记录 / 工单 ----
        labs_list = list(Laboratory.objects.filter(is_deleted=False))
        teachers = [u for u in User.objects.filter(is_deleted=False)
                    if u.has_role(UserRole.TEACHER)]
        now = timezone.now()
        if labs_list and teachers:
            for i, lab in enumerate(labs_list[:4]):
                teacher = teachers[i % len(teachers)]
                _, s_created = Schedule.objects.get_or_create(
                    laboratory=lab, semester=sem, weekday=WeekDay.MONDAY,
                    time_slot='1-2',
                    defaults={
                        'course_name': f'{lab.name}实训课{i+1}',
                        'teacher': teacher, 'weeks': '1-16',
                        'class_name': f'计科{2301+i}班',
                        'student_count': 40 - i * 5,
                    })
                created['schedules'] += int(s_created)
                # 使用记录
                for d in range(1, 4):
                    record_date = now.date()
                    if not UsageRecord.objects.filter(
                            laboratory=lab, usage_date=record_date).exists():
                        UsageRecord.objects.create(
                            laboratory=lab, semester=sem,
                            usage_date=record_date, time_slot='1-2',
                            teacher=teacher, class_hours=2,
                            student_count=40 - i * 5,
                            content=f'{lab.name}常规实训',
                            device_status='正常', laboratory_status='正常')
                        created['records'] += 1
                # 工单
                if not WorkOrder.objects.filter(
                        laboratory=lab, title__startswith='巡检').exists():
                    WorkOrder.objects.create(
                        order_number=f'WO-{lab.id}-001',
                        title=f'{lab.name}月度巡检',
                        description='设备与线路例行巡检',
                        maintenance_type=MaintenanceType.ROUTINE,
                        reporter=teacher, laboratory=lab, semester=sem,
                        status=WorkOrderStatus.COMPLETED)
                    created['work_orders'] += 1

        # ---- 汇总 ----
        summary = ' | '.join(f'{k}:{v}' for k, v in created.items())
        self.stdout.write(self.style.SUCCESS(f'演示数据完成：{summary}'))
        self.stdout.write(self.style.SUCCESS(
            f'管理员账号 admin / {DEMO_PASSWORD}；分院管理员/教师口令同'))
        self.stdout.write(self.style.SUCCESS(f'当前学期：{sem.name}'
                                             f'({sem.start_date}~{sem.end_date})'))
