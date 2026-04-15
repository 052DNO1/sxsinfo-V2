import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lims.settings.development')
django.setup()

from apps.schedules.models import Schedule
from apps.schedules.serializers import ScheduleSerializer

# 获取一个实训室的课表
schedules = Schedule.objects.filter(laboratory_id=15)[:5]
print(f'找到 {schedules.count()} 条课表')

serializer = ScheduleSerializer(schedules, many=True)
print('\n序列化后的数据:')
for item in serializer.data:
    print(f"  ID: {item['id']}, 课程: {item['course_name']}, weekday: {item['weekday']}, time_slot: {item['time_slot']}, weeks: {item['weeks']}")
