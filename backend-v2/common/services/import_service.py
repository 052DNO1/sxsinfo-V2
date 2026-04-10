"""
导入服务
"""

import csv
import io
from django.db import transaction
from apps.core.exceptions import ValidationError, PermissionDenied
from apps.laboratories.models import Laboratory
from apps.schedules.models import Schedule, Semester
from apps.laboratories.models import Equipment
from apps.users.models import User, Department


class ImportService:
    """导入服务"""

    @classmethod
    @transaction.atomic
    def import_laboratories(cls, requester, file_data) -> dict:
        if not requester.is_department_admin and not requester.is_super_admin:
            raise PermissionDenied('无权限导入实训室')
        
        try:
            decoded_file = file_data.read().decode('utf-8')
            reader = csv.DictReader(io.StringIO(decoded_file))
        except Exception as e:
            raise ValidationError(f'文件解析失败: {str(e)}')
        
        success_count = 0
        failed_list = []
        
        for row_num, row in enumerate(reader, start=2):
            try:
                code = row.get('code', '').strip()
                name = row.get('name', '').strip()
                
                if not code or not name:
                    failed_list.append({'row': row_num, 'reason': '编号或名称为空'})
                    continue
                
                if Laboratory.objects.filter(code=code).exists():
                    failed_list.append({'row': row_num, 'reason': f'编号 "{code}" 已存在'})
                    continue
                
                department_name = row.get('department', '').strip()
                department_id = None
                if department_name:
                    dept = Department.objects.filter(name=department_name).first()
                    if dept:
                        department_id = dept.id
                
                if not requester.is_super_admin:
                    department_id = requester.department_id
                
                Laboratory.objects.create(
                    name=name,
                    code=code,
                    building=row.get('building', '').strip(),
                    floor=row.get('floor', '').strip(),
                    room_number=row.get('room_number', '').strip(),
                    capacity=int(row.get('capacity', 30)),
                    area=row.get('area', '').strip(),
                    laboratory_type=row.get('laboratory_type', '普通实训室').strip(),
                    department_id=department_id,
                    note=row.get('note', '').strip(),
                )
                success_count += 1
                
            except Exception as e:
                failed_list.append({'row': row_num, 'reason': str(e)})
        
        return {
            'success_count': success_count,
            'failed_count': len(failed_list),
            'failed_list': failed_list,
        }

    @classmethod
    @transaction.atomic
    def import_schedules(cls, requester, file_data) -> dict:
        if not requester.is_department_admin and not requester.is_super_admin and not requester.is_laboratory_admin:
            raise PermissionDenied('无权限导入课表')
        
        try:
            decoded_file = file_data.read().decode('utf-8')
            reader = csv.DictReader(io.StringIO(decoded_file))
        except Exception as e:
            raise ValidationError(f'文件解析失败: {str(e)}')
        
        success_count = 0
        failed_list = []
        
        semester = Semester.get_current()
        if not semester:
            raise ValidationError('未设置当前学期')
        
        for row_num, row in enumerate(reader, start=2):
            try:
                course_name = row.get('course_name', '').strip()
                laboratory_code = row.get('laboratory_code', '').strip()
                weekday = row.get('weekday', '').strip()
                
                if not course_name or not laboratory_code or not weekday:
                    failed_list.append({'row': row_num, 'reason': '课程名称、实训室编号或星期为空'})
                    continue
                
                try:
                    laboratory = Laboratory.objects.get(code=laboratory_code, is_deleted=False)
                except Laboratory.DoesNotExist:
                    failed_list.append({'row': row_num, 'reason': f'实训室编号 "{laboratory_code}" 不存在'})
                    continue
                
                Schedule.objects.create(
                    course_name=course_name,
                    course_code=row.get('course_code', '').strip(),
                    weekday=int(weekday),
                    time_slot=row.get('time_slot', '1-4').strip(),
                    weeks=row.get('weeks', '1-18').strip(),
                    laboratory=laboratory,
                    semester=semester,
                    teacher_name=row.get('teacher_name', '').strip(),
                    class_name=row.get('class_name', '').strip(),
                    student_count=int(row.get('student_count', 0)),
                    note=row.get('note', '').strip(),
                )
                success_count += 1
                
            except Exception as e:
                failed_list.append({'row': row_num, 'reason': str(e)})
        
        return {
            'success_count': success_count,
            'failed_count': len(failed_list),
            'failed_list': failed_list,
        }

    @classmethod
    @transaction.atomic
    def import_equipment(cls, requester, file_data) -> dict:
        if not requester.is_department_admin and not requester.is_super_admin and not requester.is_laboratory_admin:
            raise PermissionDenied('无权限导入设备')
        
        try:
            decoded_file = file_data.read().decode('utf-8')
            reader = csv.DictReader(io.StringIO(decoded_file))
        except Exception as e:
            raise ValidationError(f'文件解析失败: {str(e)}')
        
        success_count = 0
        failed_list = []
        
        for row_num, row in enumerate(reader, start=2):
            try:
                code = row.get('code', '').strip()
                name = row.get('name', '').strip()
                
                if not code or not name:
                    failed_list.append({'row': row_num, 'reason': '编号或名称为空'})
                    continue
                
                laboratory_code = row.get('laboratory_code', '').strip()
                laboratory_id = None
                if laboratory_code:
                    try:
                        lab = Laboratory.objects.get(code=laboratory_code, is_deleted=False)
                        laboratory_id = lab.id
                    except Laboratory.DoesNotExist:
                        failed_list.append({'row': row_num, 'reason': f'实训室编号 "{laboratory_code}" 不存在'})
                        continue
                
                Equipment.objects.create(
                    name=name,
                    code=code,
                    category=row.get('category', '计算机').strip(),
                    brand=row.get('brand', '').strip(),
                    model=row.get('model', '').strip(),
                    serial_number=row.get('serial_number', '').strip(),
                    laboratory_id=laboratory_id,
                    position=row.get('position', '').strip(),
                    cpu=row.get('cpu', '').strip(),
                    memory=row.get('memory', '').strip(),
                    disk=row.get('disk', '').strip(),
                    gpu=row.get('gpu', '').strip(),
                    os=row.get('os', '').strip(),
                    supplier=row.get('supplier', '').strip(),
                    note=row.get('note', '').strip(),
                )
                success_count += 1
                
            except Exception as e:
                failed_list.append({'row': row_num, 'reason': str(e)})
        
        return {
            'success_count': success_count,
            'failed_count': len(failed_list),
            'failed_list': failed_list,
        }
