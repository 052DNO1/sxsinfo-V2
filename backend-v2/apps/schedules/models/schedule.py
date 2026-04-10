"""
课表模型
"""

from django.db import models
from apps.core.models import BaseModel
from apps.core.constants import WeekDay


class Schedule(BaseModel):
    """课表模型"""
    
    course_name = models.CharField('课程名称', max_length=100)
    course_code = models.CharField('课程代码', max_length=50, blank=True, default='')
    
    weekday = models.IntegerField(
        '星期',
        choices=[(d.value, d.name) for d in WeekDay]
    )
    time_slot = models.CharField(
        '节次',
        max_length=20,
        help_text='如: 1-2, 3-4, 1,2,3'
    )
    weeks = models.CharField(
        '上课周次',
        max_length=50,
        default='1-18',
        help_text='如: 1-18, 1,3,5,7-15'
    )
    
    laboratory = models.ForeignKey(
        'laboratories.Laboratory',
        on_delete=models.CASCADE,
        related_name='schedules',
        verbose_name='实训室'
    )
    semester = models.ForeignKey(
        'Semester',
        on_delete=models.CASCADE,
        related_name='schedules',
        verbose_name='学期'
    )
    teacher = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='teaching_schedules',
        verbose_name='任课教师'
    )
    teacher_name = models.CharField(
        '教师姓名',
        max_length=50,
        blank=True,
        default='',
        help_text='冗余字段'
    )
    
    class_name = models.CharField('上课班级', max_length=100, blank=True, default='')
    student_count = models.IntegerField('学生人数', default=0)
    
    is_active = models.BooleanField('是否有效', default=True)
    is_archived = models.BooleanField('是否已归档', default=False)
    
    note = models.TextField('备注', blank=True, default='')

    class Meta:
        db_table = 'schedules'
        verbose_name = '课表'
        verbose_name_plural = verbose_name
        ordering = ['laboratory__code', 'weekday', 'time_slot']
        indexes = [
            models.Index(fields=['laboratory', 'semester', 'weekday']),
            models.Index(fields=['teacher', 'semester']),
            models.Index(fields=['semester', 'is_active']),
        ]

    def __str__(self):
        return f"{self.course_name} - {self.laboratory.name}"

    def get_time_points(self):
        """解析节次"""
        from apps.core.utils import parse_date_range
        return parse_date_range(self.time_slot)

    def get_week_points(self):
        """解析周次"""
        from apps.core.utils import parse_date_range
        return parse_date_range(self.weeks)
