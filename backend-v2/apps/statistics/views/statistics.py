"""
统计视图
"""

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema
from common.responses import ApiResponse
from apps.statistics.services.statistics_service import StatisticsService


class DashboardStatsView(APIView):
    """仪表板统计视图"""
    permission_classes = [IsAuthenticated]

    @extend_schema(description='获取仪表板统计数据')
    def get(self, request):
        service = StatisticsService()
        result = service.get_dashboard_stats(requester=request.user)
        return ApiResponse.success(data=result)


class TeacherStatsView(APIView):
    """教师统计视图"""
    permission_classes = [IsAuthenticated]

    @extend_schema(description='获取教师个人统计数据')
    def get(self, request):
        service = StatisticsService()
        result = service.get_teacher_stats(requester=request.user)
        return ApiResponse.success(data={'stats': result})


class LaboratoryAdminStatsView(APIView):
    """实训室管理员统计视图"""
    permission_classes = [IsAuthenticated]

    @extend_schema(description='获取实训室管理员统计数据')
    def get(self, request):
        service = StatisticsService()
        result = service.get_laboratory_admin_stats(requester=request.user)
        return ApiResponse.success(data={'stats': result})


class SuperAdminStatsView(APIView):
    """超级管理员统计视图"""
    permission_classes = [IsAuthenticated]

    @extend_schema(description='获取超级管理员统计数据')
    def get(self, request):
        if not request.user.is_super_admin:
            return ApiResponse.error(message='只有超级管理员可以访问', code=403)
        
        service = StatisticsService()
        result = service.get_super_admin_stats(requester=request.user)
        return ApiResponse.success(data={'stats': result})


class SystemSuperuserStatsView(APIView):
    """系统超级用户统计视图（Django内置is_superuser）"""
    permission_classes = [IsAuthenticated]

    @extend_schema(description='获取系统超级用户统计数据')
    def get(self, request):
        if not request.user.is_superuser:
            return ApiResponse.error(message='只有系统超级用户可以访问', code=403)
        
        service = StatisticsService()
        result = service.get_system_superuser_stats(requester=request.user)
        return ApiResponse.success(data={'stats': result})
