"""
设备路由
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.laboratories.views import EquipmentViewSet

router = DefaultRouter()
router.register(r'', EquipmentViewSet, basename='equipment')

urlpatterns = [
    path('', include(router.urls)),
]
