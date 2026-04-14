"""
部门模型
"""

from django.db import models
from mptt.models import MPTTModel, TreeForeignKey
from apps.core.models import BaseModel


class Department(MPTTModel, BaseModel):
    """部门模型"""
    
    name = models.CharField('部门名称', max_length=100)
    code = models.CharField('部门编码', max_length=50, unique=True, blank=True, null=True)
    parent = TreeForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children',
        verbose_name='上级部门'
    )
    
    managers = models.ManyToManyField(
        'User',
        blank=True,
        related_name='managed_departments',
        verbose_name='部门管理员',
        db_table='department_managers'
    )
    
    description = models.TextField('部门描述', blank=True, default='')
    order = models.IntegerField('排序', default=0)
    is_active = models.BooleanField('是否启用', default=True)
    
    phone = models.CharField('联系电话', max_length=20, blank=True, default='')
    email = models.EmailField('部门邮箱', blank=True, default='')
    address = models.CharField('办公地址', max_length=200, blank=True, default='')

    class Meta:
        db_table = 'departments'
        verbose_name = '部门'
        verbose_name_plural = verbose_name
        ordering = ['order', 'code']

    class MPTTMeta:
        order_insertion_by = ['order']

    def __str__(self):
        return self.name

    def get_all_users(self):
        from apps.users.models import User
        descendants = self.get_descendants(include_self=True)
        return User.objects.filter(department__in=descendants, is_deleted=False)

    def get_user_count(self):
        return self.users.filter(is_deleted=False).count()
