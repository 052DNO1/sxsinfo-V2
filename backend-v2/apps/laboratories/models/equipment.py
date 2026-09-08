"""
设备模型
"""

from django.db import models
from apps.core.models import BaseModel
from apps.core.constants import EquipmentStatus


class Equipment(BaseModel):
    """设备模型"""
    
    name = models.CharField('设备名称', max_length=100)
    code = models.CharField('设备编号', max_length=50)
    category = models.CharField('设备类别', max_length=50, default='计算机')
    
    brand = models.CharField('品牌', max_length=50, blank=True, default='')
    model = models.CharField('型号', max_length=100, blank=True, default='')
    serial_number = models.CharField('序列号', max_length=100, blank=True, default='')
    
    laboratory = models.ForeignKey(
        'Laboratory',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='equipments',
        verbose_name='所属实训室'
    )
    position = models.CharField('位置', max_length=50, blank=True, default='')
    
    cpu = models.CharField('CPU', max_length=100, blank=True, default='')
    memory = models.CharField('内存', max_length=50, blank=True, default='')
    disk = models.CharField('硬盘', max_length=50, blank=True, default='')
    gpu = models.CharField('显卡', max_length=100, blank=True, default='')
    os = models.CharField('操作系统', max_length=50, blank=True, default='')
    
    purchase_date = models.DateField('购买日期', null=True, blank=True)
    warranty_expire = models.DateField('保修到期', null=True, blank=True)
    price = models.DecimalField('价格', max_digits=10, decimal_places=2, null=True, blank=True)
    supplier = models.CharField('供应商', max_length=100, blank=True, default='')
    
    status = models.CharField(
        '状态',
        max_length=20,
        default=EquipmentStatus.NORMAL,
        choices=[(s.value, s.name) for s in EquipmentStatus]
    )
    
    last_maintenance_date = models.DateField('最后维护日期', null=True, blank=True)
    
    description = models.TextField('描述', blank=True, default='')
    note = models.TextField('备注', blank=True, default='')

    class Meta:
        db_table = 'equipments'
        verbose_name = '设备'
        verbose_name_plural = verbose_name
        ordering = ['code']
        unique_together = ['code', 'laboratory']
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['laboratory', 'status']),
            models.Index(fields=['category', 'status']),
        ]

    def __str__(self):
        return f"{self.name}({self.code})"
