"""
自定义过滤器
"""

import django_filters
from django.db import models


class BaseFilterSet(django_filters.FilterSet):
    """基础过滤器集"""

    search = django_filters.CharFilter(method='filter_search', label='搜索')
    created_at_start = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_at_end = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')
    updated_at_start = django_filters.DateTimeFilter(field_name='updated_at', lookup_expr='gte')
    updated_at_end = django_filters.DateTimeFilter(field_name='updated_at', lookup_expr='lte')

    def filter_search(self, queryset, name, value):
        """通用搜索方法"""
        search_fields = getattr(self.Meta, 'search_fields', [])
        if not search_fields:
            return queryset

        queries = models.Q()
        for field in search_fields:
            queries |= models.Q(**{f'{field}__icontains': value})
        return queryset.filter(queries)
