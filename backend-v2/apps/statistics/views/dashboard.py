"""
仪表板视图
"""

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema
from common.responses import ApiResponse
from apps.statistics.services.statistics_service import StatisticsService


class UserManagementDashboardView(APIView):
    """用户管理仪表板视图"""
    permission_classes = [IsAuthenticated]

    @extend_schema(description='获取用户管理仪表板数据')
    def get(self, request):
        user = request.user
        
        if not (user.is_super_admin or user.is_department_admin):
            return ApiResponse.error(message='您没有访问用户管理的权限', code=403)
        
        return ApiResponse.success(data={
            'user': {
                'id': user.id,
                'username': user.username,
                'nickname': user.nickname,
                'is_super_admin': user.is_super_admin,
                'is_dept_admin': user.is_department_admin,
                'is_lab_admin': user.is_laboratory_admin,
                'is_teacher': user.is_teacher,
            }
        })


class LabResourceDashboardView(APIView):
    """实训室与资源管理仪表板视图"""
    permission_classes = [IsAuthenticated]

    @extend_schema(description='获取实训室资源管理仪表板数据')
    def get(self, request):
        user = request.user
        
        if not (user.is_super_admin or user.is_department_admin or user.is_laboratory_admin):
            return ApiResponse.error(message='您没有访问实训室管理的权限', code=403)
        
        return ApiResponse.success(data={
            'user': {
                'id': user.id,
                'username': user.username,
                'nickname': user.nickname,
                'is_super_admin': user.is_super_admin,
                'is_dept_admin': user.is_department_admin,
                'is_lab_admin': user.is_laboratory_admin,
                'is_teacher': user.is_teacher,
            }
        })


class SchedulingDashboardView(APIView):
    """排课与教室管理仪表板视图"""
    permission_classes = [IsAuthenticated]

    @extend_schema(description='获取排课管理仪表板数据')
    def get(self, request):
        user = request.user
        
        if not (user.is_super_admin or user.is_department_admin or user.is_laboratory_admin or user.is_teacher):
            return ApiResponse.error(message='您没有访问排课管理的权限', code=403)
        
        return ApiResponse.success(data={
            'user': {
                'id': user.id,
                'username': user.username,
                'nickname': user.nickname,
                'is_super_admin': user.is_super_admin,
                'is_dept_admin': user.is_department_admin,
                'is_lab_admin': user.is_laboratory_admin,
                'is_teacher': user.is_teacher,
            }
        })


class PersonalTeachingDashboardView(APIView):
    """个人教学中心仪表板视图"""
    permission_classes = [IsAuthenticated]

    @extend_schema(description='获取个人教学中心仪表板数据')
    def get(self, request):
        user = request.user
        
        if not user.is_teacher:
            return ApiResponse.error(message='您没有访问个人教学中心的权限', code=403)
        
        return ApiResponse.success(data={
            'user': {
                'id': user.id,
                'username': user.username,
                'nickname': user.nickname,
                'is_super_admin': user.is_super_admin,
                'is_dept_admin': user.is_department_admin,
                'is_lab_admin': user.is_laboratory_admin,
                'is_teacher': user.is_teacher,
            }
        })


class ComprehensiveStatsView(APIView):
    """综合统计视图"""
    permission_classes = [IsAuthenticated]

    @extend_schema(description='获取综合统计数据')
    def get(self, request):
        service = StatisticsService()
        result = service.get_comprehensive_stats(requester=request.user)
        return ApiResponse.success(data=result)


class ExportComprehensiveStatsView(APIView):
    """导出综合统计报表视图"""
    permission_classes = [IsAuthenticated]

    @extend_schema(description='导出综合统计报表')
    def post(self, request):
        service = StatisticsService()
        return service.export_comprehensive_stats(requester=request.user)
