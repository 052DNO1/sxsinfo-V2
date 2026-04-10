"""
Redis客户端配置
"""

import os
import redis
from django.conf import settings


def get_redis_client():
    """获取Redis客户端"""
    redis_url = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
    return redis.from_url(redis_url)


redis_client = get_redis_client()
