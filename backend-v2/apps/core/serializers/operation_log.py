"""
系统操作日志序列化器
"""

from rest_framework import serializers
from apps.core.models import SystemOperationLog


class SystemOperationLogSerializer(serializers.ModelSerializer):
    """操作日志序列化器"""

    operator_info = serializers.SerializerMethodField()
    operation_type_display = serializers.CharField(source='get_operation_type_display', read_only=True)
    module_display = serializers.CharField(source='get_module_display', read_only=True)

    class Meta:
        model = SystemOperationLog
        fields = [
            'id',
            'operator',
            'operator_username',
            'operator_info',
            'module',
            'module_display',
            'operation_type',
            'operation_type_display',
            'target_type',
            'target_id',
            'target_name',
            'description',
            'detail',
            'ip_address',
            'user_agent',
            'request_id',
            'created_at',
        ]
        read_only_fields = fields

    def get_operator_info(self, obj):
        """获取操作人详细信息"""
        if obj.operator:
            return {
                'id': obj.operator.id,
                'username': obj.operator.username,
                'nickname': obj.operator.nickname or obj.operator.username,
                'avatar': obj.operator.avatar.url if obj.operator.avatar else None,
            }
        return {
            'id': None,
            'username': obj.operator_username,
            'nickname': obj.operator_username,
            'avatar': None,
        }


class SystemOperationLogListSerializer(serializers.ModelSerializer):
    """操作日志列表序列化器（精简版）"""

    operation_type_display = serializers.CharField(source='get_operation_type_display', read_only=True)
    module_display = serializers.CharField(source='get_module_display', read_only=True)

    class Meta:
        model = SystemOperationLog
        fields = [
            'id',
            'operator_username',
            'module',
            'module_display',
            'operation_type',
            'operation_type_display',
            'target_name',
            'description',
            'ip_address',
            'created_at',
        ]
        read_only_fields = fields


class OperationLogStatsSerializer(serializers.Serializer):
    """操作日志统计序列化器"""
    
    total_count = serializers.IntegerField()
    today_count = serializers.IntegerField()
    week_count = serializers.IntegerField()
    module_stats = serializers.ListField()
    recent_operations = SystemOperationLogListSerializer(many=True)
