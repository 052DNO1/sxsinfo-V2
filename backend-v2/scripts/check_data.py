import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lims.settings.development')
django.setup()

from apps.schedules.models import Schedule
from apps.laboratories.models import Laboratory

print('='*60)
print('课表数据 (前10条)')
print('='*60)
schedules = Schedule.objects.all()[:10]
for s in schedules:
    print(f'ID: {s.id}, 课程: {s.course_name}, 实训室ID: {s.laboratory_id}, weekday: {s.weekday}, time_slot: {s.time_slot}, weeks: {s.weeks}')

print()
print('='*60)
print('实训室列表')
print('='*60)
labs = Laboratory.objects.all()[:20]
for lab in labs:
    print(f'ID: {lab.id}, 名称: {lab.name}, code: {lab.code}')

print()
print('='*60)
print('按实训室统计课表数量')
print('='*60)
for lab in labs:
    count = Schedule.objects.filter(laboratory=lab).count()
    if count > 0:
        print(f'{lab.name}: {count}条')
