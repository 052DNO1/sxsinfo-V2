"""
系统设置模型
"""

from django.db import models
from apps.core.models import BaseModel


class SystemSetting(BaseModel):
    """系统设置模型"""
    
    key = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='设置键'
    )
    value = models.TextField(
        verbose_name='设置值'
    )
    description = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='设置描述'
    )
    
    class Meta:
        db_table = 'system_setting'
        verbose_name = '系统设置'
        verbose_name_plural = verbose_name
    
    def __str__(self):
        return f"{self.key}: {self.value}"
    
    @classmethod
    def get_value(cls, key: str, default=None):
        """获取设置值"""
        try:
            setting = cls.objects.get(key=key)
            return setting.value
        except cls.DoesNotExist:
            return default
    
    @classmethod
    def set_value(cls, key: str, value: str, description: str = ''):
        """设置值"""
        return cls.objects.update_or_create(
            key=key,
            defaults={'value': value, 'description': description}
        )[0]
