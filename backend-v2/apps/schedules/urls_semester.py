"""
学期路由
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.schedules.views.semester import SemesterViewSet

router = DefaultRouter()
router.register(r'', SemesterViewSet, basename='semester')

urlpatterns = [
    path('', include(router.urls)),
]
