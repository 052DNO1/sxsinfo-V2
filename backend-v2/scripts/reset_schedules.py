import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lims.settings.development')
django.setup()

from apps.schedules.models import Schedule

print('删除现有课表数据...')
count = Schedule.objects.all().delete()
print(f'已删除 {count} 条课表数据')
