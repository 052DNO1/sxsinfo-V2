"""
课表视图
"""

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from drf_spectacular.utils import extend_schema
from common.responses import ApiResponse
from common.paginations import StandardPagination
from apps.schedules.models import Schedule
from apps.schedules.serializers import (
    ScheduleSerializer, ScheduleCreateSerializer, ScheduleUpdateSerializer,
    ScheduleConflictCheckSerializer, BatchDeleteSerializer
)
from apps.schedules.services import ScheduleService
from apps.core.exceptions import ScheduleConflictError


class ScheduleViewSet(viewsets.ModelViewSet):
    """课表视图集"""
    
    permission_classes = [IsAuthenticated]
    pagination_class = StandardPagination
    serializer_class = ScheduleSerializer
    
    def get_queryset(self):
        return Schedule.objects.filter(is_deleted=False)
    
    def get_serializer_class(self):
        if self.action == 'create':
            return ScheduleCreateSerializer
        if self.action in ['update', 'partial_update']:
            return ScheduleUpdateSerializer
        return ScheduleSerializer
    
    @extend_schema(description='获取课表列表')
    def list(self, request):
        service = ScheduleService()
        result = service.get_schedule_list(
            requester=request.user,
            laboratory_id=request.query_params.get('laboratory_id'),
            teacher_id=request.query_params.get('teacher_id'),
            semester_id=request.query_params.get('semester_id'),
            weekday=request.query_params.get('weekday'),
            search=request.query_params.get('search'),
            page=int(request.query_params.get('page', 1)),
            page_size=int(request.query_params.get('page_size', 20)),
            no_page=request.query_params.get('nopage') == 'true'
        )
        return ApiResponse.success(data=result)
    
    @extend_schema(description='获取课表详情')
    def retrieve(self, request, pk=None):
        service = ScheduleService()
        result = service.get_schedule_detail(requester=request.user, schedule_id=pk)
        return ApiResponse.success(data={'form_data': result})
    
    @extend_schema(description='创建课表')
    def create(self, request):
        serializer = ScheduleCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        service = ScheduleService()
        try:
            schedule = service.create_schedule(
                requester=request.user,
                data=serializer.validated_data
            )
            return ApiResponse.created(
                data={'id': schedule.id},
                message='课表添加成功'
            )
        except ScheduleConflictError as e:
            return ApiResponse.error(
                message=str(e),
                data={'conflicts': e.data.get('conflicts', [])},
                code=400
            )
    
    @extend_schema(description='更新课表')
    def update(self, request, pk=None):
        serializer = ScheduleUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        service = ScheduleService()
        try:
            schedule = service.update_schedule(
                requester=request.user,
                schedule_id=pk,
                data=serializer.validated_data
            )
            return ApiResponse.success(
                data={'id': schedule.id},
                message='课表更新成功'
            )
        except ScheduleConflictError as e:
            return ApiResponse.error(
                message=str(e),
                data={'conflicts': e.data.get('conflicts', [])},
                code=400
            )
    
    @extend_schema(description='删除课表')
    def destroy(self, request, pk=None):
        service = ScheduleService()
        service.delete_schedule(requester=request.user, schedule_id=pk)
        return ApiResponse.success(message='课表删除成功')
    
    @extend_schema(
        request=BatchDeleteSerializer,
        description='批量删除课表'
    )
    @action(methods=['post'], detail=False)
    def batch_delete(self, request):
        serializer = BatchDeleteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        service = ScheduleService()
        result = service.batch_delete_schedules(
            requester=request.user,
            schedule_ids=serializer.validated_data['ids']
        )
        
        message = f"成功删除 {result['deleted_count']} 条课表记录"
        if result['failed_count'] > 0:
            message += f"，{result['failed_count']} 条删除失败"
        
        return ApiResponse.success(data=result, message=message)
    
    @extend_schema(
        request=ScheduleConflictCheckSerializer,
        description='检测课表冲突'
    )
    @action(methods=['post'], detail=False)
    def check_conflict(self, request):
        serializer = ScheduleConflictCheckSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        service = ScheduleService()
        result = service.check_conflict(
            laboratory_id=serializer.validated_data['laboratory_id'],
            weekday=serializer.validated_data['weekday'],
            time_slot=serializer.validated_data['time_slot'],
            weeks=serializer.validated_data['weeks'],
            exclude_id=serializer.validated_data.get('exclude_id')
        )
        
        return ApiResponse.success(data=result)
    
    @extend_schema(description='获取表单选项')
    @action(methods=['get'], detail=False)
    def form_options(self, request):
        service = ScheduleService()
        result = service.get_form_options(
            requester=request.user,
            laboratory_id=request.query_params.get('laboratory_id')
        )
        return ApiResponse.success(data=result)
    
    @extend_schema(description='获取实训室选项列表')
    @action(methods=['get'], detail=False)
    def laboratory_options(self, request):
        service = ScheduleService()
        options = service.get_laboratory_options(requester=request.user)
        return ApiResponse.success(data={'options': options})
