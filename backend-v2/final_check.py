import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lims.settings.development')
django.setup()

from django.db import connection
from apps.laboratories.models import Laboratory

# 检查3625
print("=== 检查编号3625 ===")
with connection.cursor() as cursor:
    cursor.execute("SELECT id, name, code, is_deleted FROM laboratories WHERE code = '3625'")
    row = cursor.fetchone()
    if row:
        print(f"找到: ID={row[0]}, Name={row[1]}, Code={row[2]}, is_deleted={row[3]}")
    else:
        print("3625 不存在")

# 检查ID=47
print("\n=== 检查ID=47 ===")
with connection.cursor() as cursor:
    cursor.execute("SELECT id, name, code, is_deleted FROM laboratories WHERE id = 47")
    row = cursor.fetchone()
    if row:
        print(f"找到: ID={row[0]}, Name={row[1]}, Code={row[2]}, is_deleted={row[3]}")
    else:
        print("ID=47 不存在")

# 列出所有实验室
print("\n=== 所有实验室列表 ===")
labs = Laboratory.objects.filter(is_deleted=False).order_by('id')
for lab in labs:
    print(f"ID: {lab.id}, Code: {lab.code}, Name: {lab.name}")
print(f"\n总数(未删除): {labs.count()}")
