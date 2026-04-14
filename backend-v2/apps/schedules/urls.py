"""
课表路由
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.schedules.views import ScheduleViewSet
from apps.schedules.views.semester import SemesterViewSet
from apps.schedules.views.archive import (
    ArchiveSettingsView, ManualCleanupView, ArchiveCurrentTermView,
    ArchivedRecordsView, CheckTermStatusView
)

router = DefaultRouter()
router.register(r'', ScheduleViewSet, basename='schedule')

urlpatterns = [
    path('archive-settings/', ArchiveSettingsView.as_view(), name='archive-settings'),
    path('manual-cleanup/', ManualCleanupView.as_view(), name='manual-cleanup'),
    path('archive-current/', ArchiveCurrentTermView.as_view(), name='archive-current-term'),
    path('archived/<int:semester_id>/', ArchivedRecordsView.as_view(), name='archived-records'),
    path('check-status/', CheckTermStatusView.as_view(), name='check-term-status'),
    path('', include(router.urls)),
]
