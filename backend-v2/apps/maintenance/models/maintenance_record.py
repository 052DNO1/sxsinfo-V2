"""
维护记录模型
"""

from django.db import models
from django.utils import timezone
from apps.core.models import BaseModel


class MaintenanceRecord(BaseModel):
    """维护记录模型"""
    
    ORDER_TYPE_CHOICES = [
        ('W', '维护'),
        ('G', '故障'),
    ]
    
    STATUS_CHOICES = [
        ('maintained', '已维护'),
        ('pending', '待维护'),
        ('processing', '维护中'),
    ]
    
    order_number = models.CharField('工单编号', max_length=50, unique=True, db_index=True)
    order_type = models.CharField('工单类型', max_length=1, choices=ORDER_TYPE_CHOICES, default='W')
    
    laboratory = models.ForeignKey(
        'laboratories.Laboratory',
        on_delete=models.CASCADE,
        related_name='maintenance_records',
        verbose_name='实训实验室'
    )
    
    maintainer = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='maintained_records',
        verbose_name='维护人'
    )
    
    content = models.TextField('维护内容')
    
    status = models.CharField(
        '状态',
        max_length=20,
        choices=STATUS_CHOICES,
        default='maintained'
    )
    
    maintenance_time = models.DateTimeField('维护时间', default=timezone.now)
    
    semester = models.ForeignKey(
        'schedules.Semester',
        on_delete=models.CASCADE,
        related_name='maintenance_records',
        verbose_name='学期'
    )
    
    note = models.TextField('备注', blank=True, default='')
    
    is_archived = models.BooleanField('是否已归档', default=False)
    
    class Meta:
        db_table = 'maintenance_records'
        verbose_name = '维护记录'
        verbose_name_plural = verbose_name
        ordering = ['-maintenance_time']
        indexes = [
            models.Index(fields=['laboratory', 'status']),
            models.Index(fields=['order_type', 'status']),
            models.Index(fields=['maintainer', 'status']),
        ]
    
    def __str__(self):
        return f"{self.order_number} - {self.get_status_display()}"
    
    @classmethod
    def generate_order_number(cls, order_type='W'):
        """
        生成工单编号
        格式：W202604150001 或 G202604150001
        """
        from django.db import transaction
        from datetime import datetime
        
        prefix = order_type
        date_str = timezone.now().strftime('%Y%m%d')
        
        with transaction.atomic():
            last_record = cls.objects.filter(
                order_number__startswith=f"{prefix}{date_str}"
            ).order_by('-order_number').first()
            
            if last_record:
                last_num = int(last_record.order_number[-4:])
                new_num = last_num + 1
            else:
                new_num = 1
            
            order_number = f"{prefix}{date_str}{new_num:04d}"
            
            return order_number
