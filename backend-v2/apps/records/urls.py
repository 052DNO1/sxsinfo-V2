"""
使用记录路由
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.records.views import UsageRecordViewSet

router = DefaultRouter()
router.register(r'', UsageRecordViewSet, basename='usage-record')

urlpatterns = [
    path('', include(router.urls)),
]
