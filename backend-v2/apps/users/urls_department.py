"""
部门路由
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.users.views.department import DepartmentViewSet

router = DefaultRouter()
router.register(r'', DepartmentViewSet, basename='department')

urlpatterns = [
    path('', include(router.urls)),
]
