"""
测试环境配置
"""

from .base import *

DEBUG = True
ALLOWED_HOSTS = ['*']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db_test.sqlite3',
    }
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}


class LocMemCacheCompat:
    @staticmethod
    def patch():
        from django.core.cache.backends.locmem import LocMemCache

        if not hasattr(LocMemCache, 'ttl'):
            def ttl(self, key, version=None):
                return 0
            LocMemCache.ttl = ttl

        if not hasattr(LocMemCache, 'keys'):
            def keys(self, pattern=None, version=None):
                # 真扫描 LocMemCache（django-redis 的 keys 为 Redis KEYS 语义），
                # 使 delete_pattern 在测试环境可用。LocMemCache 内部 key 形如 ':1:xxx'。
                import fnmatch
                version = version if version is not None else self.version
                prefix = f':{version}:'
                matched = []
                for raw_key in list(self._cache.keys()):
                    # raw_key 形如 ':1:api:stats:dashboard:1'
                    stripped = raw_key[len(prefix):] if raw_key.startswith(prefix) else raw_key
                    if pattern is None or fnmatch.fnmatchcase(stripped, pattern):
                        matched.append(stripped)
                return matched
            LocMemCache.keys = keys

        if not hasattr(LocMemCache, 'expire'):
            def expire(self, key, timeout, version=None):
                pass
            LocMemCache.expire = expire

LocMemCacheCompat.patch()

PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=2),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': False,
    'ALGORITHM': 'HS256',
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
}

INSTALLED_APPS = [app for app in INSTALLED_APPS
                  if app not in ('rest_framework_simplejwt.token_blacklist',)]
