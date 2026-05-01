"""
工具函数
"""

import uuid
import hashlib
import random
import string
from datetime import datetime, date
from typing import Any, Dict, List, Optional
from django.utils import timezone


def beijing_now() -> datetime:
    """返回当前北京时间（时区感知的 Asia/Shanghai 时间）"""
    return timezone.localtime(timezone.now())


def beijing_today() -> date:
    """返回当前北京日期"""
    return beijing_now().date()


def beijing_strftime(dt, fmt: str = '%Y-%m-%d %H:%M:%S') -> str:
    """将 datetime 按北京时间格式化（自动转换时区），date 对象直接格式化"""
    if dt is None:
        return ''
    if isinstance(dt, date) and not isinstance(dt, datetime):
        return dt.strftime(fmt)
    if timezone.is_aware(dt):
        dt = timezone.localtime(dt)
    return dt.strftime(fmt)


def generate_uuid() -> str:
    """生成UUID"""
    return str(uuid.uuid4()).replace('-', '')


def generate_code(prefix: str = '', length: int = 8) -> str:
    """生成编码"""
    chars = string.ascii_uppercase + string.digits
    code = ''.join(random.choice(chars) for _ in range(length))
    return f"{prefix}{code}" if prefix else code


def md5_hash(text: str) -> str:
    """MD5哈希"""
    return hashlib.md5(text.encode()).hexdigest()


def parse_date_range(date_str: str) -> List[int]:
    """
    解析日期范围字符串
    如: "1-4" -> [1, 2, 3, 4]
    如: "1,3,5" -> [1, 3, 5]
    """
    points = []
    for part in date_str.split(','):
        part = part.strip()
        if not part:
            continue
        if '-' in part:
            try:
                start, end = map(int, part.split('-'))
                points.extend(range(start, end + 1))
            except ValueError:
                continue
        else:
            try:
                points.append(int(part))
            except ValueError:
                continue
    return sorted(set(points))


def format_datetime(dt: datetime, fmt: str = '%Y-%m-%d %H:%M:%S') -> str:
    """格式化日期时间（自动转换为北京时间）"""
    if dt:
        if timezone.is_aware(dt):
            dt = timezone.localtime(dt)
        return dt.strftime(fmt)
    return ''


def format_date(d: date, fmt: str = '%Y-%m-%d') -> str:
    """格式化日期"""
    if d:
        return d.strftime(fmt)
    return ''


def chunks(lst: List[Any], n: int) -> List[List[Any]]:
    """将列表分割成指定大小的块"""
    return [lst[i:i + n] for i in range(0, len(lst), n)]


def flatten_dict(d: Dict, parent_key: str = '', sep: str = '.') -> Dict:
    """扁平化字典"""
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep).items())
        else:
            items.append((new_key, v))
    return dict(items)
