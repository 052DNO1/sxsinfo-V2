"""
用户序列化器
"""

import re
from rest_framework import serializers
from apps.users.models import User, Department
from apps.core.utils import beijing_strftime, beijing_now, beijing_today


def validate_username_format(value):
    if not re.match(r'^[a-zA-Z0-9_]+$', value):
        raise serializers.ValidationError('用户名只能包含字母、数字和下划线')
    return value


class UserSerializer(serializers.ModelSerializer):
    """用户序列化器"""
    
    department_name = serializers.SerializerMethodField()
    roles = serializers.SerializerMethodField()
    created_at = serializers.SerializerMethodField()
    updated_at = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'nickname', 'phone', 'email',
            'role', 'roles', 'status', 'department', 'department_name',
            'first_login', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'first_login']
    
    def get_roles(self, obj):
        try:
            return obj.get_roles()
        except Exception:
            return []
    
    def get_department_name(self, obj):
        return obj.department.name if obj.department else None
    
    def get_created_at(self, obj):
        if obj.created_at:
            return beijing_strftime(obj.created_at)
        return None
    
    def get_updated_at(self, obj):
        if obj.updated_at:
            return beijing_strftime(obj.updated_at)
        return None


class UserCreateSerializer(serializers.ModelSerializer):
    """用户创建序列化器"""
    
    password = serializers.CharField(write_only=True, required=False, allow_blank=True)
    department = serializers.PrimaryKeyRelatedField(
        queryset=Department.objects.all(),
        required=False,
        allow_null=True
    )
    
    class Meta:
        model = User
        fields = [
            'username', 'password', 'nickname', 'phone', 'email',
            'role', 'status', 'department'
        ]
        extra_kwargs = {
            'username': {'validators': []}
        }
    
    def validate_username(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError('用户名不能为空')
        username = value.strip()
        validate_username_format(username)
        if User.objects.filter(username=username, is_deleted=False).exists():
            raise serializers.ValidationError(f'用户名 "{username}" 已存在')
        return username
    
    def validate_department(self, value):
        if value == '' or value == 'null':
            return None
        return value
    
    def validate_phone(self, value):
        if value == '' or value is None:
            return ''
        return value
    
    def validate_email(self, value):
        if value == '' or value is None:
            return ''
        return value
    
    def create(self, validated_data):
        password = validated_data.pop('password', None)
        username = validated_data.get('username', '')
        if not password:
            password = username[:6]
        user = User.objects.create_user(**validated_data, password=password)
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    """用户更新序列化器（管理员编辑其他用户）"""
    
    class Meta:
        model = User
        fields = ['nickname', 'phone', 'email', 'role', 'status', 'department']


class UserProfileSerializer(serializers.ModelSerializer):
    """用户个人信息序列化器（用户自己修改自己的资料）"""
    
    department_name = serializers.SerializerMethodField()
    roles = serializers.SerializerMethodField()
    last_login = serializers.SerializerMethodField()
    created_at = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'nickname', 'phone', 'email',
            'role', 'roles', 'status', 'department', 'department_name',
            'first_login', 'last_login', 'created_at'
        ]
        read_only_fields = ['id', 'role', 'status', 'department', 'first_login']
    
    def validate_username(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError('用户名不能为空')
        username = value.strip()
        validate_username_format(username)
        user = self.instance
        if user and User.objects.filter(username=username, is_deleted=False).exclude(id=user.id).exists():
            raise serializers.ValidationError(f'用户名 "{username}" 已存在')
        return username
    
    def get_roles(self, obj):
        try:
            return obj.get_roles()
        except Exception:
            return []
    
    def get_department_name(self, obj):
        return obj.department.name if obj.department else None
    
    def get_last_login(self, obj):
        if obj.last_login:
            return beijing_strftime(obj.last_login)
        return None
    
    def get_created_at(self, obj):
        if obj.created_at:
            return beijing_strftime(obj.created_at)
        return None


class DepartmentSerializer(serializers.ModelSerializer):
    """部门序列化器"""
    
    user_count = serializers.SerializerMethodField()
    managers = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        many=True,
        required=False
    )
    manager_names = serializers.SerializerMethodField()
    manager_ids = serializers.SerializerMethodField()
    code = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    force_update = serializers.BooleanField(required=False, default=False, write_only=True)
    
    class Meta:
        model = Department
        fields = [
            'id', 'name', 'code', 'parent', 'managers', 'manager_names', 'manager_ids', 'description',
            'order', 'is_active', 'phone', 'email', 'address', 'user_count', 'force_update'
        ]
    
    def get_user_count(self, obj):
        return obj.get_user_count()
    
    def get_manager_names(self, obj):
        return [u.nickname or u.username for u in obj.managers.all()]
    
    def get_manager_ids(self, obj):
        return [u.id for u in obj.managers.all()]


class DepartmentTreeSerializer(serializers.ModelSerializer):
    """部门树序列化器"""
    
    children = serializers.SerializerMethodField()
    
    class Meta:
        model = Department
        fields = ['id', 'name', 'code', 'parent_id', 'children']
    
    def get_children(self, obj):
        children = obj.get_children()
        return DepartmentTreeSerializer(children, many=True).data


class BatchDeleteSerializer(serializers.Serializer):
    """批量删除序列化器"""
    
    ids = serializers.ListField(
        child=serializers.IntegerField(),
        help_text='要删除的ID列表'
    )
