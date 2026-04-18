"""
统计路由
"""

from django.urls import path
from apps.statistics.views import (
    DashboardStatsView, TeacherStatsView,
    LaboratoryAdminStatsView, SuperAdminStatsView,
    SystemSuperuserStatsView,
    UserManagementDashboardView, LabResourceDashboardView,
    SchedulingDashboardView, PersonalTeachingDashboardView,
    ComprehensiveStatsView, ExportComprehensiveStatsView
)

urlpatterns = [
    path('dashboard/', DashboardStatsView.as_view(), name='dashboard-stats'),
    path('teacher/', TeacherStatsView.as_view(), name='teacher-stats'),
    path('laboratory-admin/', LaboratoryAdminStatsView.as_view(), name='lab-admin-stats'),
    path('super-admin/', SuperAdminStatsView.as_view(), name='super-admin-stats'),
    path('system-superuser/', SystemSuperuserStatsView.as_view(), name='system-superuser-stats'),
    
    path('user-management/', UserManagementDashboardView.as_view(), name='user-management-dashboard'),
    path('lab-resource/', LabResourceDashboardView.as_view(), name='lab-resource-dashboard'),
    path('scheduling/', SchedulingDashboardView.as_view(), name='scheduling-dashboard'),
    path('personal-teaching/', PersonalTeachingDashboardView.as_view(), name='personal-teaching-dashboard'),
    path('comprehensive/', ComprehensiveStatsView.as_view(), name='comprehensive-stats'),
    path('comprehensive/export/', ExportComprehensiveStatsView.as_view(), name='export-comprehensive-stats'),
]
