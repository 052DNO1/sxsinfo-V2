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
from common.services.cache_service import CacheInvalidator
from common.decorators import cached_method


class LaboratoryService:
    """实训室服务"""

    @cached_method(timeout=60, key_prefix='lab:list')
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
        
        admin_id = data.get('admin')
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

        CacheInvalidator.invalidate_laboratory_cache(
            user_id=requester.id,
            department_id=department_id
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

        CacheInvalidator.invalidate_laboratory_cache(
            user_id=requester.id,
            department_id=laboratory.department_id
        )

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
        equipment_count = Equipment.objects.filter(laboratory=laboratory).count()
        
        lab_name = laboratory.name
        lab_code = laboratory.code
        
        has_preserved_data = record_count > 0 or order_count > 0
        
        if has_preserved_data:
            UsageRecord.objects.filter(laboratory=laboratory).update(
                laboratory_name=lab_name,
                laboratory_code=lab_code,
                laboratory=None
            )
            WorkOrder.objects.filter(laboratory=laboratory).update(
                laboratory_name=lab_name,
                laboratory_code=lab_code,
                laboratory=None
            )
            
            Schedule.objects.filter(laboratory=laboratory).delete()
            Equipment.objects.filter(laboratory=laboratory).delete()

            laboratory.soft_delete(user=requester)
            
            CacheInvalidator.invalidate_laboratory_cache(
                user_id=requester.id,
                department_id=laboratory.department_id
            )
            
            return {
                'success': True,
                'message': f'实训室已删除，已删除 {schedule_count} 条课表、{equipment_count} 台设备，保留 {record_count} 条使用记录、{order_count} 条工单',
                'deleted_counts': {
                    'schedules': schedule_count,
                    'equipment': equipment_count
                },
                'preserved_counts': {
                    'usage_records': record_count,
                    'work_orders': order_count
                }
            }
        else:
            Schedule.objects.filter(laboratory=laboratory).delete()
            Equipment.objects.filter(laboratory=laboratory).delete()
            
            laboratory.delete()
            
            CacheInvalidator.invalidate_laboratory_cache(
                user_id=requester.id,
                department_id=laboratory.department_id
            )
            
            return {
                'success': True,
                'message': f'实训室已彻底删除，已删除 {schedule_count} 条课表、{equipment_count} 台设备',
                'deleted_counts': {
                    'schedules': schedule_count,
                    'equipment': equipment_count
                },
                'preserved_counts': {
                    'usage_records': 0,
                    'work_orders': 0
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

        if deleted_count > 0:
            CacheInvalidator.invalidate_laboratory_cache(
                user_id=requester.id,
                department_id=requester.department_id
            )

        return {
            'deleted_count': deleted_count,
            'failed_count': len(failed_list),
            'failed_list': failed_list,
        }

    def check_delete_impact(self, requester, laboratory_ids: list) -> dict:
        """
        检查实训室的关联数据
        返回有关联数据的实训室列表及其关联数量（仅用于展示，不影响删除操作）
        """
        if not requester.is_super_admin and not requester.is_department_admin:
            raise PermissionDenied('无权限删除实训室')

        from apps.schedules.models import Schedule
        from apps.records.models import UsageRecord
        from apps.maintenance.models import WorkOrder
        from apps.laboratories.models import Equipment

        affected_labs = []

        for lab_id in laboratory_ids:
            try:
                laboratory = Laboratory.objects.get(id=lab_id, is_deleted=False)
            except Laboratory.DoesNotExist:
                continue

            if requester.is_department_admin and laboratory.department_id != requester.department_id:
                continue

            schedule_count = Schedule.objects.filter(laboratory=laboratory).count()
            record_count = UsageRecord.objects.filter(laboratory=laboratory).count()
            order_count = WorkOrder.objects.filter(laboratory=laboratory).count()
            equipment_count = Equipment.objects.filter(laboratory=laboratory).count()

            affected_labs.append({
                'id': laboratory.id,
                'name': laboratory.name,
                'code': laboratory.code,
                'schedule_count': schedule_count,
                'record_count': record_count,
                'order_count': order_count,
                'equipment_count': equipment_count,
            })

        return {
            'has_related_data': len([lab for lab in affected_labs if lab['schedule_count'] > 0 or lab['equipment_count'] > 0 or lab['record_count'] > 0 or lab['order_count'] > 0]) > 0,
            'related_labs': affected_labs,
            'total_count': len(affected_labs)
        }

    def get_admin_options(self, requester) -> list:
        if requester.is_super_admin:
            admins = User.objects.filter(
                is_active=True,
                is_deleted=False
            ).extra(
                where=["role & 2 != 0"]
            ).values('id', 'username', 'nickname')
        elif requester.is_department_admin:
            admins = User.objects.filter(
                department_id=requester.department_id,
                is_active=True,
                is_deleted=False
            ).extra(
                where=["role & 2 != 0"]
            ).values('id', 'username', 'nickname')
        else:
            admins = []

        return [{'id': 0, 'username': '', 'nickname': '未分配'}] + list(admins)

    def get_laboratory_options(self, requester, include_unavailable: bool = True, force_all: bool = False) -> list:
        queryset = Laboratory.objects.filter(is_deleted=False)

        if not force_all:
            if requester.is_department_admin and not requester.is_super_admin:
                queryset = queryset.filter(department_id=requester.department_id)
            elif requester.is_laboratory_admin and not requester.is_super_admin:
                queryset = queryset.filter(admin=requester)
        
        status_map = {
            LaboratoryStatus.AVAILABLE: '可用',
            LaboratoryStatus.IN_USE: '使用中',
            LaboratoryStatus.MAINTENANCE: '维护中',
            LaboratoryStatus.UNAVAILABLE: '不可用',
        }
        
        options = [{'id': '', 'text': '全部实训室', 'disabled': False}]
        for lab in queryset:
            status_text = status_map.get(lab.status, '未知')
            is_disabled = lab.status != LaboratoryStatus.AVAILABLE
            options.append({
                'id': lab.id,
                'text': f"{lab.code} {lab.name} - {status_text}",
                'code': lab.code,
                'name': lab.name,
                'status': lab.status,
                'status_text': status_text,
                'is_available': lab.is_available,
                'disabled': is_disabled
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
        
        status_map = {
            LaboratoryStatus.AVAILABLE: '可用',
            LaboratoryStatus.IN_USE: '使用中',
            LaboratoryStatus.MAINTENANCE: '维护中',
            LaboratoryStatus.UNAVAILABLE: '不可用',
        }
        status_text = status_map.get(laboratory.status, '未知')
        
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
                'text': status_text,
                'type': 'success' if laboratory.status == LaboratoryStatus.AVAILABLE else 'danger'
            },
            'status_text': status_text,
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
