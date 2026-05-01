"""
通知服务
"""

from datetime import datetime
from django.db import models
from django.utils import timezone
from django.core.paginator import Paginator
from apps.core.exceptions import NotFoundError, PermissionDenied
from apps.notifications.models import Notification, NotificationRecipient
from apps.core.utils import beijing_strftime, beijing_now, beijing_today


class NotificationService:
    """通知服务"""
                                      
    def get_notification_list(
        self,
        user,
        is_read: bool = None,
        notification_type: str = None,
        search: str = None,
        page: int = 1,
        page_size: int = 10
    ) -> dict:
        queryset = NotificationRecipient.objects.filter(
            user=user
        ).select_related('notification', 'notification__sender')
        
        if is_read is not None:
            queryset = queryset.filter(is_read=is_read)
        
        if notification_type:
            queryset = queryset.filter(notification__notification_type=notification_type)
        
        if search:
            queryset = queryset.filter(
                models.Q(notification__title__icontains=search) |
                models.Q(notification__content__icontains=search)
            )
        
        queryset = queryset.order_by('-notification__created_time')
        
        paginator = Paginator(queryset, page_size)
        page_obj = paginator.get_page(page)
        
        notifications = []
        for nr in page_obj:
            notif = nr.notification
            sender_name = '系统'
            if notif.sender:
                sender_name = notif.sender.nickname or notif.sender.username
            
            notifications.append({
                'id': notif.id,
                'title': notif.title,
                'content': notif.content,
                'sender_name': sender_name,
                'notification_type': notif.notification_type,
                'priority': notif.priority,
                'is_read': nr.is_read,
                'read_time': beijing_strftime(nr.read_time) or None,
                'created_time': beijing_strftime(notif.created_time),
            })
        
        unread_count = NotificationRecipient.objects.filter(
            user=user, is_read=False
        ).count()
        
        return {
            'notifications': notifications,
            'total': paginator.count,
            'page': page,
            'page_size': page_size,
            'total_pages': paginator.num_pages,
            'unread_count': unread_count,
        }

    def get_notification_detail(self, user, notification_id: int) -> dict:
        try:
            nr = NotificationRecipient.objects.select_related(
                'notification', 'notification__sender'
            ).get(notification_id=notification_id, user=user)
        except NotificationRecipient.DoesNotExist:
            raise NotFoundError('通知不存在')
        
        notif = nr.notification
        
        if not nr.is_read:
            nr.is_read = True
            nr.read_time = timezone.now()
            nr.save(update_fields=['is_read', 'read_time'])
        
        sender_name = '系统'
        if notif.sender:
            sender_name = notif.sender.nickname or notif.sender.username
        
        return {
            'id': notif.id,
            'title': notif.title,
            'content': notif.content,
            'sender_name': sender_name,
            'notification_type': notif.notification_type,
            'priority': notif.priority,
            'is_read': nr.is_read,
            'read_time': beijing_strftime(nr.read_time) or None,
            'created_time': beijing_strftime(notif.created_time),
            'expires_at': beijing_strftime(notif.expires_at) or None,
        }

    def send_notification(
        self,
        title: str,
        content: str,
        recipients,
        notification_type: str = 'SYSTEM',
        priority: str = 'NORMAL',
        sender=None,
        expires_at=None
    ) -> Notification:
        notification = Notification.objects.create(
            title=title,
            content=content,
            notification_type=notification_type,
            priority=priority,
            sender=sender,
            expires_at=expires_at
        )
        
        if isinstance(recipients, (list, tuple)):
            for recipient in recipients:
                NotificationRecipient.objects.create(
                    notification=notification,
                    user=recipient
                )
        else:
            NotificationRecipient.objects.create(
                notification=notification,
                user=recipients
            )
        
        return notification

    def mark_as_read(self, user, notification_id: int) -> bool:
        try:
            nr = NotificationRecipient.objects.get(
                notification_id=notification_id, user=user
            )
        except NotificationRecipient.DoesNotExist:
            raise NotFoundError('通知不存在')
        
        if not nr.is_read:
            nr.is_read = True
            nr.read_time = timezone.now()
            nr.save(update_fields=['is_read', 'read_time'])
        
        return True

    def mark_all_as_read(self, user) -> int:
        count = NotificationRecipient.objects.filter(
            user=user, is_read=False
        ).update(is_read=True, read_time=timezone.now())
        
        return count

    def delete_notification(self, user, notification_id: int) -> bool:
        try:
            nr = NotificationRecipient.objects.get(
                notification_id=notification_id, user=user
            )
        except NotificationRecipient.DoesNotExist:
            raise NotFoundError('通知不存在')
        
        nr.delete()
        return True

    def get_unread_count(self, user) -> int:
        return NotificationRecipient.objects.filter(
            user=user, is_read=False
        ).count()
