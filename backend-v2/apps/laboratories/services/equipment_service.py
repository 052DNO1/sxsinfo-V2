"""
设备服务
"""

from django.db import models, transaction
from django.core.paginator import Paginator
from apps.core.exceptions import ValidationError, NotFoundError, PermissionDenied
from apps.core.constants import EquipmentStatus
from apps.laboratories.models import Equipment, Laboratory
from apps.core.services.operation_log_service import OperationLogService
from common.decorators import cached_method
from common.services.cache_service import CacheInvalidator, cache_invalidate
from apps.core.utils import beijing_strftime, beijing_now, beijing_today


class EquipmentService:
    """设备服务"""

    @cached_method(timeout=60, key_prefix='equipment:list')
    def get_equipment_list(
        self,
        requester,
        laboratory_id: int = None,
        category: str = None,
        status: str = None,
        search: str = None,
        page: int = 1,
        page_size: int = 20,
        no_page: bool = False
    ) -> dict:
        queryset = Equipment.objects.select_related('laboratory').filter(is_deleted=False)
        
        if requester.is_department_admin and not requester.is_super_admin:
            queryset = queryset.filter(laboratory__department_id=requester.department_id)
        elif requester.is_laboratory_admin and not requester.is_super_admin:
            queryset = queryset.filter(laboratory__admin=requester)
        
        if laboratory_id:
            queryset = queryset.filter(laboratory_id=laboratory_id)
        if category:
            queryset = queryset.filter(category=category)
        if status:
            queryset = queryset.filter(status=status)
        if search:
            queryset = queryset.filter(
                models.Q(name__icontains=search) |
                models.Q(code__icontains=search) |
                models.Q(serial_number__icontains=search) |
                models.Q(brand__icontains=search) |
                models.Q(model__icontains=search)
            )
        
        queryset = queryset.order_by('code')
        
        if no_page:
            return {
                'list': [self._format_equipment(e) for e in queryset],
                'total': queryset.count(),
            }
        
        paginator = Paginator(queryset, page_size)
        page_obj = paginator.get_page(page)
        
        return {
            'list': [self._format_equipment(e) for e in page_obj],
            'total': paginator.count,
            'page': page,
            'page_size': page_size,
            'total_pages': paginator.num_pages,
        }

    def get_equipment_detail(self, requester, equipment_id: int) -> dict:
        try:
            equipment = Equipment.objects.select_related('laboratory').get(
                id=equipment_id, is_deleted=False
            )
        except Equipment.DoesNotExist:
            raise NotFoundError('设备不存在')
        
        if equipment.laboratory and not self._can_view_laboratory(requester, equipment.laboratory):
            raise PermissionDenied('无权限查看该设备')
        
        return self._format_equipment_detail(equipment)

    @transaction.atomic
    def create_equipment(self, requester, data: dict, request=None) -> Equipment:
        if not requester.is_laboratory_admin and not requester.is_department_admin and not requester.is_super_admin:
            raise PermissionDenied('无权限创建设备')
        
        code = data.get('code', '').strip()
        if not code:
            raise ValidationError('设备编号不能为空')
        
        name = data.get('name', '').strip()
        if not name:
            raise ValidationError('设备名称不能为空')
        
        laboratory = None
        laboratory_obj = data.get('laboratory')
        if laboratory_obj:
            try:
                if isinstance(laboratory_obj, Laboratory):
                    laboratory = laboratory_obj
                else:
                    laboratory = Laboratory.objects.get(id=laboratory_obj, is_deleted=False)
            except Laboratory.DoesNotExist:
                raise NotFoundError('实训室不存在')
            
            from apps.core.constants import LaboratoryStatus
            if laboratory.status != LaboratoryStatus.AVAILABLE:
                raise ValidationError(f'该实训室当前状态为"{laboratory.get_status_display()}"，不可使用，请更换其他实训室')
            
            if not self._can_manage_laboratory(requester, laboratory):
                raise PermissionDenied('无权限在该实训室创建设备')
            
            existing = Equipment.objects.filter(code=code, laboratory=laboratory).first()
            if existing and not existing.is_deleted:
                raise ValidationError(f'设备编号 "{code}" 在该实训室已存在')
        
        equipment = Equipment.objects.create(
            name=name,
            code=code,
            category=data.get('category', '计算机'),
            brand=data.get('brand', ''),
            model=data.get('model', ''),
            serial_number=data.get('serial_number', ''),
            laboratory=laboratory if laboratory_obj else None,
            position=data.get('position', ''),
            cpu=data.get('cpu', ''),
            memory=data.get('memory', ''),
            disk=data.get('disk', ''),
            gpu=data.get('gpu', ''),
            os=data.get('os', ''),
            purchase_date=data.get('purchase_date'),
            warranty_expire=data.get('warranty_expire'),
            price=data.get('price'),
            supplier=data.get('supplier', ''),
            status=data.get('status', EquipmentStatus.NORMAL),
            description=data.get('description', ''),
            note=data.get('note', ''),
        )

        OperationLogService.log_equipment_operation(
            request=request,
            operation_type='equipment_create',
            equipment=equipment
        )

        return equipment

    @transaction.atomic
    def update_equipment(self, requester, equipment_id: int, data: dict, request=None) -> Equipment:
        try:
            equipment = Equipment.objects.select_related('laboratory').get(
                id=equipment_id, is_deleted=False
            )
        except Equipment.DoesNotExist:
            raise NotFoundError('设备不存在')

        if equipment.laboratory and not self._can_manage_laboratory(requester, equipment.laboratory):
            raise PermissionDenied('无权限修改该设备')

        old_data = {
            'name': equipment.name,
            'code': equipment.code,
            'category': equipment.category,
            'brand': equipment.brand,
            'model': equipment.model,
            'status': equipment.status,
            'laboratory_id': equipment.laboratory_id,
        }

        if 'code' in data:
            code = data['code'].strip()
            if not code:
                raise ValidationError('设备编号不能为空')
            equipment.code = code

        if 'name' in data:
            equipment.name = data['name'].strip()
        
        for field in ['category', 'brand', 'model', 'serial_number', 'position',
                      'cpu', 'memory', 'disk', 'gpu', 'os', 'purchase_date',
                      'warranty_expire', 'price', 'supplier', 'status',
                      'description', 'note']:
            if field in data:
                setattr(equipment, field, data[field])
        
        if 'laboratory' in data:
            new_laboratory = data['laboratory']
            if new_laboratory:
                try:
                    if isinstance(new_laboratory, Laboratory):
                        laboratory_id = new_laboratory.id
                    else:
                        laboratory_id = new_laboratory
                    new_lab = Laboratory.objects.get(id=laboratory_id, is_deleted=False)
                    if self._can_manage_laboratory(requester, new_lab):
                        equipment.laboratory_id = laboratory_id
                except Laboratory.DoesNotExist:
                    raise ValidationError('目标实训室不存在')
            else:
                equipment.laboratory_id = None
        
        equipment.save()

        new_data = {
            'name': equipment.name,
            'code': equipment.code,
            'category': equipment.category,
            'brand': equipment.brand,
            'model': equipment.model,
            'status': equipment.status,
            'laboratory_id': equipment.laboratory_id,
        }

        OperationLogService.log_equipment_operation(
            request=request,
            operation_type='equipment_update',
            equipment=equipment,
            old_data=old_data,
            new_data=new_data
        )

        return equipment

    @transaction.atomic
    def delete_equipment(self, requester, equipment_id: int, request=None) -> bool:
        try:
            equipment = Equipment.objects.select_related('laboratory').get(
                id=equipment_id, is_deleted=False
            )
        except Equipment.DoesNotExist:
            raise NotFoundError('设备不存在')
        
        if equipment.laboratory and not self._can_manage_laboratory(requester, equipment.laboratory):
            raise PermissionDenied('无权限删除该设备')

        equipment_name = f'{equipment.name}({equipment.code})'
        equipment.delete()
        
        CacheInvalidator.invalidate_equipment_cache(user_id=requester.id)

        OperationLogService.log_equipment_operation(
            request=request,
            operation_type='equipment_delete',
            equipment=equipment,
            description=f'删除了设备 {equipment_name}'
        )
        
        return True

    @transaction.atomic
    def batch_delete_equipments(self, requester, equipment_ids: list) -> dict:
        deleted_count = 0
        failed_list = []
        
        for equipment_id in equipment_ids:
            try:
                self.delete_equipment(requester, equipment_id)
                deleted_count += 1
            except Exception as e:
                failed_list.append({'id': equipment_id, 'reason': str(e)})
        
        return {
            'deleted_count': deleted_count,
            'failed_count': len(failed_list),
            'failed_list': failed_list,
        }

    def get_category_options(self) -> list:
        categories = Equipment.objects.filter(
            is_deleted=False
        ).values_list('category', flat=True).distinct()
        
        default_categories = ['计算机', '服务器', '网络设备', '投影仪', '打印机', '其他设备']
        
        all_categories = set(categories) | set(default_categories)
        
        return [{'value': c, 'label': c} for c in sorted(all_categories)]

    def get_status_options(self) -> list:
        return [
            {'value': s.value, 'label': s.name} for s in EquipmentStatus
        ]

    def _can_view_laboratory(self, user, laboratory: Laboratory) -> bool:
        if user.is_super_admin:
            return True
        if user.is_department_admin:
            return laboratory.department_id == user.department_id
        if user.is_laboratory_admin:
            return laboratory.admin_id == user.id
        return True

    def _can_manage_laboratory(self, user, laboratory: Laboratory) -> bool:
        if user.is_super_admin:
            return True
        if user.is_department_admin:
            return laboratory.department_id == user.department_id
        if user.is_laboratory_admin:
            return laboratory.admin_id == user.id
        return False

    def _format_equipment(self, equipment: Equipment) -> dict:
        config_parts = []
        if equipment.cpu:
            config_parts.append(f'CPU: {equipment.cpu}')
        if equipment.memory:
            config_parts.append(f'内存: {equipment.memory}')
        if equipment.disk:
            config_parts.append(f'硬盘: {equipment.disk}')
        if equipment.gpu:
            config_parts.append(f'显卡: {equipment.gpu}')
        if equipment.os:
            config_parts.append(f'系统: {equipment.os}')

        return {
            'id': equipment.id,
            'name': equipment.name,
            'code': equipment.code,
            'category': equipment.category,
            'brand': equipment.brand,
            'model': equipment.model,
            'serial_number': equipment.serial_number,
            'laboratory_id': equipment.laboratory_id,
            'laboratory_name': equipment.laboratory.name if equipment.laboratory else None,
            'laboratory_code': equipment.laboratory.code if equipment.laboratory else None,
            'position': equipment.position,
            'cpu': equipment.cpu,
            'memory': equipment.memory,
            'disk': equipment.disk,
            'gpu': equipment.gpu,
            'os': equipment.os,
            'config': ' | '.join(config_parts) if config_parts else None,
            'status': equipment.status,
            'purchase_date': beijing_strftime(equipment.purchase_date, '%Y-%m-%d') or None,
            'warranty_expire': beijing_strftime(equipment.warranty_expire, '%Y-%m-%d') or None,
            'created_at': beijing_strftime(equipment.created_at),
        }

    def _format_equipment_detail(self, equipment: Equipment) -> dict:
        data = self._format_equipment(equipment)
        data.update({
            'cpu': equipment.cpu,
            'memory': equipment.memory,
            'disk': equipment.disk,
            'gpu': equipment.gpu,
            'os': equipment.os,
            'price': str(equipment.price) if equipment.price else None,
            'supplier': equipment.supplier,
            'last_maintenance_date': beijing_strftime(equipment.last_maintenance_date, '%Y-%m-%d') or None,
            'total_usage_hours': equipment.total_usage_hours,
            'description': equipment.description,
            'note': equipment.note,
            'updated_at': beijing_strftime(equipment.updated_at),
        })
        return data
