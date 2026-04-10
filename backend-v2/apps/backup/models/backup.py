"""
备份模型
"""

from django.db import models
from apps.core.models import BaseModel


class AutoBackupConfig(BaseModel):
    """自动备份配置"""

    PERIOD_CHOICES = [
        ('daily', '每天'),
        ('weekly', '每周'),
        ('monthly', '每月'),
    ]

    enabled = models.BooleanField('是否启用', default=False)
    period = models.CharField(
        '备份周期',
        max_length=20,
        choices=PERIOD_CHOICES,
        default='daily'
    )
    last_backup_time = models.DateTimeField('上次备份时间', null=True, blank=True)
    next_backup_time = models.DateTimeField('下次备份时间', null=True, blank=True)

    class Meta:
        db_table = 'auto_backup_config'
        verbose_name = '自动备份配置'
        verbose_name_plural = '自动备份配置'

    def __str__(self):
        return f'自动备份配置 - {self.get_period_display()}'
