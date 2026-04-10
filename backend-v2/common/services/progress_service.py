"""
进度查询服务
"""

from django.core.cache import cache


class ProgressService:
    """进度查询服务"""

    CACHE_PREFIX = 'progress_'
    CACHE_TIMEOUT = 3600

    @classmethod
    def get_progress(cls, user_id: int, task_type: str = 'import') -> dict:
        cache_key = f'{cls.CACHE_PREFIX}{user_id}_{task_type}'
        progress = cache.get(cache_key)
        
        if progress:
            return progress
        
        return {
            'status': 'idle',
            'percent': 0,
            'message': '',
            'total': 0,
            'current': 0,
        }

    @classmethod
    def set_progress(
        cls,
        user_id: int,
        task_type: str,
        status: str,
        percent: int,
        message: str = '',
        total: int = 0,
        current: int = 0,
        extra_data: dict = None
    ) -> None:
        cache_key = f'{cls.CACHE_PREFIX}{user_id}_{task_type}'
        
        progress = {
            'status': status,
            'percent': percent,
            'message': message,
            'total': total,
            'current': current,
        }
        
        if extra_data:
            progress.update(extra_data)
        
        cache.set(cache_key, progress, cls.CACHE_TIMEOUT)

    @classmethod
    def clear_progress(cls, user_id: int, task_type: str) -> None:
        cache_key = f'{cls.CACHE_PREFIX}{user_id}_{task_type}'
        cache.delete(cache_key)

    @classmethod
    def start_task(cls, user_id: int, task_type: str, total: int = 0) -> None:
        cls.set_progress(
            user_id=user_id,
            task_type=task_type,
            status='running',
            percent=0,
            message='任务开始',
            total=total,
            current=0
        )

    @classmethod
    def update_progress(
        cls,
        user_id: int,
        task_type: str,
        current: int,
        total: int,
        message: str = ''
    ) -> None:
        percent = int((current / total) * 100) if total > 0 else 0
        
        cls.set_progress(
            user_id=user_id,
            task_type=task_type,
            status='running',
            percent=percent,
            message=message or f'处理中 {current}/{total}',
            total=total,
            current=current
        )

    @classmethod
    def complete_task(
        cls,
        user_id: int,
        task_type: str,
        message: str = '任务完成',
        extra_data: dict = None
    ) -> None:
        cls.set_progress(
            user_id=user_id,
            task_type=task_type,
            status='completed',
            percent=100,
            message=message,
            extra_data=extra_data
        )

    @classmethod
    def fail_task(
        cls,
        user_id: int,
        task_type: str,
        error_message: str
    ) -> None:
        cls.set_progress(
            user_id=user_id,
            task_type=task_type,
            status='failed',
            percent=0,
            message=error_message
        )
