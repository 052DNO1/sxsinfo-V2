"""
使用记录模型
"""

from django.db import models
from apps.core.models import BaseModel


class UsageRecord(BaseModel):
    """使用记录模型"""
    
    usage_date = models.DateField('使用日期')
    time_slot = models.CharField('节次', max_length=20, default='1-4')
    class_hours = models.IntegerField('学时', default=4)
    
    laboratory = models.ForeignKey(
        'laboratories.Laboratory',
        on_delete=models.CASCADE,
        related_name='usage_records',
        verbose_name='实训室'
    )
    semester = models.ForeignKey(
        'schedules.Semester',
        on_delete=models.CASCADE,
        related_name='usage_records',
        verbose_name='学期'
    )
    teacher = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='usage_records',
        verbose_name='教师'
    )
    
    class_name = models.CharField('上课班级', max_length=100, blank=True, default='')
    student_count = models.IntegerField('学生人数', default=0)
    content = models.TextField('实训内容', blank=True, default='')
    
    device_status = models.CharField('设备状态', max_length=50, default='正常')
    laboratory_status = models.CharField('实训室状态', max_length=50, default='正常')
    
    is_locked = models.BooleanField('是否锁定', default=False)
    is_archived = models.BooleanField('是否已归档', default=False)
    
    note = models.TextField('备注', blank=True, default='')

    class Meta:
        db_table = 'usage_records'
        verbose_name = '使用记录'
        verbose_name_plural = verbose_name
        ordering = ['-usage_date', 'laboratory__code']
        indexes = [
            models.Index(fields=['laboratory', 'usage_date']),
            models.Index(fields=['teacher', 'usage_date']),
            models.Index(fields=['semester', 'usage_date']),
        ]

    def __str__(self):
        return f"{self.laboratory.name} - {self.usage_date}"
