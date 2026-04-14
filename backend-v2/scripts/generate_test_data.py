"""
生成测试数据脚本 - 为信息工程学院和5120部门生成使用记录、维护记录、故障记录、课表数据
"""

import os
import django
import random
from datetime import date, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lims.settings.development')
django.setup()

from apps.users.models import User, Department
from apps.laboratories.models import Laboratory, Equipment
from apps.schedules.models import Semester, Schedule
from apps.records.models import UsageRecord
from apps.maintenance.models import MaintenanceRecord, WorkOrder
from apps.core.constants import UserRole, UserStatus, LaboratoryStatus, EquipmentStatus, WorkOrderStatus, MaintenanceType, WeekDay


DEPARTMENTS_CONFIG = [
    {
        'code': 'INFO',
        'name': '信息工程学院',
        'description': '信息工程学院，负责计算机、软件工程等专业教学',
        'building': '信息楼',
        'lab_prefix': 'INFO',
        'lab_names': [
            ('计算机网络实训室', 'NET'),
            ('软件开发实训室', 'DEV'),
            ('数据库实训室', 'DB'),
            ('人工智能实训室', 'AI'),
            ('网络安全实训室', 'SEC')
        ]
    },
    {
        'code': '5120',
        'name': '5120部门',
        'description': '5120部门，负责相关专业教学实训',
        'building': '实训楼',
        'lab_prefix': '5120',
        'lab_names': [
            ('智能制造实训室', 'ZZ'),
            ('电气控制实训室', 'DQ'),
            ('工业机器人实训室', 'JQ'),
            ('数控加工实训室', 'SK'),
            ('自动化生产线实训室', 'ZD')
        ]
    }
]

COURSES = [
    ('Python程序设计', 'CS101'),
    ('Java程序设计', 'CS102'),
    ('数据库原理', 'CS103'),
    ('计算机网络', 'CS104'),
    ('操作系统', 'CS105'),
    ('软件工程', 'CS106'),
    ('人工智能导论', 'CS107'),
    ('机器学习', 'CS108'),
    ('大数据技术', 'CS109'),
    ('网络安全', 'CS110'),
    ('Web前端开发', 'CS111'),
    ('移动应用开发', 'CS112'),
    ('云计算技术', 'CS113'),
    ('物联网技术', 'CS114'),
    ('嵌入式系统', 'CS115'),
    ('智能制造技术', 'ME101'),
    ('电气控制技术', 'ME102'),
    ('工业机器人编程', 'ME103'),
    ('数控加工技术', 'ME104'),
    ('自动化生产线', 'ME105'),
]

CLASS_NAMES = [
    '计科2301班', '计科2302班', '软工2301班', '软工2302班',
    '网络2301班', '数据2301班', '智能2301班', '物联网2301班',
    '制造2301班', '电气2301班', '机器人2301班', '数控2301班'
]

TEACHER_NAMES = [
    '张伟', '李娜', '王强', '刘洋', '陈静',
    '杨帆', '赵敏', '周杰', '吴芳', '郑浩',
    '孙磊', '钱红', '冯涛', '蒋丽', '沈明'
]

TIME_SLOTS = ['1-2节', '3-4节', '5-6节', '7-8节', '1-4节', '5-8节', '9-10节']


def get_or_create_department(dept_config):
    """获取或创建部门"""
    dept, created = Department.objects.get_or_create(
        code=dept_config['code'],
        defaults={
            'name': dept_config['name'],
            'description': dept_config['description'],
            'order': 1
        }
    )
    if created:
        print(f"创建部门: {dept.name}")
    else:
        print(f"部门已存在: {dept.name}")
    return dept


def get_or_create_semester():
    """获取或创建当前学期"""
    semester = Semester.get_current()
    if semester:
        print(f"当前学期: {semester.name}")
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
        print(f"创建学期: {semester.name}")
    else:
        semester.is_current = True
        semester.save()
        print(f"设置当前学期: {semester.name}")
    return semester


