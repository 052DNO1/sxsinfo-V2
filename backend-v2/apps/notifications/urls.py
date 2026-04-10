"""
通知路由
"""

from django.urls import path
from apps.notifications.views import (
    NotificationListView, NotificationDetailView,
    NotificationMarkReadView, NotificationMarkAllReadView,
    NotificationDeleteView, NotificationUnreadCountView,
    SendNotificationView, BroadcastNotificationView
)

urlpatterns = [
    path('', NotificationListView.as_view(), name='notification-list'),
    path('<int:notification_id>/', NotificationDetailView.as_view(), name='notification-detail'),
    path('<int:notification_id>/mark-read/', NotificationMarkReadView.as_view(), name='notification-mark-read'),
    path('mark-all-read/', NotificationMarkAllReadView.as_view(), name='notification-mark-all-read'),
    path('<int:notification_id>/delete/', NotificationDeleteView.as_view(), name='notification-delete'),
    path('unread-count/', NotificationUnreadCountView.as_view(), name='notification-unread-count'),
    path('send/', SendNotificationView.as_view(), name='send-notification'),
    path('broadcast/', BroadcastNotificationView.as_view(), name='broadcast-notification'),
]
