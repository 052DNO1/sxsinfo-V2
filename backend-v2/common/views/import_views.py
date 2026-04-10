"""
数据导入视图
"""

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema
from common.responses import ApiResponse
from common.services.import_service import ImportService


class ImportLaboratoriesView(APIView):
    """导入实训室"""
    permission_classes = [IsAuthenticated]

    @extend_schema(description='导入实训室数据')
    def post(self, request):
        file_obj = request.FILES.get('file')
        if not file_obj:
            return ApiResponse.error(message='请上传文件')
        
        result = ImportService.import_laboratories(
            requester=request.user,
            file_data=file_obj
        )
        
        message = f"成功导入 {result['success_count']} 个实训室"
        if result['failed_count'] > 0:
            message += f"，{result['failed_count']} 条失败"
        
        return ApiResponse.success(data=result, message=message)


class ImportSchedulesView(APIView):
    """导入课表"""
    permission_classes = [IsAuthenticated]

    @extend_schema(description='导入课表数据')
    def post(self, request):
        file_obj = request.FILES.get('file')
        if not file_obj:
            return ApiResponse.error(message='请上传文件')
        
        result = ImportService.import_schedules(
            requester=request.user,
            file_data=file_obj
        )
        
        message = f"成功导入 {result['success_count']} 条课表"
        if result['failed_count'] > 0:
            message += f"，{result['failed_count']} 条失败"
        
        return ApiResponse.success(data=result, message=message)


class ImportEquipmentView(APIView):
    """导入设备"""
    permission_classes = [IsAuthenticated]

    @extend_schema(description='导入设备数据')
    def post(self, request):
        file_obj = request.FILES.get('file')
        if not file_obj:
            return ApiResponse.error(message='请上传文件')
        
        result = ImportService.import_equipment(
            requester=request.user,
            file_data=file_obj
        )
        
        message = f"成功导入 {result['success_count']} 台设备"
        if result['failed_count'] > 0:
            message += f"，{result['failed_count']} 条失败"
        
        return ApiResponse.success(data=result, message=message)
