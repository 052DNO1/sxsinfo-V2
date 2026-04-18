"""
Core 应用路由配置
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.core.views.operation_log import SystemOperationLogViewSet

router = DefaultRouter()
router.register(r'operation-logs', SystemOperationLogViewSet, basename='operation-log')

urlpatterns = [
    path('', include(router.urls)),
]
