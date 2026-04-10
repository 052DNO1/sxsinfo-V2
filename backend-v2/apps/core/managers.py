"""
自定义Manager
提供常用的查询方法
"""

from django.db import models


class SoftDeleteManager(models.Manager):
    """
    软删除Manager
    默认过滤已删除的记录
    """
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)


class AllObjectsManager(models.Manager):
    """
    包含所有记录的Manager（包括已删除）
    """
    pass


class ActiveManager(models.Manager):
    """
    活跃状态Manager
    过滤已删除和未激活的记录
    """
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False, is_active=True)
