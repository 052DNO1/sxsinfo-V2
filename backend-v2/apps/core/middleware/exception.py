"""
全局异常处理中间件
"""

import logging
import traceback
from django.http import JsonResponse
from rest_framework import status
from apps.core.exceptions import LIMSException

logger = logging.getLogger(__name__)


class ExceptionMiddleware:
    """全局异常处理中间件"""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_exception(self, request, exception):
        """处理异常"""
        if isinstance(exception, LIMSException):
            logger.warning(
                f"业务异常: {exception.code} - {exception.message}",
                extra={'request': request}
            )
            return JsonResponse({
                'success': False,
                'code': exception.code,
                'message': exception.message,
                'data': exception.data
            }, status=exception.status_code)

        if hasattr(exception, 'detail'):
            logger.warning(f"验证错误: {exception.detail}")
            return JsonResponse({
                'success': False,
                'code': 'VALIDATION_ERROR',
                'message': str(exception.detail),
                'data': None
            }, status=status.HTTP_400_BAD_REQUEST)

        logger.error(
            f"系统异常: {str(exception)}\n{traceback.format_exc()}",
            extra={'request': request}
        )
        return JsonResponse({
            'success': False,
            'code': 'SYSTEM_ERROR',
            'message': '系统内部错误，请稍后重试',
            'data': None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
