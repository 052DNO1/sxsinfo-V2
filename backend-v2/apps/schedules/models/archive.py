"""
学期归档模型
"""

from django.db import models
from apps.core.models import BaseModel


class TermArchive(BaseModel):
    """学期归档数据模型"""
    
    ARCHIVE_TYPES = [
        ('lab_info', '实训室信息'),
        ('device_info', '设备信息'),
        ('user_info', '用户信息'),
    ]
    
    semester = models.ForeignKey(
        'schedules.Semester',
        on_delete=models.CASCADE,
        related_name='archives',
        verbose_name='关联学期'
    )
    archive_type = models.CharField(
        max_length=20,
        choices=ARCHIVE_TYPES,
        verbose_name='归档类型'
    )
    content = models.JSONField(
        verbose_name='归档内容'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='归档时间'
    )
    
    class Meta:
        db_table = 'term_archive'
        verbose_name = '学期归档'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']
        unique_together = ['semester', 'archive_type']
    
    def __str__(self):
        return f"{self.semester.name} - {self.get_archive_type_display()}"
