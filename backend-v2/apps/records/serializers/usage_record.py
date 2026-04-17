"""
使用记录序列化器
"""

from rest_framework import serializers
from apps.records.models import UsageRecord


class UsageRecordSerializer(serializers.ModelSerializer):
    """使用记录序列化器"""
    
    laboratory_name = serializers.SerializerMethodField()
    laboratory_code = serializers.SerializerMethodField()
    teacher_name = serializers.CharField(source='teacher.nickname', read_only=True)
    semester_name = serializers.CharField(source='semester.name', read_only=True)
    
    class Meta:
        model = UsageRecord
        fields = [
            'id', 'usage_date', 'time_slot', 'class_hours',
            'laboratory', 'laboratory_name', 'laboratory_code',
            'semester', 'semester_name', 'teacher', 'teacher_name',
            'class_name', 'student_count', 'content',
            'device_status', 'laboratory_status',
            'is_locked', 'is_archived', 'note',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_laboratory_name(self, obj):
        if obj.laboratory:
            return obj.laboratory.name
        return obj.laboratory_name or ''
    
    def get_laboratory_code(self, obj):
        if obj.laboratory:
            return obj.laboratory.code
        return obj.laboratory_code or ''


class UsageRecordCreateSerializer(serializers.ModelSerializer):
    """使用记录创建序列化器"""

    laboratory_id = serializers.IntegerField(required=True)
    teacher_id = serializers.IntegerField(required=False, allow_null=True)

    class Meta:
        model = UsageRecord
        fields = [
            'usage_date', 'time_slot', 'class_hours',
            'laboratory_id', 'teacher_id', 'class_name', 'student_count',
            'content', 'device_status', 'laboratory_status', 'note'
        ]


class UsageRecordUpdateSerializer(serializers.ModelSerializer):
    """使用记录更新序列化器"""

    laboratory_id = serializers.IntegerField(required=False)
    teacher_id = serializers.IntegerField(required=False, allow_null=True)

    class Meta:
        model = UsageRecord
        fields = [
            'usage_date', 'time_slot', 'class_hours',
            'laboratory_id', 'teacher_id', 'class_name', 'student_count',
            'content', 'device_status', 'laboratory_status', 'note'
        ]


class BatchDeleteSerializer(serializers.Serializer):
    """批量删除序列化器"""
    
    ids = serializers.ListField(
        child=serializers.IntegerField(min_value=1),
        allow_empty=False,
        help_text='要删除的ID列表'
    )
