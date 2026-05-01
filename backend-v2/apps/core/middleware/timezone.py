"""
时区中间件
确保每个请求都使用北京时间（Asia/Shanghai）
"""

from django.utils import timezone
from django.conf import settings


class BeijingTimezoneMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        timezone.activate(settings.TIME_ZONE)
        return self.get_response(request)
