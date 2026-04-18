"""
缓存配置序列化器
"""

from rest_framework import serializers
from apps.cache_config.models import CacheConfig, ApiStats, CacheOperationLog


class CacheConfigSerializer(serializers.ModelSerializer):
    """缓存配置序列化器"""
    
    updated_by_name = serializers.CharField(source='updated_by.name', read_only=True)
    
    class Meta:
        model = CacheConfig
        fields = [
            'id', 'api_path', 'frontend_ttl', 'backend_ttl',
            'enabled', 'description', 'updated_by', 'updated_by_name',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'updated_by']


class CacheConfigCreateSerializer(serializers.ModelSerializer):
    """缓存配置创建序列化器"""
    
    class Meta:
        model = CacheConfig
        fields = [
            'api_path', 'frontend_ttl', 'backend_ttl',
            'enabled', 'description'
        ]


class CacheConfigUpdateSerializer(serializers.ModelSerializer):
    """缓存配置更新序列化器"""
    
    class Meta:
        model = CacheConfig
        fields = [
            'frontend_ttl', 'backend_ttl', 'enabled', 'description'
        ]


class ApiStatsSerializer(serializers.ModelSerializer):
    """API统计序列化器"""
    
    avg_response_time = serializers.FloatField(read_only=True)
    cache_hit_rate = serializers.FloatField(read_only=True)
    
    class Meta:
        model = ApiStats
        fields = [
            'id', 'api_path', 'date', 'request_count',
            'cache_hit_count', 'total_response_time', 'error_count',
            'avg_response_time', 'cache_hit_rate', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ApiStatsSummarySerializer(serializers.Serializer):
    """API统计汇总序列化器"""
    
    api_path = serializers.CharField()
    total_requests = serializers.IntegerField()
    total_cache_hits = serializers.IntegerField()
    avg_response_time = serializers.FloatField()
    cache_hit_rate = serializers.FloatField()
    error_rate = serializers.FloatField()


class CacheOperationLogSerializer(serializers.ModelSerializer):
    """缓存操作日志序列化器"""
    
    operator_name = serializers.CharField(source='operator.name', read_only=True)
    operation_type_display = serializers.CharField(source='get_operation_type_display', read_only=True)
    
    class Meta:
        model = CacheOperationLog
        fields = [
            'id', 'operator', 'operator_name', 'operation_type',
            'operation_type_display', 'api_path', 'old_value', 'new_value',
            'reason', 'ip_address', 'user_agent', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class CacheClearSerializer(serializers.Serializer):
    """缓存清除序列化器"""
    
    api_path = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text='API路径，为空则清除所有缓存'
    )
    reason = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text='操作原因'
    )


class CacheConfigBatchUpdateSerializer(serializers.Serializer):
    """缓存配置批量更新序列化器"""
    
    configs = serializers.ListField(
        child=serializers.DictField(),
        help_text='配置列表'
    )
    reason = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text='操作原因'
    )
