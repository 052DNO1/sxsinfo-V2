"""
用户服务
"""

import io
from django.db import models, transaction
from django.core.paginator import Paginator
from openpyxl import load_workbook
from apps.core.exceptions import ValidationError, NotFoundError, PermissionDenied
from apps.core.constants import UserRole
from apps.users.models import User, Department
from common.decorators import cached_method
from common.services.cache_service import CacheInvalidator


class UserService:
    """用户服务"""

    @cached_method(timeout=60, key_prefix='user:list')
    def get_user_list(
        self,
        requester,
        department_id: int = None,
        role: int = None,
        status: str = None,
        search: str = None,
        page: int = 1,
        page_size: int = 20,
        no_page: bool = False
    ) -> dict:
        queryset = User.objects.select_related('department').filter(is_deleted=False)
        
        if requester.is_department_admin and not requester.is_super_admin:
            queryset = queryset.filter(department_id=requester.department_id)
        
        if department_id:
            queryset = queryset.filter(department_id=department_id)
        if role is not None:
            from django.db.models import IntegerField, Q
            
            if isinstance(role, str) and ',' in role:
                role_list = [int(r.strip()) for r in role.split(',') if r.strip().isdigit()]
                if role_list:
                    where_conditions = ' OR '.join([f'(role & {r} > 0)' for r in role_list])
                    queryset = queryset.extra(where=[where_conditions])
            else:
                try:
                    role_int = int(role)
                    queryset = queryset.annotate(
                        role_bitand=models.ExpressionWrapper(
                            models.F('role').bitand(role_int),
                            output_field=IntegerField()
                        )
                    ).filter(role_bitand__gt=0)
                except (ValueError, TypeError):
                    pass
        if status:
            queryset = queryset.filter(status=status)
        if search:
            queryset = queryset.filter(
                models.Q(username__icontains=search) |
                models.Q(nickname__icontains=search) |
                models.Q(phone__icontains=search)
            )
        
        queryset = queryset.order_by('-created_at')
        
        if no_page:
            return {
                'list': [self._format_user(u) for u in queryset],
                'pagination': {
                    'total': queryset.count(),
                }
            }
        
        paginator = Paginator(queryset, page_size)
        page_obj = paginator.get_page(page)
        
        return {
            'list': [self._format_user(u) for u in page_obj],
            'pagination': {
                'total': paginator.count,
                'page': page,
                'page_size': page_size,
                'total_pages': paginator.num_pages,
            }
        }

    @transaction.atomic
    def create_user(self, requester, data: dict):
        if not requester.is_department_admin and not requester.is_super_admin:
            raise PermissionDenied('无权限创建用户')
        
        username = data.get('username', '').strip()
        if not username:
            raise ValidationError('用户名不能为空')
        
        if User.objects.filter(username=username).exists():
            raise ValidationError(f'用户名 "{username}" 已存在')
        
        department = data.get('department')
        if department:
            if not requester.is_super_admin:
                if department.id != requester.department_id:
                    raise PermissionDenied('无权限在该部门创建用户')
        
        default_password = username[:6]
        
        default_role = UserRole.TEACHER
        if requester.is_super_admin and 'role' not in data:
            default_role = UserRole.DEPARTMENT_ADMIN
        
        user = User.objects.create_user(
            username=username,
            nickname=data.get('nickname', username),
            phone=data.get('phone', ''),
            email=data.get('email', ''),
            role=data.get('role', default_role),
            department=department,
            is_active=True,
            password=data.get('password', default_password)
        )

        CacheInvalidator.invalidate_user_cache(requester.id)

        return user

    @transaction.atomic
    def update_user(self, requester, user_id: int, data: dict):
        try:
            user = User.objects.get(id=user_id, is_deleted=False)
        except User.DoesNotExist:
            raise NotFoundError('用户不存在')
        
        if not self._can_manage_user(requester, user):
            raise PermissionDenied('无权限修改该用户')
        
        allowed_fields = ['nickname', 'phone', 'email', 'status']
        if requester.is_super_admin or requester.is_department_admin:
            allowed_fields.extend(['role', 'department_id'])
        
        for field in allowed_fields:
            if field in data:
                setattr(user, field, data[field])
        
        user.save()

        CacheInvalidator.invalidate_user_cache(user_id)

        return user

    @transaction.atomic
    def delete_user(self, requester, user_id: int) -> bool:
        try:
            user = User.objects.get(id=user_id, is_deleted=False)
        except User.DoesNotExist:
            raise NotFoundError('用户不存在')
        
        if user.id == requester.id:
            raise ValidationError('不能删除自己')
        
        if not self._can_manage_user(requester, user):
            raise PermissionDenied('无权限删除该用户')
        
        user.delete()

        CacheInvalidator.invalidate_user_cache(user_id)

        return True

    @transaction.atomic
    def batch_delete_users(self, requester, user_ids: list) -> dict:
        deleted_count = 0
        failed_list = []
        
        for user_id in user_ids:
            try:
                self.delete_user(requester, user_id)
                deleted_count += 1
            except Exception as e:
                failed_list.append({'id': user_id, 'reason': str(e)})

        if deleted_count > 0:
            CacheInvalidator.invalidate_user_cache(requester.id)
        
        return {
            'deleted_count': deleted_count,
            'failed_count': len(failed_list),
            'failed_list': failed_list,
        }

    @transaction.atomic
    def activate_user(self, requester, user_id: int, is_active: bool) -> User:
        try:
            user = User.objects.get(id=user_id, is_deleted=False)
        except User.DoesNotExist:
            raise NotFoundError('用户不存在')
        
        if not self._can_manage_user(requester, user):
            raise PermissionDenied('无权限操作该用户')
        
        user.is_active = is_active
        user.save(update_fields=['is_active'])

        CacheInvalidator.invalidate_user_cache(user_id)

        return user

    @transaction.atomic
    def update_user_role(self, requester, user_id: int, role: int) -> User:
        if not requester.is_super_admin and not requester.is_department_admin:
            raise PermissionDenied('无权限修改用户角色')
        
        try:
            user = User.objects.get(id=user_id, is_deleted=False)
        except User.DoesNotExist:
            raise NotFoundError('用户不存在')
        
        if not self._can_manage_user(requester, user):
            raise PermissionDenied('无权限修改该用户角色')
        
        user.role = role
        user.save(update_fields=['role'])

        CacheInvalidator.invalidate_user_cache(user_id)

        return user

    @transaction.atomic
    def assign_permission(self, requester, user_id: int, permissions: list) -> User:
        if not requester.is_super_admin:
            raise PermissionDenied('只有超级管理员可以分配权限')
        
        try:
            user = User.objects.get(id=user_id, is_deleted=False)
        except User.DoesNotExist:
            raise NotFoundError('用户不存在')
        
        user.custom_permissions = permissions
        user.save(update_fields=['custom_permissions'])

        CacheInvalidator.invalidate_user_cache(user_id)

        return user

    @transaction.atomic
    def cleanup_user_data(self, requester, user_id: int) -> dict:
        if not requester.is_super_admin:
            raise PermissionDenied('只有超级管理员可以清理用户数据')
        
        try:
            user = User.objects.get(id=user_id, is_deleted=False)
        except User.DoesNotExist:
            raise NotFoundError('用户不存在')
        
        from apps.schedules.models import Schedule
        from apps.records.models import UsageRecord
        from apps.maintenance.models import WorkOrder
        
        cleaned = {
            'schedules': Schedule.objects.filter(teacher=user).delete()[0],
            'records': UsageRecord.objects.filter(teacher=user).delete()[0],
            'work_orders_reporter': WorkOrder.objects.filter(reporter=user).delete()[0],
            'work_orders_handler': WorkOrder.objects.filter(handler=user).update(handler=None),
        }

        CacheInvalidator.invalidate_user_cache(user_id)

        return cleaned

    def _can_manage_user(self, requester, target_user) -> bool:
        if requester.is_super_admin:
            return True
        if requester.is_department_admin:
            return target_user.department_id == requester.department_id
        return False

    def _format_user(self, user) -> dict:
        return {
            'id': user.id,
            'username': user.username,
            'nickname': user.nickname or user.username,
            'email': user.email or '',
            'phone': user.phone or '',
            'role': user.role,
            'department_id': user.department_id,
            'department_name': user.department.name if user.department else '',
            'is_active': user.is_active,
            'status': 'active' if user.is_active else 'inactive',
            'created_at': user.created_at.strftime('%Y-%m-%d %H:%M:%S') if user.created_at else '',
            'last_login': user.last_login.strftime('%Y-%m-%d %H:%M:%S') if user.last_login else '',
        }
