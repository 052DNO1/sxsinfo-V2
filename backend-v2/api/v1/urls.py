"""
API v1 路由汇总
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

urlpatterns = [
    path('auth/', include('apps.users.urls_auth')),
    path('users/', include('apps.users.urls')),
    path('departments/', include('apps.users.urls_department')),
    path('laboratories/', include('apps.laboratories.urls')),
    path('equipments/', include('apps.laboratories.urls_equipment')),
    path('schedules/', include('apps.schedules.urls')),
    path('semesters/', include('apps.schedules.urls_semester')),
    path('records/', include('apps.records.urls')),
    path('work-orders/', include('apps.maintenance.urls')),
    path('notifications/', include('apps.notifications.urls')),
    path('ai/', include('apps.ai_assistant.urls')),
    path('backups/', include('apps.backup.urls')),
    path('statistics/', include('apps.statistics.urls')),
    path('common/', include('common.urls')),
]
