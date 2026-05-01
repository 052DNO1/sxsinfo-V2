"""
操作日志服务层
提供便捷的日志记录方法
"""

from django.db import transaction
from django.utils import timezone
from datetime import timedelta
from apps.core.models import SystemOperationLog
from apps.core.utils import beijing_strftime, beijing_now, beijing_today


class OperationLogService:
    """操作日志服务"""

    @staticmethod
    def log(request, module: str, operation_type: str,
            target_type: str = '', target_id: int = None,
            target_name: str = '', description: str = '',
            detail: dict = None):
        """
        记录操作日志（通用方法）

        Args:
            request: Django request 对象
            module: 模块标识 (user, equipment, schedule, etc.)
            operation_type: 操作类型 (user_create, equipment_delete, etc.)
            target_type: 目标对象类型 (User, Equipment, Schedule)
            target_id: 目标对象 ID
            target_name: 目标对象可读名称
            description: 操作描述（自然语言）
            detail: 详细信息（JSON格式）

        Returns:
            SystemOperationLog: 创建的日志对象
        """
        return SystemOperationLog.create_log(
            request=request,
            module=module,
            operation_type=operation_type,
            target_type=target_type,
            target_id=target_id,
            target_name=target_name,
            description=description,
            detail=detail
        )

    @staticmethod
    def log_user_operation(request, operation_type: str, user, description: str = '',
                          old_data: dict = None, new_data: dict = None):
        """
        记录用户管理操作

        Args:
            request: Django request 对象
            operation_type: 操作类型 (user_create, user_delete, user_update, user_role_update)
            user: 用户对象
            description: 操作描述
            old_data: 修改前的数据
            new_data: 修改后的数据
        """
        if not description:
            username = user.nickname or user.username if user else '未知用户'
            type_map = {
                'user_create': f'添加了用户 {username}',
                'user_delete': f'删除了用户 {username}',
                'user_update': f'更新了用户 {username} 的信息',
                'user_role_update': f'更新了用户 {username} 的权限',
                'user_activate': f'{"启用" if user and user.is_active else "禁用"}了用户 {username}',
                'user_batch_delete': f'批量删除了用户',
                'user_import': f'导入了用户',
            }
            description = type_map.get(operation_type, f'对用户 {username} 执行了操作')

        detail = None
        if old_data or new_data:
            detail = {
                'old_value': old_data,
                'new_value': new_data,
            }

        return OperationLogService.log(
            request=request,
            module='user',
            operation_type=operation_type,
            target_type='User',
            target_id=user.id if user else None,
            target_name=user.nickname or user.username if user else '',
            description=description,
            detail=detail
        )

    @staticmethod
    def log_equipment_operation(request, operation_type: str, equipment, description: str = '',
                               old_data: dict = None, new_data: dict = None):
        """
        记录设备管理操作

        Args:
            request: Django request 对象
            operation_type: 操作类型 (equipment_create, equipment_delete, equipment_update)
            equipment: 设备对象
            description: 操作描述
            old_data: 修改前的数据
            new_data: 修改后的数据
        """
        if not description:
            name = equipment.name if equipment else '未知设备'
            code = equipment.code if equipment else ''
            type_map = {
                'equipment_create': f'添加了设备 {name}({code})',
                'equipment_delete': f'删除了设备 {name}({code})',
                'equipment_update': f'更新了设备 {name}({code}) 的信息',
                'equipment_batch_delete': f'批量删除了设备',
            }
            description = type_map.get(operation_type, f'对设备 {name} 执行了操作')

        detail = None
        if old_data or new_data:
            detail = {
                'old_value': old_data,
                'new_value': new_data,
            }

        return OperationLogService.log(
            request=request,
            module='equipment',
            operation_type=operation_type,
            target_type='Equipment',
            target_id=equipment.id if equipment else None,
            target_name=f'{equipment.name}({equipment.code})' if equipment else '',
            description=description,
            detail=detail
        )

    @staticmethod
    def log_schedule_operation(request, operation_type: str, schedule, description: str = '',
                              old_data: dict = None, new_data: dict = None):
        """
        记录课表管理操作

        Args:
            request: Django request 对象
            operation_type: 操作类型 (schedule_create, schedule_delete, schedule_update)
            schedule: 课表对象
            description: 操作描述
            old_data: 修改前的数据
            new_data: 修改后的数据
        """
        if not description:
            course_name = schedule.course_name if schedule else '未知课程'
            lab_name = schedule.laboratory.name if schedule and schedule.laboratory else ''
            type_map = {
                'schedule_create': f'添加了课表《{course_name}》({lab_name})',
                'schedule_delete': f'删除了课表《{course_name}》({lab_name})',
                'schedule_update': f'更新了课表《{course_name}》的信息',
            }
            description = type_map.get(operation_type, f'对课表《{course_name}》执行了操作')

        detail = None
        if old_data or new_data:
            detail = {
                'old_value': old_data,
                'new_value': new_data,
            }

        return OperationLogService.log(
            request=request,
            module='schedule',
            operation_type=operation_type,
            target_type='Schedule',
            target_id=schedule.id if schedule else None,
            target_name=f'{schedule.course_name}' if schedule else '',
            description=description,
            detail=detail
        )

    @staticmethod
    def log_cache_config_operation(request, operation_type: str, config, description: str = '',
                                  old_data: dict = None, new_data: dict = None):
        """
        记录缓存配置操作

        Args:
            request: Django request 对象
            operation_type: 操作类型
            config: 缓存配置对象
            description: 操作描述
            old_data: 修改前的数据
            new_data: 修改后的数据
        """
        if not description:
            api_path = config.api_path if config else ''
            type_map = {
                'cache_config_create': f'创建了缓存配置 {api_path}',
                'cache_config_delete': f'删除了缓存配置 {api_path}',
                'cache_config_update': f'更新了缓存配置 {api_path}',
                'cache_clear': f'清除了缓存 {api_path}',
            }
            description = type_map.get(operation_type, f'对缓存配置 {api_path} 执行了操作')

        detail = None
        if old_data or new_data:
            detail = {
                'old_value': old_data,
                'new_value': new_data,
            }

        return OperationLogService.log(
            request=request,
            module='cache_config',
            operation_type=operation_type,
            target_type='CacheConfig',
            target_id=config.id if config else None,
            target_name=config.api_path if config else '',
            description=description,
            detail=detail
        )

    @staticmethod
    def log_department_operation(request, operation_type: str, department, description: str = '',
                                  old_data: dict = None, new_data: dict = None):
        """
        记录部门管理操作

        Args:
            request: Django request 对象
            operation_type: 操作类型 (department_create, department_delete, department_update)
            department: 部门对象
            description: 操作描述
            old_data: 修改前的数据
            new_data: 修改后的数据
        """
        if not description:
            name = department.name if department else '未知部门'
            type_map = {
                'department_create': f'创建了部门 {name}',
                'department_delete': f'删除了部门 {name}',
                'department_update': f'更新了部门 {name} 的信息',
            }
            description = type_map.get(operation_type, f'对部门 {name} 执行了操作')

        detail = None
        if old_data or new_data:
            detail = {
                'old_value': old_data,
                'new_value': new_data,
            }

        return OperationLogService.log(
            request=request,
            module='department',
            operation_type=operation_type,
            target_type='Department',
            target_id=department.id if department else None,
            target_name=department.name if department else '',
            description=description,
            detail=detail
        )

    @staticmethod
    def log_laboratory_operation(request, operation_type: str, laboratory, description: str = '',
                                  old_data: dict = None, new_data: dict = None):
        """
        记录实训室管理操作

        Args:
            request: Django request 对象
            operation_type: 操作类型 (laboratory_create, laboratory_delete, laboratory_update)
            laboratory: 实训室对象
            description: 操作描述
            old_data: 修改前的数据
            new_data: 修改后的数据
        """
        if not description:
            name = laboratory.name if laboratory else '未知实训室'
            code = laboratory.code if laboratory else ''
            type_map = {
                'laboratory_create': f'创建了实训室 {name}({code})',
                'laboratory_delete': f'删除了实训室 {name}({code})',
                'laboratory_update': f'更新了实训室 {name}({code}) 的信息',
            }
            description = type_map.get(operation_type, f'对实训室 {name} 执行了操作')

        detail = None
        if old_data or new_data:
            detail = {
                'old_value': old_data,
                'new_value': new_data,
            }

        return OperationLogService.log(
            request=request,
            module='laboratory',
            operation_type=operation_type,
            target_type='Laboratory',
            target_id=laboratory.id if laboratory else None,
            target_name=f'{laboratory.name}({laboratory.code})' if laboratory else '',
            description=description,
            detail=detail
        )

    @staticmethod
    def log_backup_operation(request, operation_type: str, description: str = '',
                             detail: dict = None):
        """
        记录备份管理操作

        Args:
            request: Django request 对象
            operation_type: 操作类型 (backup_create, backup_delete, backup_restore)
            description: 操作描述
            detail: 详细信息
        """
        if not description:
            type_map = {
                'backup_create': '创建了系统备份',
                'backup_delete': '删除了系统备份',
                'backup_restore': '恢复了系统备份',
            }
            description = type_map.get(operation_type, '执行了备份操作')

        return OperationLogService.log(
            request=request,
            module='backup',
            operation_type=operation_type,
            target_type='Backup',
            target_id=None,
            target_name='系统备份',
            description=description,
            detail=detail
        )

    @staticmethod
    def get_logs(filters: dict = None, page: int = 1, page_size: int = 20) -> dict:
        """
        获取操作日志列表

        Args:
            filters: 筛选条件
            page: 页码
            page_size: 每页数量

        Returns:
            dict: 包含列表和分页信息
        """
        from django.core.paginator import Paginator

        queryset = SystemOperationLog.objects.all()

        if filters:
            module = filters.get('module')
            if module:
                queryset = queryset.filter(module=module)

            operation_type = filters.get('operation_type')
            if operation_type:
                queryset = queryset.filter(operation_type=operation_type)

            operator_id = filters.get('operator_id')
            if operator_id:
                queryset = queryset.filter(operator_id=operator_id)

            target_type = filters.get('target_type')
            if target_type:
                queryset = queryset.filter(target_type=target_type)

            start_date = filters.get('start_date')
            if start_date:
                queryset = queryset.filter(created_at__gte=start_date)

            end_date = filters.get('end_date')
            if end_date:
                queryset = queryset.filter(created_at__lte=end_date)

            search = filters.get('search')
            if search:
                queryset = queryset.filter(
                    models.Q(description__icontains=search) |
                    models.Q(target_name__icontains=search) |
                    models.Q(operator_username__icontains=search)
                )

        queryset = queryset.select_related('operator').order_by('-created_at')

        paginator = Paginator(queryset, page_size)
        page_obj = paginator.page(page)

        from apps.core.serializers.operation_log import SystemOperationLogSerializer
        serializer = SystemOperationLogSerializer(page_obj.object_list, many=True)

        return {
            'list': serializer.data,
            'pagination': {
                'total': paginator.count,
                'page': page,
                'page_size': page_size,
                'total_pages': paginator.num_pages,
            }
        }

    @staticmethod
    def get_stats() -> dict:
        """
        获取操作日志统计信息

        Returns:
            dict: 统计信息
        """
        from django.db.models import Count
        from datetime import date

        today = beijing_today()
        week_ago = today - timedelta(days=7)

        total_count = SystemOperationLog.objects.count()
        today_count = SystemOperationLog.objects.filter(
            created_at__date=today
        ).count()
        week_count = SystemOperationLog.objects.filter(
            created_at__date__gte=week_ago
        ).count()

        # 按模块统计
        module_stats = list(
            SystemOperationLog.objects.values('module').annotate(
                count=Count('id')
            ).order_by('-count')[:10]
        )

        # 最近操作
        recent_logs = SystemOperationLog.objects.select_related('operator')[:10]

        from apps.core.serializers.operation_log import (
            SystemOperationLogListSerializer,
            OperationLogStatsSerializer
        )
        
        log_serializer = SystemOperationLogListSerializer(recent_logs, many=True)

        return {
            'total_count': total_count,
            'today_count': today_count,
            'week_count': week_count,
            'module_stats': module_stats,
            'recent_operations': log_serializer.data,
        }
