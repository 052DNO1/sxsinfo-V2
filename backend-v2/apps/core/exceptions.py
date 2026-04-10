"""
自定义异常类
"""

from rest_framework import status


class LIMSException(Exception):
    """基础异常类"""
    default_message = "系统错误"
    default_code = "SYSTEM_ERROR"
    default_status_code = status.HTTP_400_BAD_REQUEST

    def __init__(self, message=None, code=None, status_code=None, data=None):
        self.message = message or self.default_message
        self.code = code or self.default_code
        self.status_code = status_code or self.default_status_code
        self.data = data
        super().__init__(self.message)


class ValidationError(LIMSException):
    """验证错误"""
    default_message = "数据验证失败"
    default_code = "VALIDATION_ERROR"


class AuthenticationError(LIMSException):
    """认证错误"""
    default_message = "认证失败"
    default_code = "AUTHENTICATION_ERROR"
    default_status_code = status.HTTP_401_UNAUTHORIZED


class PermissionDenied(LIMSException):
    """权限不足"""
    default_message = "权限不足"
    default_code = "PERMISSION_DENIED"
    default_status_code = status.HTTP_403_FORBIDDEN


class NotFoundError(LIMSException):
    """资源不存在"""
    default_message = "资源不存在"
    default_code = "NOT_FOUND"
    default_status_code = status.HTTP_404_NOT_FOUND


class ConflictError(LIMSException):
    """资源冲突"""
    default_message = "资源冲突"
    default_code = "CONFLICT"
    default_status_code = status.HTTP_409_CONFLICT


class ScheduleConflictError(ConflictError):
    """课表冲突"""
    default_message = "课表时间冲突"
    default_code = "SCHEDULE_CONFLICT"


class BusinessError(LIMSException):
    """业务逻辑错误"""
    default_message = "业务处理失败"
    default_code = "BUSINESS_ERROR"
