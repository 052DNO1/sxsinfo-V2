"""
基础模型类
所有业务模型都应继承这些基类
"""

from django.db import models
from django.utils import timezone


class TimeStampedModel(models.Model):
    """
    时间戳模型
    自动记录创建时间和更新时间
    """
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        abstract = True


class SoftDeleteModel(models.Model):
    """
    软删除模型
    删除时不真正删除，而是标记为已删除
    """
    is_deleted = models.BooleanField(default=False, verbose_name='是否已删除')
    deleted_at = models.DateTimeField(null=True, blank=True, verbose_name='删除时间')
    deleted_by = models.ForeignKey(
        'users.User',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='deleted_%(class)s_set',
        verbose_name='删除人'
    )

    class Meta:
        abstract = True

    def soft_delete(self, user=None):
        """软删除"""
        self.is_deleted = True
        self.deleted_at = timezone.now()
        if user:
            self.deleted_by = user
        self.save()

    def restore(self):
        """恢复删除"""
        self.is_deleted = False
        self.deleted_at = None
        self.deleted_by = None
        self.save()


class BaseModel(TimeStampedModel, SoftDeleteModel):
    """
    基础模型
    包含时间戳和软删除功能
    """
    class Meta:
        abstract = True


class SingletonModel(models.Model):
    """
    单例模型
    系统中只存在一条记录的模型
    """
    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.id = 1
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass

    @classmethod
    def get_instance(cls):
        obj, _ = cls.objects.get_or_create(id=1)
        return obj
