"""
学期模型
"""

from django.db import models, transaction
from apps.core.models import BaseModel


class Semester(BaseModel):
    """学期模型"""
    
    name = models.CharField('学期名称', max_length=50, unique=True)
    code = models.CharField('学期代码', max_length=20, unique=True)
    
    start_date = models.DateField('开始日期')
    end_date = models.DateField('结束日期')
    
    is_current = models.BooleanField('是否当前学期', default=False)
    is_archived = models.BooleanField('是否已归档', default=False)
    
    total_weeks = models.IntegerField('总周数', default=18)
    
    description = models.TextField('描述', blank=True, default='')

    class Meta:
        db_table = 'semesters'
        verbose_name = '学期'
        verbose_name_plural = verbose_name
        ordering = ['-start_date']

    def __str__(self):
        return self.name

    @classmethod
    def get_current(cls):
        """获取当前学期"""
        return cls.objects.filter(is_current=True, is_archived=False).first()

    @transaction.atomic
    def set_as_current(self):
        """设置为当前学期"""
        Semester.objects.filter(is_current=True).update(is_current=False)
        self.is_current = True
        self.is_archived = False
        self.save(update_fields=['is_current', 'is_archived'])

    @transaction.atomic
    def archive(self):
        """归档学期"""
        self.is_archived = True
        self.is_current = False
        self.save(update_fields=['is_archived', 'is_current'])
        
        from .schedule import Schedule
        Schedule.objects.filter(semester=self).update(is_archived=True)

    def get_schedule_count(self):
        return self.schedules.filter(is_deleted=False).count()
