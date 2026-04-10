"""
公共功能路由
"""

from django.urls import path
from common.views.search import GlobalSearchView
from common.views.export import (
    ExportLaboratoriesView, ExportSchedulesView, ExportRecordsView,
    ExportWorkOrdersView, ExportEquipmentView, ExportUsersView,
    ExportStatisticsReportView
)
from common.views.progress import ProgressView
from common.views.health import HealthCheckView
from common.views.import_views import (
    ImportLaboratoriesView, ImportSchedulesView, ImportEquipmentView
)

urlpatterns = [
    path('search/', GlobalSearchView.as_view(), name='global-search'),
    path('progress/', ProgressView.as_view(), name='progress'),
    path('health/', HealthCheckView.as_view(), name='health-check'),
    
    path('export/laboratories/', ExportLaboratoriesView.as_view(), name='export-laboratories'),
    path('export/schedules/', ExportSchedulesView.as_view(), name='export-schedules'),
    path('export/records/', ExportRecordsView.as_view(), name='export-records'),
    path('export/work-orders/', ExportWorkOrdersView.as_view(), name='export-work-orders'),
    path('export/equipment/', ExportEquipmentView.as_view(), name='export-equipment'),
    path('export/users/', ExportUsersView.as_view(), name='export-users'),
    path('export/statistics/', ExportStatisticsReportView.as_view(), name='export-statistics'),
    
    path('import/laboratories/', ImportLaboratoriesView.as_view(), name='import-laboratories'),
    path('import/schedules/', ImportSchedulesView.as_view(), name='import-schedules'),
    path('import/equipment/', ImportEquipmentView.as_view(), name='import-equipment'),
]
