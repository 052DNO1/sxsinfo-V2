"""
自定义验证器
"""

import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _


def validate_phone(value):
    """验证手机号"""
    if not re.match(r'^1[3-9]\d{9}$', value):
        raise ValidationError(_('请输入有效的手机号码'))


def validate_id_card(value):
    """验证身份证号"""
    if not re.match(r'^\d{17}[\dXx]$', value):
        raise ValidationError(_('请输入有效的身份证号'))


def validate_password_strength(value):
    """验证密码强度"""
    if len(value) < 8:
        raise ValidationError(_('密码长度至少8位'))
    if not re.search(r'[A-Z]', value):
        raise ValidationError(_('密码必须包含大写字母'))
    if not re.search(r'[a-z]', value):
        raise ValidationError(_('密码必须包含小写字母'))
    if not re.search(r'\d', value):
        raise ValidationError(_('密码必须包含数字'))


class FileSizeValidator:
    """文件大小验证器"""

    def __init__(self, max_size_mb=10):
        self.max_size = max_size_mb * 1024 * 1024

    def __call__(self, value):
        if value.size > self.max_size:
            raise ValidationError(_(f'文件大小不能超过 {self.max_size // 1024 // 1024}MB'))


class FileExtensionValidator:
    """文件扩展名验证器"""

    def __init__(self, allowed_extensions=None):
        self.allowed_extensions = allowed_extensions or ['jpg', 'jpeg', 'png', 'pdf', 'xlsx', 'xls']

    def __call__(self, value):
        ext = value.name.split('.')[-1].lower()
        if ext not in self.allowed_extensions:
            raise ValidationError(_(f'不支持的文件类型: {ext}'))
