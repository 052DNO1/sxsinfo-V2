"""
异常处理
"""

from rest_framework.views import exception_handler
from rest_framework import status
from common.responses import ApiResponse


def custom_exception_handler(exc, context):
    """自定义异常处理器"""
    response = exception_handler(exc, context)
    
    if response is not None:
        return ApiResponse.error(
            message=str(exc.detail) if hasattr(exc, 'detail') else str(exc),
            code='ERROR',
            status_code=response.status_code
        )
    
    return None
