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


class UserService:
    """用户服务"""

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
        
        return user

    @transaction.atomic
    def update_user(self, requester, user_id: int, data: dict):
        try:
            user = User.objects.get(id=user_id, is_deleted=False)
        except User.DoesNotExist:
            raise NotFoundError('用户不存在')
        
        if not self._can_manage_user(requester, user):
            raise PermissionDenied('无权限修改该用户')
        
        allowed_fields = ['username', 'nickname', 'phone', 'email', 'status']
        if requester.is_super_admin or requester.is_department_admin:
            allowed_fields.extend(['role', 'department_id'])
        
        for field in allowed_fields:
            if field in data:
                setattr(user, field, data[field])
        
        user.save()
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
        
        return {
            'user_id': user_id,
            'username': user.username,
            'cleaned': cleaned,
            'message': '用户数据清理完成'
        }

    @transaction.atomic
    def import_users(self, requester, file_data) -> dict:
        if not requester.is_department_admin and not requester.is_super_admin:
            raise PermissionDenied('无权限导入用户')
        
        try:
            wb = load_workbook(filename=io.BytesIO(file_data.read()))
            ws = wb.active
            rows = list(ws.iter_rows(values_only=True))
            
            if len(rows) < 2:
                raise ValidationError('文件内容为空或只有表头')
            
            header_row = rows[0]
            header_map = {str(h).strip(): idx for idx, h in enumerate(header_row) if h}
            
            def get_value(row, *keys):
                for key in keys:
                    if key in header_map:
                        val = row[header_map[key]]
                        return str(val).strip() if val is not None else ''
                return ''
        except Exception as e:
            raise ValidationError(f'文件解析失败: {str(e)}')
        
        success_count = 0
        failed_list = []
        
        for row_num, row in enumerate(rows[1:], start=2):
            try:
                username = get_value(row, '用户名', 'username')
                nickname = get_value(row, '昵称', 'nickname') or username
                
                if not username:
                    failed_list.append({'row': row_num, 'reason': '用户名为空'})
                    continue
                
                if User.objects.filter(username=username).exists():
                    failed_list.append({'row': row_num, 'reason': f'用户名 "{username}" 已存在'})
                    continue
                
                department_name = get_value(row, '部门', 'department')
                department_id = None
                if department_name:
                    dept = Department.objects.filter(name=department_name).first()
                    if dept:
                        department_id = dept.id
                
                if not requester.is_super_admin:
                    department_id = requester.department_id
                
                role_str = get_value(row, '权限', 'role')
                role = UserRole.TEACHER
                if role_str:
                    role_map = {'教师': 1, '实训室管理员': 2, '部门管理员': 4, '分院管理员': 4}
                    for role_name, role_val in role_map.items():
                        if role_name in role_str:
                            role |= role_val
                    if role == UserRole.TEACHER and role_str.isdigit():
                        role = int(role_str)
                else:
                    if requester.is_super_admin:
                        role = UserRole.DEPARTMENT_ADMIN
                
                phone = get_value(row, '手机号', 'phone')
                email = get_value(row, '邮箱', 'email')
                
                default_password = username[:6]
                User.objects.create_user(
                    username=username,
                    nickname=nickname,
                    phone=phone,
                    email=email,
                    role=role,
                    department_id=department_id,
                    password=default_password
                )
                success_count += 1
                
            except Exception as e:
                failed_list.append({'row': row_num, 'reason': str(e)})
        
        return {
            'success_count': success_count,
            'failed_count': len(failed_list),
            'failed_list': failed_list,
        }

    def get_user_options(self, requester) -> list:
        queryset = User.objects.filter(is_deleted=False, is_active=True)
        
        if requester.is_department_admin and not requester.is_super_admin:
            queryset = queryset.filter(department_id=requester.department_id)
        
        return [
            {'id': u.id, 'username': u.username, 'nickname': u.nickname}
            for u in queryset
        ]

    def _can_manage_user(self, requester, target) -> bool:
        if requester.is_super_admin:
            return True
        if requester.is_department_admin:
            return target.department_id == requester.department_id
        return False

    def _format_user(self, user) -> dict:
        role_display_map = {
            1: '教师',
            2: '实训室管理员',
            4: '部门管理员',
            16: '超级管理员',
            32: '系统管理员',
        }
        
        role_display = []
        if user.role:
            for role_val, role_name in role_display_map.items():
                if user.role & role_val:
                    role_display.append(role_name)
        
        managed_labs = []
        if hasattr(user, 'managed_laboratories'):
            managed_labs = [lab.name for lab in user.managed_laboratories.filter(is_deleted=False)]
        
        return {
            'id': user.id,
            'username': user.username,
            'nickname': user.nickname,
            'phone': user.phone,
            'email': user.email,
            'role': user.role,
            'role_display': ', '.join(role_display) if role_display else '普通用户',
            'roles': user.get_roles(),
            'department_id': user.department_id,
            'department_name': user.department.name if user.department else None,
            'status': user.status,
            'is_active': user.is_active,
            'managed_laboratories': ', '.join(managed_labs) if managed_labs else '-',
            'avatar': user.avatar.url if user.avatar else None,
            'created_at': user.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        }
