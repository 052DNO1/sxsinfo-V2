"""
枚举类
"""

from enum import Enum


class BaseEnum(Enum):
    """基础枚举类"""
    
    @classmethod
    def choices(cls):
        """获取Django choices格式"""
        return [(item.value, item.name) for item in cls]
    
    @classmethod
    def values(cls):
        """获取所有值"""
        return [item.value for item in cls]
    
    @classmethod
    def names(cls):
        """获取所有名称"""
        return [item.name for item in cls]
    
    @classmethod
    def get_name(cls, value):
        """根据值获取名称"""
        for item in cls:
            if item.value == value:
                return item.name
        return None
