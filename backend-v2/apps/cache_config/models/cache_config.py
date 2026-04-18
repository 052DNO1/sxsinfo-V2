"""
缓存配置管理模型
提供API缓存配置、请求统计、操作日志功能
"""

from django.db import models
from django.conf import settings
from apps.core.models import BaseModel


class CacheConfig(BaseModel):
    """缓存配置模型"""
    
    api_path = models.CharField(
        max_length=200,
        unique=True,
        verbose_name='API路径'
    )
    frontend_ttl = models.IntegerField(
        default=60,
        verbose_name='前端缓存时间(秒)'
    )
    backend_ttl = models.IntegerField(
        default=300,
        verbose_name='后端缓存时间(秒)'
    )
    enabled = models.BooleanField(
        default=True,
        verbose_name='是否启用缓存'
    )
    description = models.TextField(
        blank=True,
        verbose_name='配置说明'
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='updated_cache_configs',
        verbose_name='最后更新人'
    )
    
    class Meta:
        db_table = 'cache_config'
        verbose_name = '缓存配置'
        verbose_name_plural = verbose_name
        ordering = ['api_path']
    
    def __str__(self):
        return f"{self.api_path} (前端:{self.frontend_ttl}s, 后端:{self.backend_ttl}s)"
    
    @classmethod
    def get_config(cls, api_path: str):
        """获取指定API的缓存配置"""
        try:
            return cls.objects.get(api_path=api_path, enabled=True)
        except cls.DoesNotExist:
            return None
    
    @classmethod
    def get_all_configs(cls):
        """获取所有启用的缓存配置"""
        return cls.objects.filter(enabled=True)


class ApiStats(BaseModel):
    """API统计模型 - 按天聚合"""
    
    api_path = models.CharField(
        max_length=200,
        verbose_name='API路径'
    )
    date = models.DateField(
        verbose_name='统计日期'
    )
    request_count = models.IntegerField(
        default=0,
        verbose_name='请求次数'
    )
    cache_hit_count = models.IntegerField(
        default=0,
        verbose_name='缓存命中次数'
    )
    total_response_time = models.FloatField(
        default=0,
        verbose_name='总响应时间(ms)'
    )
    error_count = models.IntegerField(
        default=0,
        verbose_name='错误次数'
    )
    
    class Meta:
        db_table = 'api_stats'
        verbose_name = 'API统计'
        verbose_name_plural = verbose_name
        unique_together = ['api_path', 'date']
        ordering = ['-date', 'api_path']
    
    def __str__(self):
        return f"{self.api_path} - {self.date} ({self.request_count}次)"
    
    @property
    def avg_response_time(self):
        """平均响应时间"""
        if self.request_count > 0:
            return round(self.total_response_time / self.request_count, 2)
        return 0
    
    @property
    def cache_hit_rate(self):
        """缓存命中率"""
        if self.request_count > 0:
            return round(self.cache_hit_count / self.request_count * 100, 2)
        return 0
    
    @classmethod
    def get_today_stats(cls, api_path: str):
        """获取今日统计"""
        from django.utils import timezone
        today = timezone.now().date()
        try:
            return cls.objects.get(api_path=api_path, date=today)
        except cls.DoesNotExist:
            return None
    
    @classmethod
    def get_date_range_stats(cls, api_path: str, start_date, end_date):
        """获取日期范围内的统计"""
        return cls.objects.filter(
            api_path=api_path,
            date__gte=start_date,
            date__lte=end_date
        ).order_by('date')


class CacheOperationLog(BaseModel):
    """缓存操作日志模型"""
    
    OPERATION_TYPES = [
        ('config_create', '创建配置'),
        ('config_update', '更新配置'),
        ('config_delete', '删除配置'),
        ('cache_clear', '清除缓存'),
        ('cache_clear_all', '清除所有缓存'),
        ('cache_warmup', '缓存预热'),
    ]
    
    operator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='cache_operation_logs',
        verbose_name='操作人'
    )
    operation_type = models.CharField(
        max_length=20,
        choices=OPERATION_TYPES,
        verbose_name='操作类型'
    )
    api_path = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='API路径'
    )
    old_value = models.JSONField(
        null=True,
        blank=True,
        verbose_name='修改前的值'
    )
    new_value = models.JSONField(
        null=True,
        blank=True,
        verbose_name='修改后的值'
    )
    reason = models.TextField(
        blank=True,
        verbose_name='操作原因'
    )
    ip_address = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='操作IP'
    )
    user_agent = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='用户代理'
    )
    
    class Meta:
        db_table = 'cache_operation_log'
        verbose_name = '缓存操作日志'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_operation_type_display()} - {self.api_path} - {self.created_at}"
    
    @classmethod
    def create_log(cls, request, operation_type: str, api_path: str = '',
                   old_value=None, new_value=None, reason: str = ''):
        """创建操作日志"""
        return cls.objects.create(
            operator=request.user if request.user.is_authenticated else None,
            operation_type=operation_type,
            api_path=api_path,
            old_value=old_value,
            new_value=new_value,
            reason=reason,
            ip_address=request.META.get('REMOTE_ADDR', ''),
            user_agent=request.META.get('HTTP_USER_AGENT', '')[:255]
        )
