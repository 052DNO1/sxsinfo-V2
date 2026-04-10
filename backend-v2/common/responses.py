"""
统一响应格式
"""

from rest_framework.response import Response
from rest_framework import status


class ApiResponse(Response):
    """统一API响应类"""

    def __init__(
        self,
        data=None,
        message='操作成功',
        code='SUCCESS',
        success=True,
        status_code=status.HTTP_200_OK,
        **kwargs
    ):
        response_data = {
            'success': success,
            'code': code,
            'message': message,
            'data': data
        }
        response_data.update(kwargs)
        super().__init__(data=response_data, status=status_code)

    @classmethod
    def success(cls, data=None, message='操作成功', **kwargs):
        """成功响应"""
        return cls(data=data, message=message, **kwargs)

    @classmethod
    def error(cls, message='操作失败', code='ERROR', data=None,
              status_code=status.HTTP_400_BAD_REQUEST, **kwargs):
        """错误响应"""
        return cls(
            data=data,
            message=message,
            code=code,
            success=False,
            status_code=status_code,
            **kwargs
        )

    @classmethod
    def created(cls, data=None, message='创建成功'):
        """创建成功响应"""
        return cls(
            data=data,
            message=message,
            code='CREATED',
            status_code=status.HTTP_201_CREATED
        )

    @classmethod
    def not_found(cls, message='资源不存在'):
        """资源不存在响应"""
        return cls.error(
            message=message,
            code='NOT_FOUND',
            status_code=status.HTTP_404_NOT_FOUND
        )

    @classmethod
    def forbidden(cls, message='权限不足'):
        """权限不足响应"""
        return cls.error(
            message=message,
            code='FORBIDDEN',
            status_code=status.HTTP_403_FORBIDDEN
        )

    @classmethod
    def unauthorized(cls, message='未授权'):
        """未授权响应"""
        return cls.error(
            message=message,
            code='UNAUTHORIZED',
            status_code=status.HTTP_401_UNAUTHORIZED
        )
