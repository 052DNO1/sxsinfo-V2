"""
课表序列化器
"""

from rest_framework import serializers
from apps.schedules.models import Schedule, Semester


class ScheduleSerializer(serializers.ModelSerializer):
    """课表序列化器"""
    
    laboratory_name = serializers.CharField(source='laboratory.name', read_only=True)
    laboratory_code = serializers.CharField(source='laboratory.code', read_only=True)
    teacher_name_display = serializers.SerializerMethodField()
    semester_name = serializers.CharField(source='semester.name', read_only=True)
    weekday_display = serializers.SerializerMethodField()
    
    class Meta:
        model = Schedule
        fields = [
            'id', 'course_name', 'course_code', 'weekday', 'weekday_display',
            'time_slot', 'weeks', 'laboratory', 'laboratory_name', 'laboratory_code',
            'semester', 'semester_name', 'teacher', 'teacher_name', 'teacher_name_display',
            'class_name', 'student_count', 'is_active', 'is_archived', 'note',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_teacher_name_display(self, obj):
        return obj.teacher_name or (obj.teacher.nickname if obj.teacher else '')
    
    def get_weekday_display(self, obj):
        weekday_map = {1: '周一', 2: '周二', 3: '周三', 4: '周四', 5: '周五', 6: '周六', 7: '周日'}
        return weekday_map.get(obj.weekday, f"周{obj.weekday}")


class ScheduleCreateSerializer(serializers.ModelSerializer):
    """课表创建序列化器"""
    
    laboratory_id = serializers.IntegerField(required=True)
    teacher_id = serializers.IntegerField(required=False, allow_null=True)
    
    class Meta:
        model = Schedule
        fields = [
            'course_name', 'course_code', 'weekday', 'time_slot', 'weeks',
            'laboratory_id', 'teacher_id', 'teacher_name',
            'class_name', 'student_count', 'note'
        ]
    
    def validate_course_name(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError('课程名称不能为空')
        return value.strip()
    
    def validate_weekday(self, value):
        if value < 1 or value > 7:
            raise serializers.ValidationError('星期必须在1-7之间')
        return value


class ScheduleUpdateSerializer(serializers.ModelSerializer):
    """课表更新序列化器"""
    
    laboratory_id = serializers.IntegerField(required=False)
    teacher_id = serializers.IntegerField(required=False, allow_null=True)
    
    class Meta:
        model = Schedule
        fields = [
            'course_name', 'course_code', 'weekday', 'time_slot', 'weeks',
            'laboratory_id', 'teacher_id', 'teacher_name',
            'class_name', 'student_count', 'note'
        ]
    
    def validate_course_name(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError('课程名称不能为空')
        return value.strip()
    
    def validate_weekday(self, value):
        if value < 1 or value > 7:
            raise serializers.ValidationError('星期必须在1-7之间')
        return value


class ScheduleConflictCheckSerializer(serializers.Serializer):
    """课表冲突检测序列化器"""
    
    laboratory_id = serializers.IntegerField(required=True)
    weekday = serializers.IntegerField(required=True, min_value=1, max_value=7)
    time_slot = serializers.CharField(required=True, max_length=20)
    weeks = serializers.CharField(required=True, max_length=50)
    exclude_id = serializers.IntegerField(required=False, allow_null=True)


class BatchDeleteSerializer(serializers.Serializer):
    """批量删除序列化器"""
    
    ids = serializers.ListField(
        child=serializers.IntegerField(min_value=1),
        allow_empty=False,
        help_text='要删除的ID列表'
    )


class SemesterSerializer(serializers.ModelSerializer):
    """学期序列化器"""
    
    schedule_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Semester
        fields = [
            'id', 'name', 'code', 'start_date', 'end_date',
            'is_current', 'is_archived', 'total_weeks',
            'description', 'schedule_count', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_schedule_count(self, obj):
        return obj.get_schedule_count()


class SemesterCreateSerializer(serializers.ModelSerializer):
    """学期创建序列化器"""
    
    is_current = serializers.BooleanField(required=False, default=False)
    
    class Meta:
        model = Semester
        fields = ['name', 'code', 'start_date', 'end_date', 'total_weeks', 'description', 'is_current']
        extra_kwargs = {
            'code': {'required': False}
        }
    
    def validate_name(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError('学期名称不能为空')
        return value.strip()
    
    def create(self, validated_data):
        if 'code' not in validated_data or not validated_data['code']:
            name = validated_data.get('name', '')
            validated_data['code'] = name.lower().replace(' ', '_').replace('-', '_')
        return super().create(validated_data)