def get_or_create_teachers(dept, count=10):
    """获取或创建教师"""
    teachers = []
    dept_code = dept.code
    
    for i in range(count):
        username = f'{dept_code}_teacher{i+1}'
        teacher, created = User.objects.get_or_create(
            username=username,
            defaults={
                'nickname': TEACHER_NAMES[i % len(TEACHER_NAMES)],
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
            print(f"  创建教师: {teacher.nickname}")
        teachers.append(teacher)
    
    return teachers


def get_or_create_laboratories(dept, dept_config, count=5):
    """获取或创建实训室"""
    labs = []
    lab_names = dept_config['lab_names']
    building = dept_config['building']
    prefix = dept_config['lab_prefix']
    
    for i in range(count):
        lab_info = lab_names[i % len(lab_names)]
        code = f'{prefix}-{lab_info[1]}-{str(i+1).zfill(2)}'
        lab, created = Laboratory.objects.get_or_create(
            code=code,
            defaults={
                'name': lab_info[0],
                'department': dept,
                'building': building,
                'floor': (i % 5) + 1,
                'room_number': f'{(i % 5) + 1}0{i+1}',
                'capacity': 45,
                'area': 120.0,
                'laboratory_type': '专业实训室',
                'status': LaboratoryStatus.AVAILABLE,
                'description': f'{lab_info[0]}，配备先进设备'
            }
        )
        if created:
            print(f"  创建实训室: {lab.name}({lab.code})")
        labs.append(lab)
    
    return labs


def get_or_create_equipments(labs):
    """获取或创建设备"""
    equipments = []
    categories = ['计算机', '服务器', '交换机', '路由器', '投影仪']
    brands = ['Dell', 'HP', 'Lenovo', 'Huawei', 'Cisco']
    
    for lab in labs:
        for i in range(3):
            code = f'{lab.code}-EQ-{str(i+1).zfill(3)}'
            category = categories[i % len(categories)]
            brand = brands[i % len(brands)]
            
            equipment, created = Equipment.objects.get_or_create(
                code=code,
                laboratory=lab,
                defaults={
                    'name': f'{brand} {category}',
                    'category': category,
                    'brand': brand,
                    'model': f'Model-{random.randint(1000, 9999)}',
                    'status': EquipmentStatus.NORMAL,
                    'position': f'{i+1}号机位'
                }
            )
            if created:
                print(f"  创建设备: {equipment.name}({equipment.code})")
            equipments.append(equipment)
    
    return equipments


def create_schedules(labs, teachers, semester, count=20):
    """创建课表数据"""
    print(f"\n  开始创建 {count} 条课表记录...")
    
    created_count = 0
    for i in range(count):
        lab = random.choice(labs)
        teacher = random.choice(teachers)
        course = COURSES[i % len(COURSES)]
        weekday = random.randint(1, 7)
        time_slot = random.choice(TIME_SLOTS)
        
        start_week = random.randint(1, 10)
        end_week = min(start_week + random.randint(4, 8), 18)
        weeks = f'{start_week}-{end_week}'
        
        schedule, created = Schedule.objects.get_or_create(
            course_name=course[0],
            laboratory=lab,
            semester=semester,
            weekday=weekday,
            time_slot=time_slot,
            weeks=weeks,
            defaults={
                'course_code': course[1],
                'teacher': teacher,
                'teacher_name': teacher.nickname,
                'class_name': random.choice(CLASS_NAMES),
                'student_count': random.randint(25, 45),
                'is_active': True,
                'note': f'第{i+1}条课表'
            }
        )
        if created:
            created_count += 1
    
    print(f"  创建了 {created_count} 条课表记录")
    return created_count


def create_usage_records(labs, teachers, semester, count=20):
    """创建使用记录"""
    print(f"\n  开始创建 {count} 条使用记录...")
    
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
        '移动应用开发实践',
        '大数据分析实验',
        '云计算平台部署实训',
        '物联网应用开发',
        '机器学习算法实现',
        '区块链技术实践',
        '嵌入式系统设计',
        '计算机图形学实验',
        '算法设计与分析',
        '编译原理实践',
        '分布式系统实训'
    ]
    
    created_count = 0
    for i in range(count):
        lab = random.choice(labs)
        teacher = random.choice(teachers)
        usage_date = date.today() - timedelta(days=random.randint(1, 90))
        
        record, created = UsageRecord.objects.get_or_create(
            laboratory=lab,
            usage_date=usage_date,
            time_slot=random.choice(TIME_SLOTS),
            teacher=teacher,
            semester=semester,
            defaults={
                'class_name': random.choice(CLASS_NAMES),
                'student_count': random.randint(25, 45),
                'content': contents[i % len(contents)],
                'class_hours': random.choice([2, 4]),
                'device_status': '正常',
                'laboratory_status': '正常'
            }
        )
        if created:
            created_count += 1
    
    print(f"  创建了 {created_count} 条使用记录")
    return created_count


def create_maintenance_records(labs, teachers, semester, count=20):
    """创建维护记录"""
    print(f"\n  开始创建 {count} 条维护记录...")
    
    contents = [
        '定期检查设备运行状态，清洁设备表面',
        '更新操作系统和软件补丁',
        '检查网络连接，优化网络配置',
        '清理磁盘空间，优化系统性能',
        '检查空调设备运行状态',
        '更换老化电源线和网线',
        '校准投影仪画面',
        '检查消防设施和安全出口',
        '维护UPS电源设备',
        '检查监控设备运行状态',
        '清洁空调滤网',
        '检查门禁系统',
        '维护服务器散热系统',
        '更新杀毒软件病毒库',
        '检查接地线路',
        '维护网络交换设备',
        '检查照明设备',
        '维护实验桌椅',
        '检查通风系统',
        '维护打印设备'
    ]
    
    statuses = ['maintained', 'maintained', 'maintained', 'pending', 'processing']
    
    created_count = 0
    for i in range(count):
        lab = random.choice(labs)
        maintainer = random.choice(teachers)
        maintenance_time = date.today() - timedelta(days=random.randint(1, 90))
        
        order_number = MaintenanceRecord.generate_order_number('W')
        
        record, created = MaintenanceRecord.objects.get_or_create(
            order_number=order_number,
            defaults={
                'order_type': 'W',
                'laboratory': lab,
                'maintainer': maintainer,
                'content': contents[i % len(contents)],
                'status': random.choice(statuses),
                'maintenance_time': maintenance_time,
                'semester': semester,
                'note': f'第{i+1}次例行维护'
            }
        )
        if created:
            created_count += 1
    
    print(f"  创建了 {created_count} 条维护记录")
    return created_count


def create_work_orders(labs, teachers, equipments, semester, count=20):
    """创建故障工单"""
    print(f"\n  开始创建 {count} 条故障工单...")
    
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
        '软件无法安装',
        '打印机卡纸',
        '音响无声音',
        '门禁系统故障',
        '监控画面丢失',
        '服务器宕机',
        '交换机端口故障',
        '电源插座损坏',
        '硬盘读写错误',
        '内存条故障',
        '显卡驱动异常'
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
        '安装软件时提示权限不足',
        '打印机卡纸，无法取出',
        '音响设备无声音输出',
        '刷卡无法开门，系统无响应',
        '监控画面黑屏，无法录像',
        '服务器无法访问，网站打不开',
        '网络端口指示灯不亮',
        '插座接触不良，设备频繁断电',
        '硬盘读写时发出异响',
        '开机报警，内存检测失败',
        '显示分辨率异常，无法调整'
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
        '以管理员权限重新安装',
        '清理卡纸，校准打印头',
        '检查音频线连接，更新驱动',
        '重启门禁控制器，重新授权',
        '更换摄像头，恢复监控',
        '重启服务器，检查日志',
        '更换交换机端口，网络恢复',
        '更换插座面板，测试正常',
        '更换硬盘，数据迁移完成',
        '更换内存条，系统正常',
        '重新安装显卡驱动，问题解决'
    ]
    
    statuses = [WorkOrderStatus.PENDING, WorkOrderStatus.PROCESSING, WorkOrderStatus.COMPLETED, WorkOrderStatus.CLOSED]
    maintenance_types = [MaintenanceType.REPAIR, MaintenanceType.ROUTINE, MaintenanceType.SAFETY]
    
    created_count = 0
    for i in range(count):
        lab = random.choice(labs)
        reporter = random.choice(teachers)
        equipment = random.choice(equipments) if equipments else None
        status = random.choice(statuses)
        
        reported_at = date.today() - timedelta(days=random.randint(1, 90))
        
        defaults = {
            'title': titles[i % len(titles)],
            'description': descriptions[i % len(descriptions)],
            'laboratory': lab,
            'equipment': equipment,
            'semester': semester,
            'maintenance_type': random.choice(maintenance_types).value,
            'status': status.value,
            'priority': random.randint(1, 3),
            'reporter': reporter,
            'reported_at': reported_at,
        }
        
        if status in [WorkOrderStatus.COMPLETED, WorkOrderStatus.CLOSED]:
            handler = random.choice([t for t in teachers if t != reporter])
            defaults['handler'] = handler
            defaults['solution'] = solutions[i % len(solutions)]
            defaults['completed_at'] = reported_at + timedelta(days=random.randint(1, 7))
        
        order, created = WorkOrder.objects.get_or_create(
            title=titles[i % len(titles)],
            laboratory=lab,
            reporter=reporter,
            reported_at__date=reported_at,
            defaults=defaults
        )
        if created:
            created_count += 1
    
    print(f"  创建了 {created_count} 条故障工单")
    return created_count


