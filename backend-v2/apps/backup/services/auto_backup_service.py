"""
自动备份配置服务
"""

from django.core.cache import cache
from apps.core.exceptions import PermissionDenied, ValidationError
from apps.backup.models import AutoBackupConfig


class AutoBackupConfigService:
    """自动备份配置服务"""

    CACHE_KEY = 'auto_backup_config'

    def get_config(self, requester) -> dict:
        if not requester.is_super_admin:
            raise PermissionDenied('仅超级管理员可执行此操作')
        
        config = AutoBackupConfig.objects.filter(is_deleted=False).first()
        
        if config:
            return {
                'enabled': config.enabled,
                'period': config.period,
                'last_backup_time': config.last_backup_time.strftime('%Y-%m-%d %H:%M:%S') if config.last_backup_time else None,
                'next_backup_time': config.next_backup_time.strftime('%Y-%m-%d %H:%M:%S') if config.next_backup_time else None,
            }
        else:
            return {
                'enabled': False,
                'period': 'daily',
                'last_backup_time': None,
                'next_backup_time': None,
            }

    def save_config(self, requester, data: dict) -> dict:
        if not requester.is_super_admin:
            raise PermissionDenied('仅超级管理员可执行此操作')
        
        enabled = data.get('enabled', False)
        period = data.get('period', 'daily')
        
        if period not in ['daily', 'weekly', 'monthly']:
            raise ValidationError('无效的备份周期')
        
        config, created = AutoBackupConfig.objects.update_or_create(
            is_deleted=False,
            defaults={
                'enabled': enabled,
                'period': period,
            }
        )
        
        cache.delete(self.CACHE_KEY)
        
        return {
            'enabled': config.enabled,
            'period': config.period,
            'message': '配置保存成功'
        }
