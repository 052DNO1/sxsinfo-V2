"""
学期归档视图
"""

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema
from common.responses import ApiResponse
from apps.schedules.services.semester_service import SemesterService


class ArchiveSettingsView(APIView):
    """归档设置视图"""
    permission_classes = [IsAuthenticated]

    @extend_schema(description='获取归档设置')
    def get(self, request):
        service = SemesterService()
        result = service.get_archive_settings(requester=request.user)
        return ApiResponse.success(data=result)

    @extend_schema(description='保存归档设置')
    def post(self, request):
        retention_months = request.data.get('retention_months')
        
        service = SemesterService()
        result = service.save_archive_settings(
            requester=request.user,
            retention_months=retention_months
        )
        return ApiResponse.success(data=result, message=result.get('message', '设置已保存'))


class ManualCleanupView(APIView):
    """手动清理视图"""
    permission_classes = [IsAuthenticated]

    @extend_schema(description='手动清理过期归档')
    def post(self, request):
        service = SemesterService()
        result = service.manual_cleanup(requester=request.user)
        return ApiResponse.success(data=result, message=result['message'])


class ArchiveCurrentTermView(APIView):
    """归档当前学期记录视图"""
    permission_classes = [IsAuthenticated]

    @extend_schema(description='归档当前学期记录')
    def post(self, request):
        archive_types = request.data.get('archive_types', [])
        
        service = SemesterService()
        result = service.archive_current_term_records(
            requester=request.user,
            archive_types=archive_types
        )
        return ApiResponse.success(data=result, message=result['message'])


class ArchivedRecordsView(APIView):
    """查看归档记录视图"""
    permission_classes = [IsAuthenticated]

    @extend_schema(description='查看归档记录')
    def get(self, request, semester_id):
        record_type = request.query_params.get('type')
        department_id = request.query_params.get('department_id')
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 10))
        export_format = request.query_params.get('format')
        
        service = SemesterService()
        result = service.get_archived_records(
            requester=request.user,
            semester_id=semester_id,
            record_type=record_type,
            department_id=int(department_id) if department_id else None,
            page=page,
            page_size=page_size,
            export_format=export_format
        )
        
        if export_format in ['excel', 'pdf']:
            return result
        
        return ApiResponse.success(data=result)


class CheckTermStatusView(APIView):
    """检查学期状态视图"""
    permission_classes = [IsAuthenticated]

    @extend_schema(description='检查学期状态')
    def get(self, request):
        service = SemesterService()
        result = service.check_term_status(requester=request.user)
        return ApiResponse.success(data=result)
