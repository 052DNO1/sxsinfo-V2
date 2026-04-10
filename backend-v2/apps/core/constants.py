"""
核心常量
"""

from enum import Enum


class UserRole(int, Enum):
    """用户角色"""
    TEACHER = 1
    LABORATORY_ADMIN = 2
    DEPARTMENT_ADMIN = 4
    SUPER_ADMIN = 16
    SYSTEM_ADMIN = 32


class UserStatus(int, Enum):
    """用户状态"""
    ACTIVE = 1
    INACTIVE = 0
    PENDING = 2


class LaboratoryStatus(int, Enum):
    """实训室状态"""
    AVAILABLE = 1
    IN_USE = 2
    MAINTENANCE = 3
    UNAVAILABLE = 4


class EquipmentStatus(str, Enum):
    """设备状态"""
    NORMAL = 'NORMAL'
    MAINTENANCE = 'MAINTENANCE'
    DAMAGED = 'DAMAGED'
    SCRAPPED = 'SCRAPPED'
    BORROWED = 'BORROWED'


class WorkOrderStatus(str, Enum):
    """工单状态"""
    PENDING = 'PENDING'
    PROCESSING = 'PROCESSING'
    COMPLETED = 'COMPLETED'
    CLOSED = 'CLOSED'


class MaintenanceType(int, Enum):
    """维护类型"""
    ROUTINE = 1
    SAFETY = 2
    REPAIR = 3
    UPGRADE = 4


class WeekDay(int, Enum):
    """星期"""
    MONDAY = 1
    TUESDAY = 2
    WEDNESDAY = 3
    THURSDAY = 4
    FRIDAY = 5
    SATURDAY = 6
    SUNDAY = 7


PAGINATION_PAGE_SIZE = 20
PAGINATION_MAX_PAGE_SIZE = 100
ACCESS_TOKEN_LIFETIME = 2
REFRESH_TOKEN_LIFETIME = 7
