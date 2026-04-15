"""
工单路由
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.maintenance.views import (
    WorkOrderViewSet,
    WorkOrderCenterListView, WorkOrderCenterDetailView,
    WorkOrderCenterHideView
)

router = DefaultRouter()
router.register(r'', WorkOrderViewSet, basename='work-order')

urlpatterns = [
    path('center/', WorkOrderCenterListView.as_view(), name='work-order-center-list'),
    path('center/<int:order_id>/', WorkOrderCenterDetailView.as_view(), name='work-order-center-detail'),
    path('center/<int:order_id>/hide/', WorkOrderCenterHideView.as_view(), name='work-order-center-hide'),
    
    path('', include(router.urls)),
]
