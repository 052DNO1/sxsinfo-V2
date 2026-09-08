"""
基础模型类
所有业务模型都应继承这些基类
"""

from django.db import models
from django.conf import settings
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


class SystemOperationLog(BaseModel):
    """系统操作日志模型"""

    MODULE_CHOICES = [
        ('user', '用户管理'),
        ('equipment', '设备管理'),
        ('schedule', '课表管理'),
        ('cache_config', '缓存配置'),
        ('department', '部门管理'),
        ('laboratory', '实训室管理'),
        ('backup', '备份管理'),
        ('system', '系统设置'),
    ]

    OPERATION_TYPE_CHOICES = [
        # 用户管理
        ('user_create', '创建用户'),
        ('user_delete', '删除用户'),
        ('user_update', '更新用户'),
        ('user_role_update', '更新用户权限'),
        ('user_batch_delete', '批量删除用户'),
        ('user_import', '导入用户'),
        ('user_activate', '启用/禁用用户'),
        # 设备管理
        ('equipment_create', '添加设备'),
        ('equipment_delete', '删除设备'),
        ('equipment_update', '更新设备'),
        ('equipment_batch_delete', '批量删除设备'),
        # 课表管理
        ('schedule_create', '添加课表'),
        ('schedule_delete', '删除课表'),
        ('schedule_update', '更新课表'),
        # 缓存配置
        ('cache_config_create', '创建缓存配置'),
        ('cache_config_delete', '删除缓存配置'),
        ('cache_config_update', '更新缓存配置'),
        ('cache_clear', '清除缓存'),
        # 部门管理
        ('department_create', '创建部门'),
        ('department_update', '更新部门'),
        ('department_delete', '删除部门'),
        # 实训室管理
        ('laboratory_create', '创建实训室'),
        ('laboratory_update', '更新实训室'),
        ('laboratory_delete', '删除实训室'),
        # 备份管理
        ('backup_create', '创建备份'),
        ('backup_delete', '删除备份'),
        ('backup_restore', '恢复备份'),
        # 系统设置
        ('system_setting_update', '更新系统设置'),
    ]

    operator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='operation_logs',
        verbose_name='操作人'
    )
    operator_username = models.CharField(
        max_length=150,
        blank=True,
        default='',
        verbose_name='操作人用户名',
        help_text='冗余字段，防止用户被删除后无法显示'
    )
    module = models.CharField(
        max_length=20,
        choices=MODULE_CHOICES,
        verbose_name='模块',
        db_index=True
    )
    operation_type = models.CharField(
        max_length=30,
        choices=OPERATION_TYPE_CHOICES,
        verbose_name='操作类型',
        db_index=True
    )
    target_type = models.CharField(
        max_length=50,
        blank=True,
        default='',
        verbose_name='目标对象类型',
        help_text='如: User, Equipment, Schedule'
    )
    target_id = models.IntegerField(
        null=True,
        blank=True,
        verbose_name='目标对象ID'
    )
    target_name = models.CharField(
        max_length=200,
        blank=True,
        default='',
        verbose_name='目标对象名称',
        help_text='便于阅读的名称描述'
    )
    description = models.TextField(
        blank=True,
        default='',
        verbose_name='操作描述',
        help_text='自然语言描述，如: 张三添加了用户李四'
    )
    detail = models.JSONField(
        null=True,
        blank=True,
        verbose_name='详细信息',
        help_text='记录修改前后的值等详细信息'
    )
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name='操作IP地址'
    )
    user_agent = models.CharField(
        max_length=255,
        blank=True,
        default='',
        verbose_name='用户代理'
    )
    request_id = models.CharField(
        max_length=50,
        blank=True,
        default='',
        verbose_name='请求ID',
        help_text='关联请求，便于追踪完整请求链路'
    )

    class Meta:
        db_table = 'system_operation_log'
        verbose_name = '系统操作日志'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['module', 'operation_type']),
            models.Index(fields=['operator', 'created_at']),
            models.Index(fields=['target_type', 'target_id']),
            models.Index(fields=['-created_at']),
        ]

    def __str__(self):
        return f"{self.get_operation_type_display()} - {self.target_name} - {self.operator_username} - {self.created_at}"

    @classmethod
    def create_log(cls, request, module: str, operation_type: str,
                   target_type: str = '', target_id: int = None,
                   target_name: str = '', description: str = '',
                   detail: dict = None):
        """
        创建操作日志

        Args:
            request: Django request 对象
            module: 模块标识 (user, equipment, schedule, etc.)
            operation_type: 操作类型 (user_create, equipment_delete, etc.)
            target_type: 目标对象类型 (User, Equipment, Schedule)
            target_id: 目标对象 ID
            target_name: 目标对象可读名称
            description: 操作描述（自然语言）
            detail: 详细信息（JSON格式）
        """
        operator = None
        operator_username = ''

        if request and hasattr(request, 'user') and request.user.is_authenticated:
            operator = request.user
            operator_username = request.user.nickname or request.user.username

        ip_address = ''
        user_agent = ''
        request_id = ''

        if request:
            ip_address = request.META.get('REMOTE_ADDR', '') or \
                        request.META.get('HTTP_X_FORWARDED_FOR', '').split(',')[0].strip()
            user_agent = request.META.get('HTTP_USER_AGENT', '')[:255]
            request_id = getattr(request, 'request_id', '') or \
                         request.META.get('X-Request-ID', '')

        return cls.objects.create(
            operator=operator,
            operator_username=operator_username,
            module=module,
            operation_type=operation_type,
            target_type=target_type,
            target_id=target_id,
            target_name=target_name[:200],
            description=description,
            detail=detail,
            ip_address=ip_address or None,
            user_agent=user_agent,
            request_id=request_id
        )

    @classmethod
    def get_module_operations(cls, module: str) -> list:
        """获取指定模块的所有操作类型"""
        return [choice for choice in cls.OPERATION_TYPE_CHOICES if choice[0].startswith(module)]
