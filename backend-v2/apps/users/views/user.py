"""
用户视图
"""

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from drf_spectacular.utils import extend_schema
from common.responses import ApiResponse
from common.paginations import StandardPagination
from apps.users.models import User
from apps.users.serializers import (
    UserSerializer, UserCreateSerializer, UserUpdateSerializer,
    UserProfileSerializer, BatchDeleteSerializer
)
from apps.users.services import UserService


class UserViewSet(viewsets.ModelViewSet):
    """用户视图集"""
    
    permission_classes = [IsAuthenticated]
    pagination_class = StandardPagination
    serializer_class = UserSerializer
    
    def get_queryset(self):
        return User.objects.filter(is_deleted=False)
    
    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return UserUpdateSerializer
        return UserSerializer
    
    @extend_schema(description='获取用户列表')
    def list(self, request):
        service = UserService()
        result = service.get_user_list(
            requester=request.user,
            department_id=request.query_params.get('department_id'),
            role=request.query_params.get('role'),
            status=request.query_params.get('status'),
            search=request.query_params.get('search'),
            page=int(request.query_params.get('page', 1)),
            page_size=int(request.query_params.get('page_size', 20)),
            no_page=request.query_params.get('nopage') == 'true'
        )
        return ApiResponse.success(data=result)
    
    @extend_schema(description='获取用户详情')
    def retrieve(self, request, pk=None):
        service = UserService()
        try:
            user = User.objects.get(id=pk, is_deleted=False)
            return ApiResponse.success(data=service._format_user(user))
        except User.DoesNotExist:
            return ApiResponse.error(message='用户不存在', code=404)
    
    @extend_schema(description='创建用户')
    def create(self, request):
        serializer = UserCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        service = UserService()
        user = service.create_user(
            requester=request.user,
            data=serializer.validated_data,
            request=request
        )

        return ApiResponse.created(
            data={'id': user.id, 'username': user.username},
            message='用户创建成功'
        )
    
    @extend_schema(description='更新用户')
    def update(self, request, pk=None):
        serializer = UserUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        service = UserService()
        user = service.update_user(
            requester=request.user,
            user_id=pk,
            data=serializer.validated_data,
            request=request
        )

        return ApiResponse.success(
            data={'id': user.id},
            message='用户更新成功'
        )
    
    @extend_schema(description='删除用户')
    def destroy(self, request, pk=None):
        service = UserService()
        service.delete_user(requester=request.user, user_id=pk, request=request)
        return ApiResponse.success(message='用户删除成功')
    
    @extend_schema(
        request=BatchDeleteSerializer,
        description='批量删除用户'
    )
    @action(methods=['post'], detail=False)
    def batch_delete(self, request):
        serializer = BatchDeleteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        service = UserService()
        result = service.batch_delete_users(
            requester=request.user,
            user_ids=serializer.validated_data['ids'],
            request=request
        )
        
        message = f"成功删除 {result['deleted_count']} 个用户"
        if result['failed_count'] > 0:
            message += f"，{result['failed_count']} 个删除失败"
        
        return ApiResponse.success(data=result, message=message)
    
    @extend_schema(description='激活/停用用户')
    @action(methods=['post'], detail=True)
    def activate(self, request, pk=None):
        is_active = request.data.get('is_active', True)

        service = UserService()
        user = service.activate_user(
            requester=request.user,
            user_id=pk,
            is_active=is_active,
            request=request
        )

        status_text = '激活' if is_active else '停用'
        return ApiResponse.success(
            data={'id': user.id, 'is_active': user.is_active},
            message=f'用户已{status_text}'
        )
    
    @extend_schema(description='更新用户角色')
    @action(methods=['post'], detail=True)
    def update_role(self, request, pk=None):
        role = request.data.get('role')
        if role is None:
            return ApiResponse.error(message='角色不能为空')
        
        department_id = request.data.get('department_id')
        
        if role & 4:
            if not department_id:
                return ApiResponse.error(message='分院管理员必须指定所属部门')
        
        service = UserService()
        user = service.update_user_role(
            requester=request.user,
            user_id=pk,
            role=role,
            department_id=department_id,
            request=request
        )
        
        return ApiResponse.success(
            data={'id': user.id, 'role': user.role, 'department_id': user.department_id},
            message='角色更新成功'
        )
    
    @extend_schema(description='分配权限')
    @action(methods=['post'], detail=True)
    def assign_permission(self, request, pk=None):
        permissions = request.data.get('permissions', [])
        
        service = UserService()
        user = service.assign_permission(
            requester=request.user,
            user_id=pk,
            permissions=permissions
        )
        
        return ApiResponse.success(
            data={'id': user.id},
            message='权限分配成功'
        )
    
    @extend_schema(description='清理用户数据')
    @action(methods=['post'], detail=True)
    def cleanup_data(self, request, pk=None):
        service = UserService()
        result = service.cleanup_user_data(
            requester=request.user,
            user_id=pk
        )
        
        return ApiResponse.success(data=result, message=result['message'])
    
    @extend_schema(description='导入用户')
    @action(methods=['post'], detail=False)
    def import_users(self, request):
        file_obj = request.FILES.get('file')
        if not file_obj:
            return ApiResponse.error(message='请上传文件')
        
        service = UserService()
        result = service.import_users(
            requester=request.user,
            file_data=file_obj
        )
        
        message = f"成功导入 {result['success_count']} 个用户"
        if result['failed_count'] > 0:
            message += f"，{result['failed_count']} 条失败"
        
        return ApiResponse.success(data=result, message=message)
    
    @extend_schema(description='获取用户选项列表')
    @action(methods=['get'], detail=False)
    def options(self, request):
        service = UserService()
        options = service.get_user_options(requester=request.user)
        return ApiResponse.success(data={'users': options})


class ProfileView(viewsets.ViewSet):
    """个人信息视图"""
    
    permission_classes = [IsAuthenticated]
    
    @extend_schema(description='获取个人信息')
    def list(self, request):
        serializer = UserProfileSerializer(request.user)
        return ApiResponse.success(data=serializer.data)
    
    @extend_schema(description='更新个人信息')
    def update(self, request):
        serializer = UserProfileSerializer(
            request.user,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return ApiResponse.success(data=serializer.data, message='更新成功')
