"""
生产环境配置
"""

import os
from django.core.exceptions import ImproperlyConfigured
from .base import *


def _require_env(name: str) -> str:
    """必须从环境变量/.env 读取，缺失则启动失败（禁止静默 None/硬编码）"""
    value = os.environ.get(name)
    if not value:
        raise ImproperlyConfigured(f'{name} 未配置。请在环境变量/.env 中设置（参见 backend-v2/.env.example）')
    return value

DEBUG = False

# 生产环境 ALLOWED_HOSTS 必须显式配置，缺失即启动失败（禁止默认空/全放行）
_allowed_hosts_raw = os.environ.get('ALLOWED_HOSTS', '').strip()
if not _allowed_hosts_raw:
    raise ImproperlyConfigured(
        'ALLOWED_HOSTS 未配置。请在环境变量/.env 中设置逗号分隔的主机白名单'
        '（如 ALLOWED_HOSTS=lims.example.com,www.lims.example.com）'
    )
ALLOWED_HOSTS = [h.strip() for h in _allowed_hosts_raw.split(',') if h.strip()]

# ─────────────────────────────────────────────
# 🖥️ 桌面端(Tauri) 远程连接 CORS 配置
# 允许桌面端应用直连后端 API（绕过 Nginx）
# ─────────────────────────────────────────────
# 生产 CORS 默认 fail-closed：必须显式配置来源白名单，禁止默认 '*' 全放行
_cors_raw = os.environ.get('CORS_ALLOWED_ORIGINS', '').strip()
if not _cors_raw or _cors_raw == '*':
    raise ImproperlyConfigured(
        'CORS_ALLOWED_ORIGINS 未配置或为 *. 生产环境必须显式设置来源白名单'
        '（如 CORS_ALLOWED_ORIGINS=https://lims.example.com）'
    )
CORS_ALLOWED_ORIGINS = [o.strip() for o in _cors_raw.split(',') if o.strip()]
CORS_ALLOW_ALL_ORIGINS = False
# Tauri 桌面端 Origin 白名单
CORS_ALLOWED_ORIGINS.append('tauri://localhost')
CORS_ALLOWED_ORIGINS.append('http://tauri.localhost')
CORS_ALLOWED_ORIGINS.append('https://tauri.localhost')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': _require_env('DB_NAME'),
        'USER': _require_env('DB_USER'),
        'PASSWORD': _require_env('DB_PASSWORD'),
        'HOST': _require_env('DB_HOST'),
        'PORT': _require_env('DB_PORT'),
        'OPTIONS': {
            'charset': 'utf8mb4',
            'init_command': "SET SQL_MODE='STRICT_TRANS_TABLES'",
        },
        'CONN_MAX_AGE': 60,
    }
}

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': os.environ.get('REDIS_URL'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'

if os.environ.get('USE_HTTPS') == 'true':
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ.get('EMAIL_HOST')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL')

# 日志文件路径可配置（默认沿用 base 的 BASE_DIR/logs/django.log，
# 容器内可设 LOG_FILE_PATH=/app/logs/django.log；避免硬编码容器路径导致容器外启动崩溃）
if os.environ.get('LOG_FILE_PATH'):
    LOGGING['handlers']['file']['filename'] = os.environ['LOG_FILE_PATH']
