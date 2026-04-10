"""
实训室模型
"""

from django.db import models
from apps.core.models import BaseModel
from apps.core.constants import LaboratoryStatus


class Laboratory(BaseModel):
    """实训室模型"""
    
    name = models.CharField('实训室名称', max_length=100)
    code = models.CharField('实训室编号', max_length=50, unique=True)
    building = models.CharField('所在楼宇', max_length=100, blank=True, default='')
    floor = models.IntegerField('所在楼层', null=True, blank=True)
    room_number = models.CharField('房间号', max_length=50, blank=True, default='')
    
    capacity = models.IntegerField('工位数', default=30)
    area = models.FloatField('面积(平方米)', null=True, blank=True)
    
    laboratory_type = models.CharField(
        '实训室类型',
        max_length=50,
        default='普通实训室'
    )
    
    department = models.ForeignKey(
        'users.Department',
        on_delete=models.PROTECT,
        related_name='laboratories',
        verbose_name='所属部门'
    )
    admin = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='managed_laboratories',
        verbose_name='管理员'
    )
    
    status = models.IntegerField(
        '状态',
        default=LaboratoryStatus.AVAILABLE,
        choices=[(s.value, s.name) for s in LaboratoryStatus]
    )
    is_available = models.BooleanField('是否可用', default=True)
    
    facilities = models.JSONField(
        '设施配置',
        default=dict,
        blank=True
    )
    
    description = models.TextField('描述', blank=True, default='')
    note = models.TextField('备注', blank=True, default='')
    
    images = models.JSONField(
        '图片列表',
        default=list,
        blank=True
    )

    class Meta:
        db_table = 'laboratories'
        verbose_name = '实训室'
        verbose_name_plural = verbose_name
        ordering = ['code']
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['department', 'status']),
            models.Index(fields=['admin', 'status']),
        ]

    def __str__(self):
        return f"{self.name}({self.code})"

    @property
    def location(self):
        parts = [self.building]
        if self.floor:
            parts.append(f"{self.floor}楼")
        if self.room_number:
            parts.append(self.room_number)
        return ' '.join(filter(None, parts))

    def get_equipment_count(self):
        return self.equipments.filter(is_deleted=False).count()
    
    def get_schedule_count(self):
        from apps.schedules.models import Schedule
        return Schedule.objects.filter(laboratory=self, is_deleted=False).count()
