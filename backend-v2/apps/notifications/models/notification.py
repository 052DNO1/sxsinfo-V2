"""
通知模型
"""

from django.db import models
from django.conf import settings


class Notification(models.Model):
    """通知模型"""
    
    TYPE_CHOICES = [
        ('SYSTEM', '系统通知'),
        ('MAINTENANCE', '维护通知'),
        ('SCHEDULE', '课表通知'),
        ('ALERT', '告警通知'),
        ('INFO', '信息通知'),
    ]
    
    PRIORITY_CHOICES = [
        ('LOW', '低'),
        ('NORMAL', '普通'),
        ('HIGH', '高'),
        ('URGENT', '紧急'),
    ]
    
    title = models.CharField('标题', max_length=200)
    content = models.TextField('内容')
    notification_type = models.CharField(
        '通知类型',
        max_length=20,
        choices=TYPE_CHOICES,
        default='SYSTEM'
    )
    priority = models.CharField(
        '优先级',
        max_length=10,
        choices=PRIORITY_CHOICES,
        default='NORMAL'
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sent_notifications',
        verbose_name='发送者'
    )
    recipients = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through='NotificationRecipient',
        related_name='notifications',
        verbose_name='接收者'
    )
    created_time = models.DateTimeField('创建时间', auto_now_add=True)
    expires_at = models.DateTimeField('过期时间', null=True, blank=True)
    
    class Meta:
        db_table = 'notification'
        verbose_name = '通知'
        verbose_name_plural = '通知'
        ordering = ['-created_time']
    
    def __str__(self):
        return self.title


class NotificationRecipient(models.Model):
    """通知接收者关联表"""
    
    notification = models.ForeignKey(Notification, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    is_read = models.BooleanField('是否已读', default=False)
    read_time = models.DateTimeField('阅读时间', null=True, blank=True)
    
    class Meta:
        db_table = 'notification_recipient'
        unique_together = ['notification', 'user']
