"""
数据导出视图
"""

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema
from common.responses import ApiResponse
from common.services.export_service import ExportService
from apps.laboratories.services import LaboratoryService
from apps.schedules.services import ScheduleService
from apps.records.services import UsageRecordService
from apps.maintenance.services import WorkOrderService
from apps.laboratories.services import EquipmentService
from apps.users.services import UserService
from apps.statistics.services import StatisticsService


class ExportLaboratoriesView(APIView):
    """导出实训室"""
    permission_classes = [IsAuthenticated]

    @extend_schema(description='导出实训室数据')
    def get(self, request):
        service = LaboratoryService()
        result = service.get_laboratory_list(
            requester=request.user,
            department_id=request.query_params.get('department_id'),
            status=request.query_params.get('status'),
            search=request.query_params.get('search'),
            page=1,
            page_size=10000,
            no_page=True
        )
        
        return ExportService.export_laboratories(result['list'])


class ExportSchedulesView(APIView):
    """导出课表"""
    permission_classes = [IsAuthenticated]

    @extend_schema(description='导出课表数据')
    def get(self, request):
        service = ScheduleService()
        result = service.get_schedule_list(
            requester=request.user,
            laboratory_id=request.query_params.get('laboratory_id'),
            semester_id=request.query_params.get('semester_id'),
            search=request.query_params.get('search'),
            page=1,
            page_size=10000,
            no_page=True
        )
        
        return ExportService.export_schedules(result['list'])


class ExportRecordsView(APIView):
    """导出使用记录"""
    permission_classes = [IsAuthenticated]

    @extend_schema(description='导出使用记录数据')
    def get(self, request):
        service = UsageRecordService()
        result = service.get_record_list(
            requester=request.user,
            laboratory_id=request.query_params.get('laboratory_id'),
            semester_id=request.query_params.get('semester_id'),
            start_date=request.query_params.get('start_date'),
            end_date=request.query_params.get('end_date'),
            search=request.query_params.get('search'),
            page=1,
            page_size=10000,
            no_page=True
        )
        
        return ExportService.export_records(result['list'])


class ExportWorkOrdersView(APIView):
    """导出工单"""
    permission_classes = [IsAuthenticated]

    @extend_schema(description='导出工单数据')
    def get(self, request):
        service = WorkOrderService()
        result = service.get_work_order_list(
            requester=request.user,
            laboratory_id=request.query_params.get('laboratory_id'),
            status=request.query_params.get('status'),
            search=request.query_params.get('search'),
            page=1,
            page_size=10000,
            no_page=True
        )
        
        return ExportService.export_work_orders(result['list'])


class ExportEquipmentView(APIView):
    """导出设备"""
    permission_classes = [IsAuthenticated]

    @extend_schema(description='导出设备数据')
    def get(self, request):
        service = EquipmentService()
        result = service.get_equipment_list(
            requester=request.user,
            laboratory_id=request.query_params.get('laboratory_id'),
            category=request.query_params.get('category'),
            status=request.query_params.get('status'),
            search=request.query_params.get('search'),
            page=1,
            page_size=10000,
            no_page=True
        )
        
        return ExportService.export_equipment(result['list'])


class ExportUsersView(APIView):
    """导出用户"""
    permission_classes = [IsAuthenticated]

    @extend_schema(description='导出用户数据')
    def get(self, request):
        if not request.user.is_department_admin and not request.user.is_super_admin:
            return ApiResponse.error(message='无权限导出用户', code=403)
        
        service = UserService()
        result = service.get_user_list(
            requester=request.user,
            department_id=request.query_params.get('department_id'),
            role=request.query_params.get('role'),
            search=request.query_params.get('search'),
            page=1,
            page_size=10000,
            no_page=True
        )
        
        return ExportService.export_users(result['list'])


class ExportStatisticsReportView(APIView):
    """导出统计报表"""
    permission_classes = [IsAuthenticated]

    @extend_schema(description='导出综合统计报表')
    def get(self, request):
        service = StatisticsService()
        stats = service.get_dashboard_stats(requester=request.user)
        
        return ExportService.export_statistics_report(stats)
