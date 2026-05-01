"""
认证序列化器
"""

import re
from rest_framework import serializers


class LoginSerializer(serializers.Serializer):
    """登录序列化器"""
    
    username = serializers.CharField(required=True, max_length=150)
    password = serializers.CharField(required=True, max_length=128)
    captcha_key = serializers.CharField(required=False, max_length=100)
    captcha = serializers.CharField(required=False, max_length=10)
    
    def validate_username(self, value):
        if not re.match(r'^[a-zA-Z0-9_]+$', value):
            raise serializers.ValidationError('用户名格式不正确')
        return value


class TokenRefreshSerializer(serializers.Serializer):
    """Token刷新序列化器"""
    
    refresh_token = serializers.CharField(required=True)


class ChangePasswordSerializer(serializers.Serializer):
    """修改密码序列化器"""
    
    old_pwd = serializers.CharField(required=True, max_length=128)
    new_pwd = serializers.CharField(required=True, max_length=128)
    confirm_pwd = serializers.CharField(required=True, max_length=128)
    
    def validate(self, data):
        if data['new_pwd'] != data['confirm_pwd']:
            raise serializers.ValidationError('两次密码输入不一致')
        return data


class CaptchaVerifySerializer(serializers.Serializer):
    """验证码校验序列化器"""
    
    captcha_key = serializers.CharField(required=True, max_length=100)
    captcha = serializers.CharField(required=True, max_length=10)


class SecurityQuestionSetSerializer(serializers.Serializer):
    """设置密保问题序列化器"""
    
    question = serializers.CharField(required=True, max_length=100)
    answer = serializers.CharField(required=True, min_length=2, max_length=50)


class UserSecurityQuestionSerializer(serializers.Serializer):
    """获取用户密保问题序列化器"""
    
    username = serializers.CharField(required=True, max_length=150)
    
    def validate_username(self, value):
        if not re.match(r'^[a-zA-Z0-9@.\-_]+$', value):
            raise serializers.ValidationError('用户名格式不正确')
        return value


class VerifySecurityAnswerSerializer(serializers.Serializer):
    """验证密保答案序列化器"""
    
    username = serializers.CharField(required=True, max_length=150)
    answer = serializers.CharField(required=True, max_length=50)


class ResetPasswordBySecuritySerializer(serializers.Serializer):
    """通过密保重置密码序列化器"""
    
    reset_token = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, max_length=128)
    confirm_password = serializers.CharField(required=True, max_length=128)
    
    def validate(self, data):
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError('两次密码输入不一致')
        return data


class PasswordResetContactSerializer(serializers.Serializer):
    """密码重置联系人序列化器"""
    
    username = serializers.CharField(required=True, max_length=150)
    
    def validate_username(self, value):
        if not re.match(r'^[a-zA-Z0-9@.\-_]+$', value):
            raise serializers.ValidationError('用户名格式不正确')
        return value


class AdminResetPasswordSerializer(serializers.Serializer):
    """管理员重置密码序列化器"""
    
    user_id = serializers.IntegerField(required=True)


class BatchResetPasswordSerializer(serializers.Serializer):
    """批量重置密码序列化器"""
    
    user_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=True
    )
