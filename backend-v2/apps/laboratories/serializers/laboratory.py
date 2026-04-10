"""
实训室序列化器
"""

from rest_framework import serializers
from apps.laboratories.models import Laboratory, Equipment


class LaboratorySerializer(serializers.ModelSerializer):
    """实训室序列化器"""
    
    department_name = serializers.CharField(source='department.name', read_only=True)
    admin_name = serializers.CharField(source='admin.nickname', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    equipment_count = serializers.SerializerMethodField()
    schedule_count = serializers.SerializerMethodField()
    location = serializers.CharField(read_only=True)
    
    class Meta:
        model = Laboratory
        fields = [
            'id', 'name', 'code', 'building', 'floor', 'room_number', 'location',
            'capacity', 'area', 'laboratory_type', 'department', 'department_name',
            'admin', 'admin_name', 'status', 'status_display', 'is_available', 'facilities',
            'description', 'note', 'images', 'equipment_count', 'schedule_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_equipment_count(self, obj):
        return obj.get_equipment_count()
    
    def get_schedule_count(self, obj):
        return obj.get_schedule_count()


class LaboratoryCreateSerializer(serializers.ModelSerializer):
    """实训室创建序列化器"""
    
    class Meta:
        model = Laboratory
        fields = [
            'name', 'code', 'building', 'floor', 'room_number',
            'capacity', 'area', 'laboratory_type', 'department',
            'admin', 'facilities', 'description', 'note'
        ]
    
    def validate_code(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError('实训室编号不能为空')
        return value.strip()
    
    def validate_name(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError('实训室名称不能为空')
        return value.strip()


class LaboratoryUpdateSerializer(serializers.ModelSerializer):
    """实训室更新序列化器"""

    admin = serializers.CharField(required=False, allow_null=True, allow_blank=True)

    class Meta:
        model = Laboratory
        fields = [
            'name', 'code', 'building', 'floor', 'room_number',
            'capacity', 'area', 'laboratory_type', 'admin',
            'status', 'facilities', 'description', 'note'
        ]
        extra_kwargs = {
            'note': {'required': False, 'allow_null': True, 'allow_blank': True},
        }

    def validate_code(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError('实训室编号不能为空')
        return value.strip()

    def validate_name(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError('实训室名称不能为空')
        return value.strip()

    def validate_admin(self, value):
        """
        验证管理员字段：
        - None、0、空字符串、'0'表示"未分配"
        - 其他值必须是有效的用户ID
        """
        if value is None or value == '' or str(value).strip() == '' or str(value) == '0':
            return None

        from apps.users.models import User
        try:
            user_id = int(value)
            user = User.objects.get(id=user_id, is_deleted=False)
            return user.id
        except (User.DoesNotExist, ValueError, TypeError) as e:
            raise serializers.ValidationError(f'管理员用户(ID={value})不存在或无效')


class BatchDeleteSerializer(serializers.Serializer):
    """批量删除序列化器"""
    
    ids = serializers.ListField(
        child=serializers.IntegerField(min_value=1),
        allow_empty=False,
        help_text='要删除的ID列表'
    )


class EquipmentSerializer(serializers.ModelSerializer):
    """设备序列化器"""
    
    laboratory_name = serializers.CharField(source='laboratory.name', read_only=True)
    
    class Meta:
        model = Equipment
        fields = [
            'id', 'name', 'code', 'category', 'brand', 'model', 'serial_number',
            'laboratory', 'laboratory_name', 'position', 'cpu', 'memory', 'disk',
            'gpu', 'os', 'purchase_date', 'warranty_expire', 'price', 'supplier',
            'status', 'last_maintenance_date', 'total_usage_hours',
            'description', 'note', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class EquipmentCreateSerializer(serializers.ModelSerializer):
    """设备创建序列化器"""
    
    class Meta:
        model = Equipment
        fields = [
            'name', 'code', 'category', 'brand', 'model', 'serial_number',
            'laboratory', 'position', 'cpu', 'memory', 'disk', 'gpu', 'os',
            'purchase_date', 'warranty_expire', 'price', 'supplier',
            'status', 'description', 'note'
        ]
