"""
部门视图
"""

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from drf_spectacular.utils import extend_schema
from common.responses import ApiResponse
from common.paginations import StandardPagination
from apps.users.models import Department
from apps.users.serializers import DepartmentSerializer, BatchDeleteSerializer
from apps.users.services import DepartmentService


class DepartmentViewSet(viewsets.ModelViewSet):
    """部门视图集"""
    
    permission_classes = [IsAuthenticated]
    pagination_class = StandardPagination
    serializer_class = DepartmentSerializer
    
    def get_queryset(self):
        return Department.objects.all()
    
    @extend_schema(description='获取部门列表')
    def list(self, request):
        service = DepartmentService()
        result = service.get_department_list(
            requester=request.user,
            search=request.query_params.get('search'),
            page=int(request.query_params.get('page', 1)),
            page_size=int(request.query_params.get('page_size', 10)),
            no_page=request.query_params.get('nopage') == 'true'
        )
        return ApiResponse.success(data=result)
    
    @extend_schema(description='获取部门详情')
    def retrieve(self, request, pk=None):
        service = DepartmentService()
        result = service.get_department_detail(requester=request.user, department_id=pk)
        return ApiResponse.success(data=result)
    
    @extend_schema(description='创建部门')
    def create(self, request):
        serializer = DepartmentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        service = DepartmentService()
        department = service.create_department(
            requester=request.user,
            data=serializer.validated_data
        )
        
        return ApiResponse.created(
            data={'id': department.id, 'name': department.name},
            message='部门创建成功'
        )
    
    @extend_schema(description='更新部门')
    def update(self, request, pk=None):
        serializer = DepartmentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        service = DepartmentService()
        department = service.update_department(
            requester=request.user,
            department_id=pk,
            data=serializer.validated_data
        )
        
        return ApiResponse.success(
            data={'id': department.id},
            message='部门更新成功'
        )
    
    @extend_schema(description='删除部门')
    def destroy(self, request, pk=None):
        service = DepartmentService()
        service.delete_department(requester=request.user, department_id=pk)
        return ApiResponse.success(message='部门删除成功')
    
    @extend_schema(
        request=BatchDeleteSerializer,
        description='批量删除部门'
    )
    @action(methods=['post'], detail=False)
    def batch_delete(self, request):
        serializer = BatchDeleteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        service = DepartmentService()
        result = service.batch_delete_departments(
            requester=request.user,
            department_ids=serializer.validated_data['ids']
        )
        
        message = f"成功删除 {result['deleted_count']} 个部门"
        if result['failed_count'] > 0:
            message += f"，{result['failed_count']} 个删除失败"
        
        return ApiResponse.success(data=result, message=message)
    
    @extend_schema(description='获取部门选项列表')
    @action(methods=['get'], detail=False)
    def options(self, request):
        service = DepartmentService()
        options = service.get_department_options()
        return ApiResponse.success(data={'departments': options})
