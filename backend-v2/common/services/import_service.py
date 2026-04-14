"""
导入服务
"""

import io
from django.db import transaction
from openpyxl import load_workbook
from apps.core.exceptions import ValidationError, PermissionDenied
from apps.laboratories.models import Laboratory
from apps.schedules.models import Schedule, Semester
from apps.laboratories.models import Equipment
from apps.users.models import User, Department


class ImportService:
    """导入服务"""

    @staticmethod
    def _parse_excel(file_data):
        """解析 Excel 文件"""
        wb = load_workbook(filename=io.BytesIO(file_data.read()))
        ws = wb.active
        rows = list(ws.iter_rows(values_only=True))
        
        if len(rows) < 2:
            raise ValidationError('文件内容为空或只有表头')
        
        header_row = rows[0]
        header_map = {str(h).strip(): idx for idx, h in enumerate(header_row) if h}
        
        def get_value(row, *keys):
            for key in keys:
                if key in header_map:
                    val = row[header_map[key]]
                    return str(val).strip() if val is not None else ''
            return ''
        
        return rows[1:], get_value

    @classmethod
    @transaction.atomic
    def import_laboratories(cls, requester, file_data) -> dict:
        if not requester.is_department_admin and not requester.is_super_admin:
            raise PermissionDenied('无权限导入实训室')
        
        try:
            data_rows, get_value = cls._parse_excel(file_data)
        except Exception as e:
            raise ValidationError(f'文件解析失败: {str(e)}')
        
        success_count = 0
        failed_list = []
        
        for row_num, row in enumerate(data_rows, start=2):
            try:
                name = get_value(row, '实训室名称', 'name')
                code = get_value(row, '门牌号', 'code')
                
                if not code or not name:
                    failed_list.append({'row': row_num, 'reason': '门牌号或名称为空'})
                    continue
                
                if Laboratory.objects.filter(code=code).exists():
                    failed_list.append({'row': row_num, 'reason': f'门牌号 "{code}" 已存在'})
                    continue
                
                department_name = get_value(row, '所属部门', 'department')
                department_id = None
                if department_name:
                    dept = Department.objects.filter(name=department_name).first()
                    if dept:
                        department_id = dept.id
                
                if not requester.is_super_admin:
                    department_id = requester.department_id
                
                capacity_str = get_value(row, '工位', 'capacity')
                capacity = int(capacity_str) if capacity_str.isdigit() else 30
                
                Laboratory.objects.create(
                    name=name,
                    code=code,
                    capacity=capacity,
                    department_id=department_id,
                    note=get_value(row, '备注', 'note'),
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
    def import_schedules(cls, requester, file_data, laboratory_id=None) -> dict:
        if not requester.is_department_admin and not requester.is_super_admin and not requester.is_laboratory_admin:
            raise PermissionDenied('无权限导入课表')
        
        try:
            data_rows, get_value = cls._parse_excel(file_data)
        except Exception as e:
            raise ValidationError(f'文件解析失败: {str(e)}')
        
        success_count = 0
        failed_list = []
        
        semester = Semester.get_current()
        if not semester:
            raise ValidationError('未设置当前学期')
        
        for row_num, row in enumerate(data_rows, start=2):
            try:
                course_name = get_value(row, '课程名称', 'course_name')
                laboratory_name = get_value(row, '实训室名称', 'laboratory_name')
                weekday_str = get_value(row, '星期', 'weekday')
                
                if not course_name or not weekday_str:
                    failed_list.append({'row': row_num, 'reason': '课程名称或星期为空'})
                    continue
                
                if laboratory_id:
                    try:
                        laboratory = Laboratory.objects.get(id=laboratory_id, is_deleted=False)
                    except Laboratory.DoesNotExist:
                        failed_list.append({'row': row_num, 'reason': '指定的实训室不存在'})
                        continue
                elif laboratory_name:
                    try:
                        laboratory = Laboratory.objects.get(name=laboratory_name, is_deleted=False)
                    except Laboratory.DoesNotExist:
                        failed_list.append({'row': row_num, 'reason': f'实训室 "{laboratory_name}" 不存在'})
                        continue
                else:
                    failed_list.append({'row': row_num, 'reason': '未指定实训室'})
                    continue
                
                weekday = int(weekday_str) if weekday_str.isdigit() else 1
                
                Schedule.objects.create(
                    course_name=course_name,
                    weekday=weekday,
                    time_slot=get_value(row, '节次', 'time_slot') or '1-4',
                    weeks=get_value(row, '周次', 'weeks') or '1-18',
                    laboratory=laboratory,
                    semester=semester,
                    teacher_name=get_value(row, '任课教师', 'teacher_name'),
                    class_name=get_value(row, '上课班级', 'class_name'),
                    student_count=int(get_value(row, '人数', 'student_count') or 0),
                    note=get_value(row, '备注', 'note'),
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
            data_rows, get_value = cls._parse_excel(file_data)
        except Exception as e:
            raise ValidationError(f'文件解析失败: {str(e)}')
        
        success_count = 0
        failed_list = []
        
        for row_num, row in enumerate(data_rows, start=2):
            try:
                code = get_value(row, '电脑编号', 'code')
                name = get_value(row, '设备名称', 'name')
                
                if not code:
                    failed_list.append({'row': row_num, 'reason': '电脑编号为空'})
                    continue
                
                laboratory_name = get_value(row, '实训室名称', 'laboratory_name')
                laboratory_id = None
                if laboratory_name:
                    try:
                        lab = Laboratory.objects.get(name=laboratory_name, is_deleted=False)
                        laboratory_id = lab.id
                    except Laboratory.DoesNotExist:
                        failed_list.append({'row': row_num, 'reason': f'实训室 "{laboratory_name}" 不存在'})
                        continue
                
                Equipment.objects.create(
                    name=name or code,
                    code=code,
                    brand=get_value(row, '品牌', 'brand'),
                    model=get_value(row, '型号', 'model'),
                    laboratory_id=laboratory_id,
                    cpu=get_value(row, 'CPU', 'cpu'),
                    memory=get_value(row, '内存', 'memory'),
                    disk=get_value(row, '硬盘', 'disk'),
                    note=get_value(row, '备注', 'note'),
                )
                success_count += 1
                
            except Exception as e:
                failed_list.append({'row': row_num, 'reason': str(e)})
        
        return {
            'success_count': success_count,
            'failed_count': len(failed_list),
            'failed_list': failed_list,
        }
