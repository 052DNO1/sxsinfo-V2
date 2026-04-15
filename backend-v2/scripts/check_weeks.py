import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lims.settings.development')
django.setup()

from apps.schedules.models import Schedule

print('='*60)
print('检查课表周次范围')
print('='*60)

schedules = Schedule.objects.all()
print(f'总课表数: {schedules.count()}')

# 检查包含第1周的课表
week1_schedules = []
for s in schedules:
    weeks_str = s.weeks
    if weeks_str:
        parts = weeks_str.split('-')
        if len(parts) == 2:
            start, end = int(parts[0]), int(parts[1])
            if start <= 1 <= end:
                week1_schedules.append(s)

print(f'\n包含第1周的课表数: {len(week1_schedules)}')

# 检查各周次的课表分布
print('\n各周次课表分布:')
for week in range(1, 19):
    count = 0
    for s in schedules:
        weeks_str = s.weeks
        if weeks_str:
            parts = weeks_str.split('-')
            if len(parts) == 2:
                start, end = int(parts[0]), int(parts[1])
                if start <= week <= end:
                    count += 1
    print(f'第{week}周: {count}条')
