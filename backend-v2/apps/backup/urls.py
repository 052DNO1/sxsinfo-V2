"""
备份路由
"""

from django.urls import path
from apps.backup.views import (
    BackupStatsView, BackupExportView, BackupInfoView, BackupRestoreView,
    AutoBackupConfigView, BackupListView, BackupDownloadView, BackupDeleteView
)

urlpatterns = [
    path('stats/', BackupStatsView.as_view(), name='backup-stats'),
    path('export/', BackupExportView.as_view(), name='backup-export'),
    path('info/', BackupInfoView.as_view(), name='backup-info'),
    path('restore/', BackupRestoreView.as_view(), name='backup-restore'),
    path('auto-config/', AutoBackupConfigView.as_view(), name='auto-backup-config'),
    path('list/', BackupListView.as_view(), name='backup-list'),
    path('download/<str:filename>/', BackupDownloadView.as_view(), name='backup-download'),
    path('delete/<str:filename>/', BackupDeleteView.as_view(), name='backup-delete'),
]
