"""
数据导出服务
"""

import io
import csv
from datetime import datetime
from django.http import HttpResponse
from django.core.serializers.json import DjangoJSONEncoder
import json


class ExportService:
    """数据导出服务"""

    @classmethod
    def export_to_csv(cls, data: list, filename: str, fields: list = None) -> HttpResponse:
        output = io.StringIO()
        
        if data and not fields:
            fields = list(data[0].keys())
        
        writer = csv.DictWriter(output, fieldnames=fields)
        writer.writeheader()
        writer.writerows(data)
        
        output.seek(0)
        
        response = HttpResponse(output.getvalue(), content_type='text/csv; charset=utf-8-sig')
        response['Content-Disposition'] = f'attachment; filename="{filename}_{datetime.now().strftime("%Y%m%d")}.csv"'
        
        return response

    @classmethod
    def export_to_json(cls, data: list, filename: str) -> HttpResponse:
        json_data = json.dumps(data, cls=DjangoJSONEncoder, ensure_ascii=False, indent=2)
        
        response = HttpResponse(json_data, content_type='application/json')
        response['Content-Disposition'] = f'attachment; filename="{filename}_{datetime.now().strftime("%Y%m%d")}.json"'
        
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
        
        return cls.export_to_csv(data, '实训室列表')

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
        
        return cls.export_to_csv(data, '课表列表')

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
        
        return cls.export_to_csv(data, '使用记录')

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
        
        return cls.export_to_csv(data, '工单列表')

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
        
        return cls.export_to_csv(data, '设备列表')

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
        
        return cls.export_to_csv(data, '用户列表')

    @classmethod
    def export_statistics_report(cls, stats: dict) -> HttpResponse:
        output = io.StringIO()
        writer = csv.writer(output)
        
        writer.writerow(['综合统计报表'])
        writer.writerow(['导出时间', datetime.now().strftime('%Y-%m-%d %H:%M:%S')])
        writer.writerow([])
        
        writer.writerow(['=== 实训室统计 ==='])
        lab_stats = stats.get('laboratories', {})
        writer.writerow(['总数', lab_stats.get('total', 0)])
        writer.writerow(['可用数', lab_stats.get('available', 0)])
        writer.writerow(['总工位数', lab_stats.get('total_capacity', 0)])
        writer.writerow([])
        
        writer.writerow(['=== 课表统计 ==='])
        schedule_stats = stats.get('schedules', {})
        writer.writerow(['总数', schedule_stats.get('total', 0)])
        writer.writerow([])
        
        writer.writerow(['=== 使用记录统计 ==='])
        record_stats = stats.get('records', {})
        writer.writerow(['总数', record_stats.get('total', 0)])
        writer.writerow(['总课时', record_stats.get('total_class_hours', 0)])
        writer.writerow(['总学生人次', record_stats.get('total_students', 0)])
        writer.writerow([])
        
        writer.writerow(['=== 工单统计 ==='])
        order_stats = stats.get('work_orders', {})
        writer.writerow(['总数', order_stats.get('total', 0)])
        writer.writerow(['待处理', order_stats.get('pending', 0)])
        writer.writerow(['处理中', order_stats.get('processing', 0)])
        writer.writerow(['已完成', order_stats.get('completed', 0)])
        writer.writerow([])
        
        writer.writerow(['=== 设备统计 ==='])
        eq_stats = stats.get('equipment', {})
        writer.writerow(['总数', eq_stats.get('total', 0)])
        writer.writerow([])
        
        writer.writerow(['=== 使用率 ==='])
        usage_rate = stats.get('usage_rate', {})
        writer.writerow(['排课使用率', f"{usage_rate.get('schedule_rate', 0)}%"])
        writer.writerow(['记录使用率', f"{usage_rate.get('record_rate', 0)}%"])
        
        output.seek(0)
        
        response = HttpResponse(output.getvalue(), content_type='text/csv; charset=utf-8-sig')
        response['Content-Disposition'] = f'attachment; filename="综合统计报表_{datetime.now().strftime("%Y%m%d")}.csv"'
        
        return response
