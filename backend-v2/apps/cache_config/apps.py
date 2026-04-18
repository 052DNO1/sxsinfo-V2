from django.apps import AppConfig


class CacheConfigConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.cache_config'
    verbose_name = '缓存配置管理'
