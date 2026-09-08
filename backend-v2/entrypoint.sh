#!/bin/bash
set -e

echo "=========================================="
echo "🚀 LIMS 后端服务启动中..."
echo "=========================================="

# 等待数据库就绪
echo "[1/4] 等待数据库连接..."
max_retries=30
counter=0
until python -c "
import MySQLdb
import os
MySQLdb.connect(
    host=os.environ.get('DB_HOST', 'db'),
    user=os.environ.get('DB_USER'),
    passwd=os.environ.get('DB_PASSWORD'),
    db=os.environ.get('DB_NAME')
)
" 2>/dev/null; do
    counter=$((counter + 1))
    if [ $counter -ge $max_retries ]; then
        echo "❌ 数据库连接超时！"
        exit 1
    fi
    echo "    等待数据库就绪... ($counter/$max_retries)"
    sleep 2
done
echo "✅ 数据库连接成功"

# 执行数据库迁移
echo "[2/4] 执行数据库迁移..."
python manage.py migrate --noinput
echo "✅ 数据库迁移完成"

# 收集静态文件
echo "[3/4] 收集静态文件..."
python manage.py collectstatic --noinput --clear
echo "✅ 静态文件收集完成"

# 创建超级管理员（如果不存在）
echo "[4/4] 检查初始化数据..."
python -c "
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lims.settings.production')
django.setup()

from apps.users.models import User, Department
from apps.schedules.models import Semester
from datetime import date

# 创建默认部门
departments = [
    {'name': '信息工程学院', 'code': 'INFO'},
    {'name': '机械工程学院', 'code': 'MECH'},
    {'name': '电气工程学院', 'code': 'ELEC'},
]
for dept_data in departments:
    Department.objects.get_or_create(code=dept_data['code'], defaults=dept_data)

# 创建超级管理员 (SYSTEM_ADMIN=32)
import secrets, string as _string
def _gen_password():
    alphabet = _string.ascii_letters + _string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(12))

admin_pwd = os.environ.get('ADMIN_INIT_PASSWORD') or _gen_password()
if not User.objects.filter(username='admin').exists():
    admin = User.objects.create_superuser(
        username='admin',
        password=admin_pwd,
        nickname='系统管理员',
        role=32
    )
    print(f'创建了系统管理员: admin / {admin_pwd}')
else:
    print('系统管理员已存在（口令未重置）')

# 创建校长用户 (SUPER_ADMIN=16)
wuhan_pwd = os.environ.get('SUPERADMIN_INIT_PASSWORD') or _gen_password()
if not User.objects.filter(username='wuhan').exists():
    wuhan = User.objects.create_user(
        username='wuhan',
        password=wuhan_pwd,
        nickname='校长',
        role=16
    )
    print(f'创建了校长用户: wuhan / {wuhan_pwd}')
else:
    print('校长用户已存在（口令未重置）')

# 创建当前学期（动态取当前学年，避免硬编码过期学期）
from datetime import date as _date
_today = _date.today()
_y = _today.year
if _today.month >= 9:
    sem_code = f'{_y}-{_y+1}-1'; sem_name = f'{_y}-{_y+1}学年第一学期'
    sem_start = _date(_y, 9, 1); sem_end = _date(_y+1, 1, 20)
else:
    sem_code = f'{_y-1}-{_y}-2'; sem_name = f'{_y-1}-{_y}学年第二学期'
    sem_start = _date(_y, 2, 20); sem_end = _date(_y, 7, 10)
Semester.objects.filter(is_current=True).update(is_current=False)
semester, created = Semester.objects.get_or_create(
    code=sem_code,
    defaults={'name': sem_name, 'start_date': sem_start, 'end_date': sem_end, 'is_current': True, 'total_weeks': 20}
)
print(f'当前学期: {semester.name}')
"
echo "✅ 初始化数据检查完成"

# 启动服务
echo "=========================================="
echo "✅ 所有准备工作完成，启动服务..."
echo "=========================================="

exec gunicorn lims.wsgi:application --bind 0.0.0.0:8000 --workers 4
