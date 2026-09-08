"""
学期视图
"""

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from drf_spectacular.utils import extend_schema
from common.responses import ApiResponse
from common.paginations import StandardPagination
from apps.schedules.models import Semester
from apps.schedules.serializers import SemesterSerializer, SemesterCreateSerializer, BatchDeleteSerializer
from apps.schedules.services import SemesterService


class SemesterViewSet(viewsets.ModelViewSet):
    """学期视图集"""
    
    permission_classes = [IsAuthenticated]
    pagination_class = StandardPagination
    serializer_class = SemesterSerializer
    
    def get_queryset(self):
        return Semester.objects.filter(is_deleted=False)
    
    def get_serializer_class(self):
        if self.action == 'create':
            return SemesterCreateSerializer
        return SemesterSerializer
    
    @extend_schema(description='获取学期列表')
    def list(self, request):
        service = SemesterService()
        result = service.get_semester_list(
            requester=request.user,
            page=int(request.query_params.get('page', 1)),
            page_size=int(request.query_params.get('page_size', 20)),
            no_page=request.query_params.get('nopage') == 'true'
        )
        return ApiResponse.success(data=result)
    
    @extend_schema(description='获取学期详情')
    def retrieve(self, request, pk=None):
        service = SemesterService()
        result = service.get_semester_detail(requester=request.user, semester_id=pk)
        return ApiResponse.success(data=result)
    
    @extend_schema(description='创建学期')
    def create(self, request):
        serializer = SemesterCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        service = SemesterService()
        semester = service.create_semester(
            requester=request.user,
            data=serializer.validated_data
        )
        
        return ApiResponse.created(
            data={'id': semester.id, 'code': semester.code},
            message='学期创建成功'
        )
    
    @extend_schema(description='更新学期')
    def update(self, request, pk=None, *args, **kwargs):
        serializer = SemesterCreateSerializer(data=request.data, partial=kwargs.get('partial', False))
        serializer.is_valid(raise_exception=True)
        
        service = SemesterService()
        semester = service.update_semester(
            requester=request.user,
            semester_id=pk,
            data=serializer.validated_data
        )
        
        return ApiResponse.success(
            data={'id': semester.id},
            message='学期更新成功'
        )
    
    @extend_schema(description='删除学期')
    def destroy(self, request, pk=None):
        service = SemesterService()
        service.delete_semester(requester=request.user, semester_id=pk)
        return ApiResponse.success(message='学期删除成功')
    
    @extend_schema(
        request=BatchDeleteSerializer,
        description='批量删除学期'
    )
    @action(methods=['post'], detail=False)
    def batch_delete(self, request):
        serializer = BatchDeleteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        service = SemesterService()
        result = service.batch_delete_semesters(
            requester=request.user,
            semester_ids=serializer.validated_data['ids']
        )
        
        message = f"成功删除 {result['deleted_count']} 个学期"
        if result['failed_count'] > 0:
            message += f"，{result['failed_count']} 个删除失败"
        
        return ApiResponse.success(data=result, message=message)
    
    @extend_schema(description='设置当前学期')
    @action(methods=['post'], detail=True)
    def set_current(self, request, pk=None):
        service = SemesterService()
        semester = service.set_current_semester(
            requester=request.user,
            semester_id=pk
        )
        return ApiResponse.success(
            data={'id': semester.id, 'is_current': True},
            message=f'已将 {semester.name} 设为当前学期'
        )
    
    @extend_schema(description='取消当前学期')
    @action(methods=['post'], detail=True)
    def unset_current(self, request, pk=None):
        service = SemesterService()
        semester = service.unset_current_semester(
            requester=request.user,
            semester_id=pk
        )
        return ApiResponse.success(
            data={'id': semester.id, 'is_current': False},
            message='已取消当前学期'
        )
    
    @extend_schema(description='归档学期')
    @action(methods=['post'], detail=True)
    def archive(self, request, pk=None):
        service = SemesterService()
        semester = service.archive_semester(
            requester=request.user,
            semester_id=pk
        )
        return ApiResponse.success(
            data={'id': semester.id, 'is_archived': True},
            message=f'已归档学期 {semester.name}'
        )
    
    @extend_schema(description='获取当前学期')
    @action(methods=['get'], detail=False)
    def current(self, request):
        service = SemesterService()
        result = service.get_current_semester(requester=request.user)
        return ApiResponse.success(data=result)
    
    @extend_schema(description='获取学期选项列表')
    @action(methods=['get'], detail=False)
    def options(self, request):
        service = SemesterService()
        options = service.get_semester_options(requester=request.user)
        return ApiResponse.success(data={'options': options})
    
    @extend_schema(description='获取归档概览')
    @action(methods=['get'], detail=False)
    def archive_overview(self, request):
        department_id = request.query_params.get('department_id')
        service = SemesterService()
        result = service.get_archive_overview(
            requester=request.user,
            department_id=int(department_id) if department_id else None
        )
        return ApiResponse.success(data=result)
