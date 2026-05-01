"""
部门服务
"""

from django.db import models, transaction
from django.core.paginator import Paginator
from django.db import connection
from apps.core.exceptions import ValidationError, NotFoundError, PermissionDenied
from apps.core.services.operation_log_service import OperationLogService
from apps.users.models import Department, User
from common.services.cache_service import CacheInvalidator
from apps.core.utils import beijing_strftime, beijing_now, beijing_today


def _invalidate_caches(old_manager_ids, new_manager_ids, requester_id):
    """专门用于清理缓存的函数"""
    try:
        for old_id in old_manager_ids:
            CacheInvalidator.invalidate_user_cache(old_id)
        for new_id in new_manager_ids:
            CacheInvalidator.invalidate_user_cache(new_id)
        CacheInvalidator.invalidate_user_cache(requester_id)
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Failed to invalidate cache: {e}")


class DepartmentService:
    """部门服务"""

    def check_manager_conflicts(self, requester, department_id: int, manager_ids: list) -> dict:
        if not requester.is_super_admin:
            raise PermissionDenied('只有超级管理员可以检查管理员冲突')
        
        conflicts = []
        for user_id in manager_ids:
            try:
                user = User.objects.get(id=user_id)
                managed_depts = user.managed_departments.exclude(id=department_id)
                if managed_depts.exists():
                    conflicts.append({
                        'user_id': user.id,
                        'username': user.username,
                        'nickname': user.nickname or user.username,
                        'current_departments': [
                            {'id': d.id, 'name': d.name}
                            for d in managed_depts
                        ]
                    })
            except User.DoesNotExist:
                pass
        
        return {
            'has_conflicts': len(conflicts) > 0,
            'conflicts': conflicts
        }

    def get_department_list(
        self,
        requester,
        search: str = None,
        page: int = 1,
        page_size: int = 10,
        no_page: bool = False
    ) -> dict:
        if not (requester.is_superuser or requester.is_super_admin or requester.is_department_admin):
            raise PermissionDenied('只有管理员可以查看部门列表')

        queryset = Department.objects.annotate(
            user_count=models.Count('users')
        ).prefetch_related('managers').order_by('order')

        if requester.is_department_admin and not requester.is_superuser and not requester.is_super_admin:
            managed_dept_ids = requester.managed_departments.values_list('id', flat=True)
            if managed_dept_ids:
                queryset = queryset.filter(id__in=managed_dept_ids)
            else:
                queryset = queryset.none()
        
        if search:
            queryset = queryset.filter(
                models.Q(name__icontains=search) |
                models.Q(description__icontains=search)
            )
        
        if no_page:
            return {
                'list': [self._format_department(d) for d in queryset],
                'pagination': {
                    'total': queryset.count(),
                }
            }
        
        paginator = Paginator(queryset, page_size)
        page_obj = paginator.get_page(page)
        
        return {
            'list': [self._format_department(d) for d in page_obj],
            'pagination': {
                'total': paginator.count,
                'page': page,
                'page_size': page_size,
                'total_pages': paginator.num_pages,
            }
        }

    def get_department_detail(self, requester, department_id: int) -> dict:
        if not requester.is_super_admin:
            raise PermissionDenied('只有超级管理员可以查看部门详情')
        
        try:
            department = Department.objects.annotate(
                user_count=models.Count('users')
            ).prefetch_related('managers').get(id=department_id)
        except Department.DoesNotExist:
            raise NotFoundError('部门不存在')
        
        return self._format_department_detail(department)

    @transaction.atomic
    def create_department(self, requester, data: dict, request=None) -> Department:
        if not requester.is_super_admin:
            raise PermissionDenied('只有超级管理员可以创建部门')
        
        name = data.get('name', '').strip()
        if not name:
            raise ValidationError('部门名称不能为空')
        
        if Department.objects.filter(name=name).exists():
            raise ValidationError(f'部门名称 "{name}" 已存在')
        
        code = data.get('code') or ''
        code = code.strip()
        if not code:
            code = name.lower().replace(' ', '_')
        
        if Department.objects.filter(code=code).exists():
            raise ValidationError(f'部门编码 "{code}" 已存在')
        
        max_order = Department.objects.aggregate(
            max_order=models.Max('order')
        )['max_order'] or 0
        
        manager_ids = data.get('managers', [])
        manager_ids = [m.id if hasattr(m, 'id') else m for m in manager_ids] if manager_ids else []
        force_update = data.get('force_update', False)
        
        if manager_ids and not force_update:
            conflicts = self.check_manager_conflicts(requester, 0, manager_ids)
            if conflicts['has_conflicts']:
                return {
                    'requires_confirmation': True,
                    'conflicts': conflicts['conflicts'],
                    'message': '部分用户已经是其他部门的管理员，是否取消原来的绑定？'
                }
        
        department = Department.objects.create(
            name=name,
            code=code,
            description=data.get('description', ''),
            order=max_order + 1
        )
        
        if manager_ids:
            if force_update:
                for user_id in manager_ids:
                    try:
                        user = User.objects.get(id=user_id)
                        user.managed_departments.clear()
                    except User.DoesNotExist:
                        pass
            department.managers.set(manager_ids)

        OperationLogService.log_department_operation(
            request=request,
            operation_type='department_create',
            department=department
        )
        
        return department

    @transaction.atomic
    def update_department(self, requester, department_id: int, data: dict, request=None) -> Department:
        if not requester.is_super_admin:
            raise PermissionDenied('只有超级管理员可以修改部门')
        
        try:
            department = Department.objects.get(id=department_id)
        except Department.DoesNotExist:
            raise NotFoundError('部门不存在')

        old_data = {
            'name': department.name,
            'code': department.code,
            'description': department.description,
        }
        
        if 'name' in data:
            name = data['name'].strip()
            if not name:
                raise ValidationError('部门名称不能为空')
            if Department.objects.filter(name=name).exclude(id=department_id).exists():
                raise ValidationError(f'部门名称 "{name}" 已存在')
            department.name = name
        
        if 'code' in data:
            code = data['code'].strip()
            if code and Department.objects.filter(code=code).exclude(id=department_id).exists():
                raise ValidationError(f'部门编码 "{code}" 已存在')
            department.code = code
        
        if 'description' in data:
            department.description = data['description']
        
        if 'managers' in data:
            managers_data = data['managers']
            manager_ids = [m.id if hasattr(m, 'id') else m for m in managers_data] if managers_data else []
            force_update = data.get('force_update', False)
            
            if manager_ids and not force_update:
                conflicts = self.check_manager_conflicts(requester, department_id, manager_ids)
                if conflicts['has_conflicts']:
                    return {
                        'requires_confirmation': True,
                        'conflicts': conflicts['conflicts'],
                        'message': '部分用户已经是其他部门的管理员，是否取消原来的绑定？'
                    }
            
            old_managers = list(department.managers.filter(is_deleted=False).values_list('id', flat=True))
            new_manager_ids = set(manager_ids) if manager_ids else set()
            
            if manager_ids:
                if force_update:
                    for user_id in manager_ids:
                        try:
                            user = User.objects.get(id=user_id, is_deleted=False)
                            user.managed_departments.clear()
                            user.department_id = department.id
                            user.save(update_fields=['department_id'])
                        except User.DoesNotExist:
                            pass
                else:
                    for user_id in manager_ids:
                        try:
                            user = User.objects.get(id=user_id, is_deleted=False)
                            if user_id not in old_managers or user.department_id != department.id:
                                other_depts = Department.objects.filter(
                                    managers=user,
                                    is_deleted=False
                                ).exclude(id=department.id)
                                for other_dept in other_depts:
                                    other_dept.managers.remove(user)
                                user.department_id = department.id
                                user.save(update_fields=['department_id'])
                        except User.DoesNotExist:
                            pass
                
                department.managers.set(manager_ids)
                
                removed_manager_ids = set(old_managers) - new_manager_ids
                for removed_id in removed_manager_ids:
                    try:
                        removed_user = User.objects.get(id=removed_id, is_deleted=False)
                        is_admin_elsewhere = Department.objects.filter(
                            managers=removed_user,
                            is_deleted=False
                        ).exclude(id=department.id).exists()

                        if not is_admin_elsewhere:
                            removed_user.department_id = None
                            removed_user.save(update_fields=['department_id'])
                    except User.DoesNotExist:
                        pass
            else:
                for old_manager_id in old_managers:
                    try:
                        old_manager = User.objects.get(id=old_manager_id, is_deleted=False)
                        old_manager.department_id = None
                        old_manager.save(update_fields=['department_id'])
                    except User.DoesNotExist:
                        pass
                department.managers.clear()

        department.save()

        if 'managers' in data:
            transaction.on_commit(lambda: _invalidate_caches(
                list(old_managers),
                list(new_manager_ids),
                requester.id
            ))

        new_data = {
            'name': department.name,
            'code': department.code,
            'description': department.description,
        }

        OperationLogService.log_department_operation(
            request=request,
            operation_type='department_update',
            department=department,
            old_data=old_data,
            new_data=new_data
        )

        return department

    @transaction.atomic
    def delete_department(self, requester, department_id: int, cascade: bool = False, request=None) -> bool:
        if not requester.is_super_admin:
            raise PermissionDenied('只有超级管理员可以删除部门')
        
        try:
            department = Department.objects.get(id=department_id)
        except Department.DoesNotExist:
            raise NotFoundError('部门不存在')

        dept_name = department.name
        
        user_count = User.objects.filter(department=department).count()
        if user_count > 0 and not cascade:
            raise ValidationError(f'部门下还有 {user_count} 个用户，无法删除')
        
        if cascade and user_count > 0:
            User.objects.filter(department=department).delete()
        
        deleted_order = department.order
        department.delete()
        
        Department.objects.filter(
            order__gt=deleted_order
        ).update(order=models.F('order') - 1)

        OperationLogService.log_department_operation(
            request=request,
            operation_type='department_delete',
            department=None,
            description=f'删除了部门 {dept_name}'
        )
        
        return True

    @transaction.atomic
    def batch_delete_departments(self, requester, department_ids: list) -> dict:
        if not requester.is_super_admin:
            raise PermissionDenied('只有超级管理员可以删除部门')
        
        deleted_count = 0
        failed_list = []
        
        for dept_id in department_ids:
            try:
                self.delete_department(requester, dept_id)
                deleted_count += 1
            except Exception as e:
                failed_list.append({'id': dept_id, 'reason': str(e)})
        
        return {
            'deleted_count': deleted_count,
            'failed_count': len(failed_list),
            'failed_list': failed_list,
        }

    def get_department_options(self) -> list:
        departments = Department.objects.all().order_by('order')
        return [
            {'id': d.id, 'name': d.name}
            for d in departments
        ]

    def _format_department(self, department) -> dict:
        managers = department.managers.all()
        return {
            'id': department.id,
            'order': department.order,
            'name': department.name,
            'code': department.code or '',
            'description': department.description or '',
            'user_count': department.user_count,
            'managers': [{'id': m.id, 'name': m.nickname or m.username} for m in managers],
            'manager_ids': [m.id for m in managers],
            'manager_names': ', '.join([m.nickname or m.username for m in managers]) if managers else '暂无管理员',
            'created_at': beijing_strftime(department.created_at),
        }

    def _format_department_detail(self, department) -> dict:
        data = self._format_department(department)
        data.update({
            'updated_at': beijing_strftime(department.updated_at),
        })
        return data
