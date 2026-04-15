"""
工单序列化器
"""

from rest_framework import serializers
from apps.maintenance.models import WorkOrder


class WorkOrderSerializer(serializers.ModelSerializer):
    """工单序列化器"""
    
    laboratory_name = serializers.SerializerMethodField()
    laboratory_code = serializers.SerializerMethodField()
    reporter_name = serializers.CharField(source='reporter.nickname', read_only=True)
    handler_name = serializers.SerializerMethodField()
    semester_name = serializers.CharField(source='semester.name', read_only=True)
    equipment_name = serializers.SerializerMethodField()
    status_display = serializers.SerializerMethodField()
    maintenance_type_display = serializers.SerializerMethodField()
    
    class Meta:
        model = WorkOrder
        fields = [
            'id', 'order_number', 'title', 'description', 'laboratory', 'laboratory_name', 'laboratory_code',
            'equipment', 'equipment_name', 'semester', 'semester_name', 'maintenance_type',
            'maintenance_type_display', 'status', 'status_display', 'priority',
            'reporter', 'reporter_name', 'handler', 'handler_name',
            'reported_at', 'assigned_at', 'started_at', 'completed_at', 'closed_at',
            'solution', 'handle_note', 'rating', 'feedback', 'is_archived',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'order_number', 'created_at', 'updated_at', 'reported_at']
    
    def get_laboratory_name(self, obj):
        if obj.laboratory:
            return obj.laboratory.name
        return obj.laboratory_name or ''
    
    def get_laboratory_code(self, obj):
        if obj.laboratory:
            return obj.laboratory.code
        return obj.laboratory_code or ''
    
    def get_handler_name(self, obj):
        return obj.handler.nickname if obj.handler else ''
    
    def get_equipment_name(self, obj):
        return obj.equipment.name if obj.equipment else None
    
    def get_status_display(self, obj):
        from apps.core.constants import WorkOrderStatus
        status_map = {
            WorkOrderStatus.PENDING: '待处理',
            WorkOrderStatus.PROCESSING: '处理中',
            WorkOrderStatus.COMPLETED: '已完成',
            WorkOrderStatus.CLOSED: '已关闭',
        }
        return status_map.get(obj.status, obj.status)
    
    def get_maintenance_type_display(self, obj):
        from apps.core.constants import MaintenanceType
        type_map = {
            MaintenanceType.ROUTINE: '检查维护',
            MaintenanceType.SAFETY: '安全检查',
            MaintenanceType.REPAIR: '设备维修',
        }
        return type_map.get(obj.maintenance_type, str(obj.maintenance_type))


class WorkOrderCreateSerializer(serializers.ModelSerializer):
    """工单创建序列化器"""
    
    laboratory_id = serializers.IntegerField(required=True)
    equipment_id = serializers.IntegerField(required=False, allow_null=True)
    
    class Meta:
        model = WorkOrder
        fields = [
            'title', 'description', 'laboratory_id', 'equipment_id',
            'maintenance_type', 'priority', 'handle_note'
        ]
    
    def validate_title(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError('工单标题不能为空')
        return value.strip()
    
    def validate_description(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError('问题描述不能为空')
        return value.strip()


class WorkOrderUpdateSerializer(serializers.ModelSerializer):
    """工单更新序列化器"""
    
    class Meta:
        model = WorkOrder
        fields = [
            'title', 'description', 'priority', 'maintenance_type', 'handle_note'
        ]
    
    def validate_title(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError('工单标题不能为空')
        return value.strip()
    
    def validate_description(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError('问题描述不能为空')
        return value.strip()


class WorkOrderAssignSerializer(serializers.Serializer):
    """工单分配序列化器"""
    
    handler_id = serializers.IntegerField(required=True)


class WorkOrderCompleteSerializer(serializers.Serializer):
    """工单完成序列化器"""
    
    solution = serializers.CharField(required=True)


class WorkOrderCloseSerializer(serializers.Serializer):
    """工单关闭序列化器"""
    
    feedback = serializers.CharField(required=False, allow_blank=True, default='')


class BatchDeleteSerializer(serializers.Serializer):
    """批量删除序列化器"""
    
    ids = serializers.ListField(
        child=serializers.IntegerField(min_value=1),
        allow_empty=False,
        help_text='要删除的ID列表'
    )
