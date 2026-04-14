"""
工单路由
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.maintenance.views import (
    WorkOrderViewSet,
    WorkOrderCenterListView, WorkOrderCenterDetailView,
    WorkOrderCenterHideView,
    MaintenanceRecordViewSet
)

router = DefaultRouter()
router.register(r'', WorkOrderViewSet, basename='work-order')

maintenance_record_router = DefaultRouter()
maintenance_record_router.register(r'', MaintenanceRecordViewSet, basename='maintenance-record')

urlpatterns = [
    path('', include(router.urls)),
    
    path('center/', WorkOrderCenterListView.as_view(), name='work-order-center-list'),
    path('center/<int:order_id>/', WorkOrderCenterDetailView.as_view(), name='work-order-center-detail'),
    path('center/<int:order_id>/hide/', WorkOrderCenterHideView.as_view(), name='work-order-center-hide'),
    
    path('records/', include(maintenance_record_router.urls)),
]
