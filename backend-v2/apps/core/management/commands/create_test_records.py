from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
import random
from datetime import date, timedelta

from apps.users.models import User, Department
from apps.laboratories.models import Laboratory
from apps.schedules.models import Semester
from apps.records.models import UsageRecord
from apps.maintenance.models import WorkOrder
from apps.core.constants import UserRole, UserStatus, LaboratoryStatus, WorkOrderStatus, MaintenanceType


class Command(BaseCommand):
    help = '生成测试数据：使用记录、维护记录、故障记录'

    def add_arguments(self, parser):
        parser.add_argument('--usage', type=int, default=10, help='使用记录数量')
        parser.add_argument('--maintain', type=int, default=5, help='维护记录数量')
        parser.add_argument('--fault', type=int, default=5, help='故障记录数量')

    def handle(self, *args, **options):
        usage_count = options['usage']
        maintain_count = options['maintain']
        fault_count = options['fault']

        self.stdout.write("=" * 60)
        self.stdout.write("开始生成测试数据")
        self.stdout.write("=" * 60)

        semester = self.get_or_create_semester()
        dept = self.get_or_create_department()

        self.stdout.write("\n创建教师...")
        teachers = self.get_or_create_teachers(dept, count=5)

        self.stdout.write("\n创建实训室...")
        labs = self.get_or_create_laboratories(dept, count=3)

        created_usage = self.create_usage_records(labs, teachers, semester, count=usage_count)
        created_maintain = self.create_maintenance_records(labs, teachers, semester, count=maintain_count)
        created_fault = self.create_fault_records(labs, teachers, semester, count=fault_count)

        self.stdout.write("\n" + "=" * 60)
        self.stdout.write(self.style.SUCCESS("数据生成完成!"))
        self.stdout.write("=" * 60)
        self.stdout.write(f"\n统计:")
        self.stdout.write(f"  使用记录: {created_usage} 条")
        self.stdout.write(f"  维护记录: {created_maintain} 条")
        self.stdout.write(f"  故障记录: {created_fault} 条")
        self.stdout.write(f"  实训室: {len(labs)} 个")
        self.stdout.write(f"  教师: {len(teachers)} 人")

    def get_or_create_semester(self):
        semester = Semester.get_current()
        if semester:
            self.stdout.write(f"使用当前学期: {semester.name}")
            return semester

        semester, created = Semester.objects.get_or_create(
            code='2025-1',
            defaults={
                'name': '2025年第一学期',
                'start_date': date(2025, 2, 17),
                'end_date': date(2025, 6, 30),
                'is_current': True,
                'total_weeks': 18
            }
        )
        if created:
            self.stdout.write(f"创建学期: {semester.name}")
        else:
            semester.is_current = True
            semester.save()
            self.stdout.write(f"设置当前学期: {semester.name}")
        return semester

    def get_or_create_department(self):
        dept, created = Department.objects.get_or_create(
            code='INFO',
            defaults={
                'name': '信息工程学院',
                'description': '信息工程学院，负责计算机、软件工程等专业教学',
                'order': 1
            }
        )
        if created:
            self.stdout.write(f"创建部门: {dept.name}")
        else:
            self.stdout.write(f"使用部门: {dept.name}")
        return dept

    def get_or_create_teachers(self, dept, count=5):
        teachers = []
        teacher_names = ['张伟', '李娜', '王强', '刘洋', '陈静', '杨帆', '赵敏', '周杰', '吴芳', '郑浩']

        for i in range(count):
            username = f'teacher{i+1}'
            teacher, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'nickname': teacher_names[i % len(teacher_names)],
                    'department': dept,
                    'role': UserRole.TEACHER,
                    'status': UserStatus.ACTIVE,
                    'email': f'{username}@example.com',
                    'phone': f'138{str(random.randint(10000000, 99999999))}'
                }
            )
            if created:
                teacher.set_password('123456')
                teacher.save()
                self.stdout.write(f"  创建教师: {teacher.nickname}")
            teachers.append(teacher)

        return teachers

    def get_or_create_laboratories(self, dept, count=3):
        labs = []
        lab_names = [
            ('计算机网络实训室', 'NET'),
            ('软件开发实训室', 'DEV'),
            ('数据库实训室', 'DB'),
            ('人工智能实训室', 'AI'),
            ('网络安全实训室', 'SEC')
        ]

        for i in range(count):
            lab_info = lab_names[i % len(lab_names)]
            code = f'LAB-{lab_info[1]}-{str(i+1).zfill(2)}'
            lab, created = Laboratory.objects.get_or_create(
                code=code,
                defaults={
                    'name': lab_info[0],
                    'department': dept,
                    'building': '信息楼',
                    'floor': (i % 3) + 1,
                    'room_number': f'{(i % 3) + 1}0{i+1}',
                    'capacity': 45,
                    'area': 120.0,
                    'laboratory_type': '专业实训室',
                    'status': LaboratoryStatus.AVAILABLE,
                    'description': f'{lab_info[0]}，配备先进设备'
                }
            )
            if created:
                self.stdout.write(f"  创建实训室: {lab.name}({lab.code})")
            labs.append(lab)

        return labs

    def create_usage_records(self, labs, teachers, semester, count=10):
        self.stdout.write(f"\n开始创建 {count} 条使用记录...")

        contents = [
            'Python程序设计实践',
            'Java Web开发实训',
            '数据库原理与应用',
            '计算机网络配置实验',
            '操作系统课程设计',
            '软件工程综合实训',
            '人工智能基础实验',
            '网络安全攻防演练',
            '前端开发实战训练',
            '移动应用开发实践'
        ]

        class_names = ['计科2301班', '计科2302班', '软工2301班', '软工2302班', '网络2301班']
        time_slots = ['1-2节', '3-4节', '5-6节', '7-8节', '1-4节', '5-8节']

        created_count = 0
        for i in range(count):
            lab = random.choice(labs)
            teacher = random.choice(teachers)
            usage_date = timezone.now().date() - timedelta(days=random.randint(1, 60))
            time_slot = random.choice(time_slots)

            record, created = UsageRecord.objects.get_or_create(
                laboratory=lab,
                usage_date=usage_date,
                time_slot=time_slot,
                teacher=teacher,
                semester=semester,
                defaults={
                    'laboratory_name': lab.name,
                    'laboratory_code': lab.code,
                    'class_name': random.choice(class_names),
                    'student_count': random.randint(25, 45),
                    'content': contents[i % len(contents)],
                    'class_hours': random.choice([2, 4]),
                    'device_status': '正常',
                    'laboratory_status': '正常'
                }
            )
            if created:
                created_count += 1

        self.stdout.write(f"  创建了 {created_count} 条使用记录")
        return created_count

    def create_maintenance_records(self, labs, teachers, semester, count=5):
        self.stdout.write(f"\n开始创建 {count} 条维护记录...")

        contents = [
            '定期设备检查维护',
            '系统软件更新升级',
            '网络设备巡检',
            '空调清洗保养',
            '投影仪清洁维护',
            '安全检查维护',
            '设备除尘清洁',
            '线路检查维护'
        ]

        solutions = [
            '已完成全部设备检查，运行正常',
            '系统已更新至最新版本',
            '网络设备运行正常，无异常',
            '空调已清洗，制冷效果良好',
            '投影仪已清洁，画面清晰',
            '安全隐患已排除',
            '设备已除尘，运行稳定',
            '线路已检查，无安全隐患'
        ]

        created_count = 0
        for i in range(count):
            lab = random.choice(labs)
            reporter = random.choice(teachers)
            handler = random.choice([t for t in teachers if t != reporter])
            reported_at = timezone.now().date() - timedelta(days=random.randint(1, 60))

            order_number = WorkOrder.generate_order_number(maintenance_type=1)

            work_order, created = WorkOrder.objects.get_or_create(
                order_number=order_number,
                defaults={
                    'title': f'{lab.name}维护工单',
                    'description': contents[i % len(contents)],
                    'laboratory': lab,
                    'laboratory_name': lab.name,
                    'laboratory_code': lab.code,
                    'semester': semester,
                    'maintenance_type': MaintenanceType.ROUTINE.value,
                    'status': WorkOrderStatus.COMPLETED.value,
                    'priority': 2,
                    'reporter': reporter,
                    'handler': handler,
                    'reported_at': reported_at,
                    'started_at': reported_at + timedelta(hours=2),
                    'completed_at': reported_at + timedelta(days=1),
                    'solution': solutions[i % len(solutions)]
                }
            )
            if created:
                created_count += 1

        self.stdout.write(f"  创建了 {created_count} 条维护记录")
        return created_count

    def create_fault_records(self, labs, teachers, semester, count=5):
        self.stdout.write(f"\n开始创建 {count} 条故障记录...")

        titles = [
            '计算机无法启动',
            '网络连接异常',
            '投影仪显示模糊',
            '空调不制冷',
            '显示器花屏',
            '键盘按键失灵',
            '鼠标无法使用',
            'USB接口损坏',
            '系统运行缓慢',
            '软件无法安装'
        ]

        descriptions = [
            '开机后无反应，电源指示灯不亮',
            '无法连接校园网，显示网络受限',
            '投影画面出现重影和模糊',
            '空调运行但不制冷，温度无法调节',
            '显示器出现彩色条纹和闪烁',
            '部分按键无响应，影响正常使用',
            '鼠标光标无法移动，点击无效',
            'U盘无法识别，接口松动',
            '系统启动缓慢，程序响应迟钝',
            '安装软件时提示权限不足'
        ]

        solutions = [
            '更换电源适配器，问题已解决',
            '重新配置网络参数，恢复连接',
            '清洁投影仪镜头，调整焦距',
            '添加制冷剂，清洗滤网',
            '更换显示器连接线，更新驱动',
            '更换新键盘，测试正常',
            '更换USB鼠标，功能正常',
            '更换USB接口板，问题解决',
            '清理系统垃圾，升级内存',
            '以管理员权限重新安装'
        ]

        statuses = [WorkOrderStatus.PENDING, WorkOrderStatus.PROCESSING, WorkOrderStatus.COMPLETED, WorkOrderStatus.CLOSED]

        created_count = 0
        for i in range(count):
            lab = random.choice(labs)
            reporter = random.choice(teachers)
            status = random.choice(statuses)
            reported_at = timezone.now().date() - timedelta(days=random.randint(1, 60))

            order_number = WorkOrder.generate_order_number(maintenance_type=3)

            defaults = {
                'title': titles[i % len(titles)],
                'description': descriptions[i % len(descriptions)],
                'laboratory': lab,
                'laboratory_name': lab.name,
                'laboratory_code': lab.code,
                'semester': semester,
                'maintenance_type': MaintenanceType.REPAIR.value,
                'status': status.value,
                'priority': random.randint(1, 3),
                'reporter': reporter,
                'reported_at': reported_at,
            }

            if status in [WorkOrderStatus.COMPLETED, WorkOrderStatus.CLOSED]:
                handler = random.choice([t for t in teachers if t != reporter])
                defaults['handler'] = handler
                defaults['solution'] = solutions[i % len(solutions)]
                defaults['started_at'] = reported_at + timedelta(hours=4)
                defaults['completed_at'] = reported_at + timedelta(days=random.randint(1, 3))

            work_order, created = WorkOrder.objects.get_or_create(
                order_number=order_number,
                defaults=defaults
            )
            if created:
                created_count += 1

        self.stdout.write(f"  创建了 {created_count} 条故障记录")
        return created_count
