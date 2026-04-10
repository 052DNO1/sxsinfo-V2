"""
日志中间件
"""

import logging
import time
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger(__name__)


class LoggingMiddleware(MiddlewareMixin):
    """请求日志中间件"""

    def process_request(self, request):
        request.start_time = time.time()
        logger.info(f"请求开始: {request.method} {request.path}")

    def process_response(self, request, response):
        if hasattr(request, 'start_time'):
            duration = time.time() - request.start_time
            logger.info(
                f"请求结束: {request.method} {request.path} "
                f"状态码: {response.status_code} 耗时: {duration:.2f}s"
            )
        return response
