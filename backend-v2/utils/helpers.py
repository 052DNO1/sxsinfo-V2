"""
工具函数
"""

from datetime import datetime, date
from typing import Any, Dict, List, Optional
import hashlib
import random
import string
import uuid


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
    """解析日期范围字符串"""
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
    """格式化日期时间"""
    if dt:
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
