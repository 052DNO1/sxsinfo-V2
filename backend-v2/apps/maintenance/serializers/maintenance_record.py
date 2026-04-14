"""
维护记录序列化器
"""

from rest_framework import serializers
from apps.maintenance.models import MaintenanceRecord


class MaintenanceRecordSerializer(serializers.ModelSerializer):
    """维护记录序列化器"""
    
    laboratory_name = serializers.CharField(source='laboratory.name', read_only=True)
    laboratory_code = serializers.CharField(source='laboratory.code', read_only=True)
    maintainer_name = serializers.SerializerMethodField()
    semester_name = serializers.CharField(source='semester.name', read_only=True)
    status_display = serializers.SerializerMethodField()
    order_type_display = serializers.SerializerMethodField()
    
    class Meta:
        model = MaintenanceRecord
        fields = [
            'id', 'order_number', 'order_type', 'order_type_display',
            'laboratory', 'laboratory_name', 'laboratory_code',
            'maintainer', 'maintainer_name', 'content', 'status', 'status_display',
            'maintenance_time', 'semester', 'semester_name', 'note',
            'is_archived', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'order_number', 'created_at', 'updated_at']
    
    def get_maintainer_name(self, obj):
        return obj.maintainer.nickname if obj.maintainer else ''
    
    def get_status_display(self, obj):
        status_map = {
            'maintained': '已维护',
            'pending': '待维护',
            'processing': '维护中',
        }
        return status_map.get(obj.status, obj.status)
    
    def get_order_type_display(self, obj):
        order_type_map = {
            'W': '维护',
            'G': '故障',
        }
        return order_type_map.get(obj.order_type, obj.order_type)


class MaintenanceRecordCreateSerializer(serializers.ModelSerializer):
    """维护记录创建序列化器"""
    
    laboratory_id = serializers.IntegerField(required=True)
    maintainer_id = serializers.IntegerField(required=False, allow_null=True)
    
    class Meta:
        model = MaintenanceRecord
        fields = [
            'laboratory_id', 'maintainer_id', 'content', 'status',
            'maintenance_time', 'note', 'order_type'
        ]
    
    def validate_content(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError('维护内容不能为空')
        return value.strip()


class MaintenanceRecordUpdateSerializer(serializers.ModelSerializer):
    """维护记录更新序列化器"""
    
    laboratory_id = serializers.IntegerField(required=False)
    maintainer_id = serializers.IntegerField(required=False, allow_null=True)
    
    class Meta:
        model = MaintenanceRecord
        fields = [
            'laboratory_id', 'maintainer_id', 'content', 'status',
            'maintenance_time', 'note'
        ]
    
    def validate_content(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError('维护内容不能为空')
        return value.strip()


class BatchDeleteSerializer(serializers.Serializer):
    """批量删除序列化器"""
    
    ids = serializers.ListField(
        child=serializers.IntegerField(min_value=1),
        allow_empty=False,
        help_text='要删除的ID列表'
    )
