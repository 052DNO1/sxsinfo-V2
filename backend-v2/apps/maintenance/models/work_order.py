"""
工单模型
"""

from django.db import models
from django.utils import timezone
from apps.core.models import BaseModel
from apps.core.constants import WorkOrderStatus, MaintenanceType


class WorkOrder(BaseModel):
    """工单模型"""
    
    title = models.CharField('工单标题', max_length=200)
    description = models.TextField('问题描述')
    
    laboratory = models.ForeignKey(
        'laboratories.Laboratory',
        on_delete=models.SET_NULL,
        null=True,
        related_name='work_orders',
        verbose_name='实训室'
    )
    laboratory_name = models.CharField('实训室名称', max_length=100, blank=True, default='')
    laboratory_code = models.CharField('实训室编号', max_length=50, blank=True, default='')
    equipment = models.ForeignKey(
        'laboratories.Equipment',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='work_orders',
        verbose_name='关联设备'
    )
    semester = models.ForeignKey(
        'schedules.Semester',
        on_delete=models.CASCADE,
        related_name='work_orders',
        verbose_name='学期'
    )
    
    maintenance_type = models.IntegerField(
        '维护类型',
        default=MaintenanceType.REPAIR,
        choices=[(t.value, t.name) for t in MaintenanceType]
    )
    
    status = models.CharField(
        '工单状态',
        max_length=20,
        default=WorkOrderStatus.PENDING,
        choices=[(s.value, s.name) for s in WorkOrderStatus]
    )
    priority = models.IntegerField('优先级', default=1)
    
    reporter = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='reported_orders',
        verbose_name='上报人'
    )
    handler = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='handled_orders',
        verbose_name='处理人'
    )
    
    reported_at = models.DateTimeField('上报时间', auto_now_add=True)
    assigned_at = models.DateTimeField('分配时间', null=True, blank=True)
    started_at = models.DateTimeField('开始处理时间', null=True, blank=True)
    completed_at = models.DateTimeField('完成时间', null=True, blank=True)
    closed_at = models.DateTimeField('关闭时间', null=True, blank=True)
    
    solution = models.TextField('解决方案', blank=True, default='')
    handle_note = models.TextField('处理备注', blank=True, default='')
    
    rating = models.IntegerField('评价', null=True, blank=True)
    feedback = models.TextField('反馈', blank=True, default='')
    
    is_archived = models.BooleanField('是否已归档', default=False)
    hidden_in_center = models.BooleanField('在工单中心隐藏', default=False)

    order_number = models.CharField('工单编号', max_length=50, unique=True, db_index=True, null=True, blank=True)

    class Meta:
        db_table = 'work_orders'
        verbose_name = '工单'
        verbose_name_plural = verbose_name
        ordering = ['-reported_at']
        indexes = [
            models.Index(fields=['laboratory', 'status']),
            models.Index(fields=['status', 'priority']),
            models.Index(fields=['reporter', 'status']),
            models.Index(fields=['handler', 'status']),
        ]

    def __str__(self):
        return f"{self.title} - {self.get_status_display()}"

    def assign(self, handler):
        """分配工单"""
        self.handler = handler
        self.status = WorkOrderStatus.PROCESSING
        self.assigned_at = timezone.now()
        self.save()

    def start_handle(self):
        """开始处理"""
        self.status = WorkOrderStatus.PROCESSING
        self.started_at = timezone.now()
        self.save()

    def complete(self, solution):
        """完成处理"""
        self.status = WorkOrderStatus.COMPLETED
        self.solution = solution
        self.completed_at = timezone.now()
        self.save()

    def close(self):
        """关闭工单"""
        self.status = WorkOrderStatus.CLOSED
        self.closed_at = timezone.now()
        self.save()

    @classmethod
    def generate_order_number(cls, maintenance_type=3):
        """
        生成工单编号
        格式：W202604150001（维护）或 G202604150001（故障）
        maintenance_type=3 是故障，其他是维护
        """
        from django.db import transaction
        
        prefix = 'G' if maintenance_type == 3 else 'W'
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
