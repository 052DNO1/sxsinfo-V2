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
                return []
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