def process_department(dept_config, semester):
    """处理单个部门的数据生成"""
    print(f"\n{'='*50}")
    print(f"开始处理部门: {dept_config['name']}")
    print('='*50)
    
    dept = get_or_create_department(dept_config)
    
    print(f"\n创建教师...")
    teachers = get_or_create_teachers(dept, count=10)
    
    print(f"\n创建实训室...")
    labs = get_or_create_laboratories(dept, dept_config, count=5)
    
    print(f"\n创建设备...")
    equipments = get_or_create_equipments(labs)
    
    print(f"\n生成记录数据...")
    
    schedule_count = create_schedules(labs, teachers, semester, count=20)
    usage_count = create_usage_records(labs, teachers, semester, count=20)
    maintenance_count = create_maintenance_records(labs, teachers, semester, count=20)
    work_order_count = create_work_orders(labs, teachers, equipments, semester, count=20)
    
    return {
        'dept': dept,
        'teachers': len(teachers),
        'labs': len(labs),
        'equipments': len(equipments),
        'schedules': schedule_count,
        'usage_records': usage_count,
        'maintenance_records': maintenance_count,
        'work_orders': work_order_count
    }


def main():
    print("=" * 60)
    print("开始为信息工程学院和5120部门生成测试数据")
    print("=" * 60)
    
    semester = get_or_create_semester()
    
    results = []
    for dept_config in DEPARTMENTS_CONFIG:
        result = process_department(dept_config, semester)
        results.append(result)
    
    print("\n" + "=" * 60)
    print("数据生成完成!")
    print("=" * 60)
    
    for result in results:
        dept = result['dept']
        print(f"\n【{dept.name}】")
        print(f"  课表记录: {result['schedules']} 条")
        print(f"  使用记录: {result['usage_records']} 条")
        print(f"  维护记录: {result['maintenance_records']} 条")
        print(f"  故障工单: {result['work_orders']} 条")
        print(f"  实训室: {result['labs']} 个")
        print(f"  教师: {result['teachers']} 人")
        print(f"  设备: {result['equipments']} 台")


if __name__ == '__main__':
    main()
