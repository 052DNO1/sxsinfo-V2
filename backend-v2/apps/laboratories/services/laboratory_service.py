"""
实训室服务
"""

from django.db import models, transaction
from django.db.models import Count, Q
from django.core.paginator import Paginator
from apps.core.exceptions import ValidationError, NotFoundError, PermissionDenied
from apps.core.constants import LaboratoryStatus
from apps.laboratories.models import Laboratory
from apps.users.models import User


class LaboratoryService:
    """实训室服务"""

    def get_laboratory_list(
        self,
        requester,
        department_id: int = None,
        status: int = None,
        laboratory_type: str = None,
        search: str = None,
        page: int = 1,
        page_size: int = 20,
        no_page: bool = False
    ) -> dict:
        queryset = Laboratory.objects.select_related('department', 'admin').filter(is_deleted=False)
        
        if requester.is_department_admin and not requester.is_super_admin:
            queryset = queryset.filter(department_id=requester.department_id)
        elif requester.is_laboratory_admin and not requester.is_super_admin:
            queryset = queryset.filter(admin=requester)
        
        if department_id:
            queryset = queryset.filter(department_id=department_id)
        if status is not None:
            queryset = queryset.filter(status=status)
        if laboratory_type:
            queryset = queryset.filter(laboratory_type=laboratory_type)
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(code__icontains=search) |
                Q(building__icontains=search)
            )
        
        queryset = queryset.annotate(
            equipment_count=Count('equipments', filter=Q(equipments__is_deleted=False))
        )
        
        queryset = queryset.order_by('code')
        
        if no_page:
            return {
                'list': [self._format_laboratory(lab) for lab in queryset],
                'pagination': {
                    'total': queryset.count(),
                }
            }
        
        paginator = Paginator(queryset, page_size)
        page_obj = paginator.get_page(page)
        
        return {
            'list': [self._format_laboratory(lab) for lab in page_obj],
            'pagination': {
                'total': paginator.count,
                'page': page,
                'page_size': page_size,
                'total_pages': paginator.num_pages,
            }
        }

    def get_laboratory_detail(self, requester, laboratory_id: int) -> dict:
        try:
            laboratory = Laboratory.objects.select_related('department', 'admin').get(
                id=laboratory_id, is_deleted=False
            )
        except Laboratory.DoesNotExist:
            raise NotFoundError('实训室不存在')
        
        if not self._can_view_laboratory(requester, laboratory):
            raise PermissionDenied('无权限查看该实训室')
        
        return self._format_laboratory_detail(laboratory)

    @transaction.atomic
    def create_laboratory(self, requester, data: dict) -> Laboratory:
        if not requester.is_department_admin and not requester.is_super_admin:
            raise PermissionDenied('无权限创建实训室')
        
        code = data.get('code', '').strip()
        name = data.get('name', '').strip()
        
        if not code or not name:
            raise ValidationError('实训室编号和名称不能为空')
        
        existing = Laboratory.objects.filter(code=code).first()
        if existing:
            if existing.is_deleted:
                existing.code = f"del_{existing.id}"[:50]
                existing.save(update_fields=['code'])
            else:
                raise ValidationError(f'实训室编号 "{code}" 已存在')
        
        department_id = data.get('department_id')
        if not requester.is_super_admin:
            department_id = requester.department_id
        
        admin_id = data.get('admin_id')
        if admin_id:
            try:
                admin = User.objects.get(id=admin_id, is_deleted=False)
                if requester.is_department_admin and not requester.is_super_admin:
                    if admin.department_id != requester.department_id:
                        raise ValidationError('只能分配本部门的用户作为管理员')
            except User.DoesNotExist:
                raise ValidationError('指定的管理员不存在')
        
        laboratory = Laboratory.objects.create(
            name=name,
            code=code,
            building=data.get('building', ''),
            floor=data.get('floor'),
            room_number=data.get('room_number', ''),
            capacity=data.get('capacity', 30),
            area=data.get('area'),
            laboratory_type=data.get('laboratory_type', '普通实训室'),
            department_id=department_id,
            admin_id=admin_id,
            description=data.get('description', ''),
            note=data.get('note', ''),
        )
        
        return laboratory

    @transaction.atomic
    def update_laboratory(self, requester, laboratory_id: int, data: dict) -> Laboratory:
        try:
            laboratory = Laboratory.objects.get(id=laboratory_id, is_deleted=False)
        except Laboratory.DoesNotExist:
            raise NotFoundError('实训室不存在')
        
        if not self._can_manage_laboratory(requester, laboratory):
            raise PermissionDenied('无权限修改该实训室')
        
        if 'code' in data:
            code = data['code'].strip()
            if code != laboratory.code:
                existing = Laboratory.objects.filter(code=code).exclude(id=laboratory_id).first()
                if existing and not existing.is_deleted:
                    raise ValidationError(f'实训室编号 "{code}" 已存在')
                laboratory.code = code
        
        if 'name' in data:
            laboratory.name = data['name'].strip()
        
        for field in ['building', 'floor', 'room_number', 'capacity',
                      'area', 'laboratory_type', 'description', 'note', 'facilities']:
            if field in data:
                setattr(laboratory, field, data[field])
        
        if 'status' in data:
            laboratory.status = data['status']
            laboratory.is_available = data['status'] == LaboratoryStatus.AVAILABLE
        
        if 'admin' in data:
            admin_id = data['admin']
            if admin_id:
                try:
                    admin = User.objects.get(id=admin_id, is_deleted=False)
                    if requester.is_department_admin and not requester.is_super_admin:
                        if admin.department_id != laboratory.department_id:
                            raise ValidationError('只能分配本部门的用户作为管理员')
                    laboratory.admin = admin
                except User.DoesNotExist:
                    raise ValidationError('指定的管理员不存在')
            else:
                laboratory.admin = None
        
        laboratory.save()
        return laboratory

    @transaction.atomic
    def delete_laboratory(self, requester, laboratory_id: int) -> dict:
        try:
            laboratory = Laboratory.objects.get(id=laboratory_id, is_deleted=False)
        except Laboratory.DoesNotExist:
            raise NotFoundError('实训室不存在')
        
        if not self._can_delete_laboratory(requester, laboratory):
            raise PermissionDenied('无权限删除实训室')
        
        from apps.schedules.models import Schedule
        from apps.records.models import UsageRecord
        from apps.maintenance.models import WorkOrder
        from apps.laboratories.models import Equipment
        
        schedule_count = Schedule.objects.filter(laboratory=laboratory).count()
        record_count = UsageRecord.objects.filter(laboratory=laboratory).count()
        order_count = WorkOrder.objects.filter(laboratory=laboratory).count()
        equipment_count = Equipment.objects.filter(location=laboratory).count()
        
        Schedule.objects.filter(laboratory=laboratory).delete()
        UsageRecord.objects.filter(laboratory=laboratory).delete()
        WorkOrder.objects.filter(laboratory=laboratory).delete()
        Equipment.objects.filter(location=laboratory).delete()
        laboratory.delete()
        
        return {
            'success': True,
            'message': f'实训室已删除，同时删除了 {schedule_count} 条课表、{record_count} 条使用记录、{order_count} 条工单、{equipment_count} 台设备',
            'deleted_counts': {
                'schedules': schedule_count,
                'records': record_count,
                'orders': order_count,
                'equipment': equipment_count
            }
        }

    @transaction.atomic
    def batch_delete_laboratories(self, requester, laboratory_ids: list) -> dict:
        if not requester.is_super_admin and not requester.is_department_admin:
            raise PermissionDenied('无权限批量删除实训室')
        
        deleted_count = 0
        failed_list = []
        
        for lab_id in laboratory_ids:
            try:
                result = self.delete_laboratory(requester, lab_id)
                if result['success']:
                    deleted_count += 1
            except Exception as e:
                failed_list.append({'id': lab_id, 'reason': str(e)})
        
        return {
            'deleted_count': deleted_count,
            'failed_count': len(failed_list),
            'failed_list': failed_list,
        }

    def get_admin_options(self, requester) -> list:
        if requester.is_super_admin:
            admins = User.objects.filter(
                role__in=[2, 4, 6, 8, 16],
                is_active=True,
                is_deleted=False
            ).values('id', 'username', 'nickname')
        elif requester.is_department_admin:
            admins = User.objects.filter(
                department_id=requester.department_id,
                role__in=[2, 4, 6, 8, 16],
                is_active=True,
                is_deleted=False
            ).values('id', 'username', 'nickname')
        else:
            admins = []
        
        return [{'id': 0, 'username': '', 'nickname': '未分配'}] + list(admins)

    def get_laboratory_options(self, requester) -> list:
        queryset = Laboratory.objects.filter(is_deleted=False, is_available=True)
        
        if requester.is_department_admin and not requester.is_super_admin:
            queryset = queryset.filter(department_id=requester.department_id)
        elif requester.is_laboratory_admin and not requester.is_super_admin:
            queryset = queryset.filter(admin=requester)
        
        options = [{'id': '', 'text': '全部实训室'}]
        for lab in queryset:
            options.append({
                'id': lab.id,
                'text': f"{lab.name} ({lab.code})"
            })
        
        return options

    def _can_view_laboratory(self, user, laboratory: Laboratory) -> bool:
        if user.is_super_admin:
            return True
        if user.is_department_admin:
            return laboratory.department_id == user.department_id
        if user.is_laboratory_admin:
            return laboratory.admin_id == user.id
        return False

    def _can_manage_laboratory(self, user, laboratory: Laboratory) -> bool:
        if user.is_super_admin:
            return True
        if user.is_department_admin:
            return laboratory.department_id == user.department_id
        if user.is_laboratory_admin:
            return laboratory.admin_id == user.id
        return False

    def _can_delete_laboratory(self, user, laboratory: Laboratory) -> bool:
        if user.is_super_admin:
            return True
        if user.is_department_admin:
            return laboratory.department_id == user.department_id
        return False

    def _format_laboratory(self, laboratory: Laboratory) -> dict:
        from apps.schedules.models import Schedule
        
        schedule_count = Schedule.objects.filter(laboratory=laboratory).count()
        
        return {
            'id': laboratory.id,
            'name': laboratory.name,
            'code': laboratory.code,
            'location': laboratory.location,
            'capacity': laboratory.capacity,
            'laboratory_type': laboratory.laboratory_type,
            'department_id': laboratory.department_id,
            'department_name': laboratory.department.name if laboratory.department else None,
            'admin': laboratory.admin_id,
            'admin_name': laboratory.admin.nickname if laboratory.admin else None,
            'status': laboratory.status,
            'status_display': {
                'text': '可用' if laboratory.is_available else '不可用',
                'type': 'success' if laboratory.is_available else 'danger'
            },
            'is_available': laboratory.is_available,
            'equipment_count': getattr(laboratory, 'equipment_count', 0),
            'schedule_count': schedule_count,
            'note': laboratory.note or '',
            'created_at': laboratory.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        }

    def _format_laboratory_detail(self, laboratory: Laboratory) -> dict:
        data = self._format_laboratory(laboratory)
        data.update({
            'building': laboratory.building,
            'floor': laboratory.floor,
            'room_number': laboratory.room_number,
            'area': laboratory.area,
            'facilities': laboratory.facilities,
            'description': laboratory.description,
            'images': laboratory.images,
            'updated_at': laboratory.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
        })
        return data
