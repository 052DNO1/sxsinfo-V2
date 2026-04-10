"""
Mixin类
"""

from rest_framework import status
from common.responses import ApiResponse


class CreateModelMixin:
    """创建模型Mixin"""
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return ApiResponse.created(data=serializer.data, message='创建成功')

    def perform_create(self, serializer):
        serializer.save()


class UpdateModelMixin:
    """更新模型Mixin"""
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return ApiResponse.success(data=serializer.data, message='更新成功')

    def perform_update(self, serializer):
        serializer.save()


class DestroyModelMixin:
    """删除模型Mixin"""
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return ApiResponse.success(message='删除成功')

    def perform_destroy(self, instance):
        instance.delete()


class ListModelMixin:
    """列表模型Mixin"""
    
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return ApiResponse.success(data=serializer.data)


class RetrieveModelMixin:
    """详情模型Mixin"""
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return ApiResponse.success(data=serializer.data)
