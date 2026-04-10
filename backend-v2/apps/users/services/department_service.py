"""
部门服务
"""

from django.db import models, transaction
from django.core.paginator import Paginator
from apps.core.exceptions import ValidationError, NotFoundError, PermissionDenied
from apps.users.models import Department, User


class DepartmentService:
    """部门服务"""

    def get_department_list(
        self,
        requester,
        search: str = None,
        page: int = 1,
        page_size: int = 10,
        no_page: bool = False
    ) -> dict:
        if not requester.is_super_admin:
            raise PermissionDenied('只有超级管理员可以查看部门列表')
        
        queryset = Department.objects.annotate(
            user_count=models.Count('users')
        ).order_by('order')
        
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
            ).get(id=department_id)
        except Department.DoesNotExist:
            raise NotFoundError('部门不存在')
        
        return self._format_department_detail(department)

    @transaction.atomic
    def create_department(self, requester, data: dict) -> Department:
        if not requester.is_super_admin:
            raise PermissionDenied('只有超级管理员可以创建部门')
        
        name = data.get('name', '').strip()
        if not name:
            raise ValidationError('部门名称不能为空')
        
        if Department.objects.filter(name=name).exists():
            raise ValidationError(f'部门名称 "{name}" 已存在')
        
        code = data.get('code', '').strip()
        if not code:
            code = name.lower().replace(' ', '_')
        
        if Department.objects.filter(code=code).exists():
            raise ValidationError(f'部门编码 "{code}" 已存在')
        
        max_order = Department.objects.aggregate(
            max_order=models.Max('order')
        )['max_order'] or 0
        
        department = Department.objects.create(
            name=name,
            code=code,
            description=data.get('description', ''),
            order=max_order + 1
        )
        
        return department

    @transaction.atomic
    def update_department(self, requester, department_id: int, data: dict) -> Department:
        if not requester.is_super_admin:
            raise PermissionDenied('只有超级管理员可以修改部门')
        
        try:
            department = Department.objects.get(id=department_id)
        except Department.DoesNotExist:
            raise NotFoundError('部门不存在')
        
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
        
        department.save()
        return department

    @transaction.atomic
    def delete_department(self, requester, department_id: int) -> bool:
        if not requester.is_super_admin:
            raise PermissionDenied('只有超级管理员可以删除部门')
        
        try:
            department = Department.objects.get(id=department_id)
        except Department.DoesNotExist:
            raise NotFoundError('部门不存在')
        
        user_count = User.objects.filter(department=department).count()
        if user_count > 0:
            raise ValidationError(f'部门下还有 {user_count} 个用户，无法删除')
        
        deleted_order = department.order
        department.delete()
        
        Department.objects.filter(
            order__gt=deleted_order
        ).update(order=models.F('order') - 1)
        
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
        return {
            'id': department.id,
            'order': department.order,
            'name': department.name,
            'code': department.code or '',
            'description': department.description or '',
            'user_count': department.user_count,
            'created_at': department.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        }

    def _format_department_detail(self, department) -> dict:
        data = self._format_department(department)
        data.update({
            'updated_at': department.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
        })
        return data
