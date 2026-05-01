"""
数据导出服务 - Excel导出
"""

import io
import urllib.parse
from datetime import datetime
from django.http import HttpResponse
from django.utils import timezone
from apps.core.utils import beijing_strftime, beijing_now, beijing_today

try:
    import pandas as pd
except ImportError:
    pd = None


class ExportService:
    """数据导出服务"""

    EXCEL_CONTENT_TYPE = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'

    @classmethod
    def _check_pandas(cls):
        if pd is None:
            raise ImportError('请安装pandas库以支持Excel导出功能: pip install pandas openpyxl')

    @classmethod
    def export_to_excel(cls, data: list, filename: str, sheet_name: str = '数据') -> HttpResponse:
        cls._check_pandas()
        
        output = io.BytesIO()
        
        df = pd.DataFrame(data)
        df.to_excel(output, sheet_name=sheet_name, index=False, engine='openpyxl')
        
        output.seek(0)
        
        full_filename = f'{filename}_{beijing_now().strftime("%Y%m%d")}.xlsx'
        encoded_filename = urllib.parse.quote(full_filename)
        
        response = HttpResponse(
            output.getvalue(),
            content_type=cls.EXCEL_CONTENT_TYPE
        )
        response['Content-Disposition'] = f"attachment; filename*=UTF-8''{encoded_filename}"
        
        return response

    @classmethod
    def export_multi_sheet_excel(cls, sheets: dict, filename: str) -> HttpResponse:
        cls._check_pandas()
        
        output = io.BytesIO()
        
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            for sheet_name, data in sheets.items():
                if data:
                    df = pd.DataFrame(data)
                    df.to_excel(writer, sheet_name=sheet_name, index=False)
        
        output.seek(0)
        
        full_filename = f'{filename}_{beijing_now().strftime("%Y%m%d")}.xlsx'
        encoded_filename = urllib.parse.quote(full_filename)
        
        response = HttpResponse(
            output.getvalue(),
            content_type=cls.EXCEL_CONTENT_TYPE
        )
        response['Content-Disposition'] = f"attachment; filename*=UTF-8''{encoded_filename}"
        
        return response

    @classmethod
    def export_laboratories(cls, laboratories: list) -> HttpResponse:
        data = []
        for lab in laboratories:
            data.append({
                '实训室名称': lab.get('name', ''),
                '实训室编号': lab.get('code', ''),
                '所在楼栋': lab.get('building', ''),
                '房间号': lab.get('room_number', ''),
                '工位数': lab.get('capacity', 0),
                '类型': lab.get('laboratory_type', ''),
                '所属部门': lab.get('department_name', ''),
                '管理员': lab.get('admin_name', ''),
                '状态': lab.get('status_display', ''),
                '备注': lab.get('note', ''),
            })
        
        return cls.export_to_excel(data, '实训室列表', '实训室')

    @classmethod
    def export_schedules(cls, schedules: list) -> HttpResponse:
        data = []
        for schedule in schedules:
            data.append({
                '课程名称': schedule.get('course_name', ''),
                '课程代码': schedule.get('course_code', ''),
                '星期': schedule.get('weekday_display', ''),
                '节次': schedule.get('time_slot', ''),
                '周次': schedule.get('weeks', ''),
                '实训室': schedule.get('laboratory_name', ''),
                '教师': schedule.get('teacher_name', ''),
                '班级': schedule.get('class_name', ''),
                '学生人数': schedule.get('student_count', 0),
                '学期': schedule.get('semester_name', ''),
            })
        
        return cls.export_to_excel(data, '课表列表', '课表')

    @classmethod
    def export_records(cls, records: list) -> HttpResponse:
        data = []
        for record in records:
            data.append({
                '使用日期': record.get('usage_date', ''),
                '节次': record.get('time_slot', ''),
                '课时数': record.get('class_hours', 0),
                '实训室': record.get('laboratory_name', ''),
                '教师': record.get('teacher_name', ''),
                '班级': record.get('class_name', ''),
                '学生人数': record.get('student_count', 0),
                '使用内容': record.get('content', ''),
                '设备状态': record.get('device_status', ''),
                '实训室状态': record.get('laboratory_status', ''),
                '备注': record.get('note', ''),
            })
        
        return cls.export_to_excel(data, '使用记录', '使用记录')

    @classmethod
    def export_work_orders(cls, work_orders: list) -> HttpResponse:
        data = []
        for order in work_orders:
            data.append({
                '工单标题': order.get('title', ''),
                '实训室': order.get('laboratory_name', ''),
                '维护类型': order.get('maintenance_type_display', ''),
                '状态': order.get('status_display', ''),
                '优先级': order.get('priority', ''),
                '上报人': order.get('reporter_name', ''),
                '处理人': order.get('handler_name', ''),
                '上报时间': order.get('reported_at', ''),
                '完成时间': order.get('completed_at', ''),
                '问题描述': order.get('description', ''),
                '解决方案': order.get('solution', ''),
            })
        
        return cls.export_to_excel(data, '工单列表', '工单')

    @classmethod
    def export_equipment(cls, equipment_list: list) -> HttpResponse:
        data = []
        for eq in equipment_list:
            data.append({
                '设备名称': eq.get('name', ''),
                '设备编号': eq.get('code', ''),
                '类别': eq.get('category', ''),
                '品牌': eq.get('brand', ''),
                '型号': eq.get('model', ''),
                '序列号': eq.get('serial_number', ''),
                '所属实训室': eq.get('laboratory_name', ''),
                '位置': eq.get('position', ''),
                '状态': eq.get('status', ''),
                '购买日期': eq.get('purchase_date', ''),
                '保修到期': eq.get('warranty_expire', ''),
                '价格': eq.get('price', ''),
                '供应商': eq.get('supplier', ''),
            })
        
        return cls.export_to_excel(data, '设备列表', '设备')

    @classmethod
    def export_users(cls, users: list) -> HttpResponse:
        data = []
        for user in users:
            data.append({
                '用户名': user.get('username', ''),
                '姓名': user.get('nickname', ''),
                '邮箱': user.get('email', ''),
                '手机号': user.get('phone', ''),
                '角色': user.get('role_display', ''),
                '所属部门': user.get('department_name', ''),
                '状态': '激活' if user.get('is_active') else '停用',
                '创建时间': user.get('created_at', ''),
            })
        
        return cls.export_to_excel(data, '用户列表', '用户')

    @classmethod
    def export_statistics_report(cls, stats: dict) -> HttpResponse:
        cls._check_pandas()
        
        output = io.BytesIO()
        
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            overview_data = [
                ['统计项', '数值', '说明'],
                ['导出时间', beijing_now().strftime('%Y-%m-%d %H:%M:%S'), ''],
                ['', '', ''],
                ['实训室总数', stats.get('laboratories', {}).get('total', 0), '间'],
                ['实训室可用数', stats.get('laboratories', {}).get('available', 0), '间'],
                ['实训室总工位数', stats.get('laboratories', {}).get('total_capacity', 0), '人'],
                ['', '', ''],
                ['课表总数', stats.get('schedules', {}).get('total', 0), '门'],
                ['', '', ''],
                ['使用记录总数', stats.get('records', {}).get('total', 0), '条'],
                ['总课时', stats.get('records', {}).get('total_class_hours', 0), '节'],
                ['总学生人次', stats.get('records', {}).get('total_students', 0), '人次'],
                ['', '', ''],
                ['工单总数', stats.get('work_orders', {}).get('total', 0), '条'],
                ['待处理', stats.get('work_orders', {}).get('pending', 0), '条'],
                ['处理中', stats.get('work_orders', {}).get('processing', 0), '条'],
                ['已完成', stats.get('work_orders', {}).get('completed', 0), '条'],
                ['', '', ''],
                ['设备总数', stats.get('equipment', {}).get('total', 0), '台'],
                ['', '', ''],
                ['排课使用率', f"{stats.get('usage_rate', {}).get('schedule_rate', 0)}%", ''],
                ['记录使用率', f"{stats.get('usage_rate', {}).get('record_rate', 0)}%", '最近30天'],
            ]
            pd.DataFrame(overview_data).to_excel(writer, sheet_name='概览', index=False, header=False)
        
        output.seek(0)
        
        full_filename = f'综合统计报表_{beijing_now().strftime("%Y%m%d")}.xlsx'
        encoded_filename = urllib.parse.quote(full_filename)
        
        response = HttpResponse(
            output.getvalue(),
            content_type=cls.EXCEL_CONTENT_TYPE
        )
        response['Content-Disposition'] = f"attachment; filename*=UTF-8''{encoded_filename}"
        
        return response
