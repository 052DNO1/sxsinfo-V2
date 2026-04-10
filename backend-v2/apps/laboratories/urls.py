"""
实训室路由
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.laboratories.views import LaboratoryViewSet

router = DefaultRouter()
router.register(r'', LaboratoryViewSet, basename='laboratory')

urlpatterns = [
    path('', include(router.urls)),
]
