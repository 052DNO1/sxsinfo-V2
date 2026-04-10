"""
课表冲突检测服务
"""

from typing import List, Dict, Tuple
from django.db.models import Q
from apps.schedules.models import Schedule


class ConflictChecker:
    """课表冲突检测器"""

    @staticmethod
    def check_laboratory_conflict(
        laboratory_id: int,
        weekday: int,
        time_slot: str,
        weeks: str,
        exclude_schedule_id: int = None
    ) -> Tuple[bool, List[Dict]]:
        """检测实训室时间冲突"""
        from apps.core.utils import parse_date_range
        
        time_points = parse_date_range(time_slot)
        week_points = parse_date_range(weeks)
        
        queryset = Schedule.objects.filter(
            laboratory_id=laboratory_id,
            weekday=weekday,
            is_deleted=False,
            is_archived=False
        )
        
        if exclude_schedule_id:
            queryset = queryset.exclude(id=exclude_schedule_id)
        
        conflicts = []
        for schedule in queryset:
            existing_time = set(schedule.get_time_points())
            existing_weeks = set(schedule.get_week_points())
            
            time_conflict = set(time_points) & existing_time
            week_conflict = set(week_points) & existing_weeks
            
            if time_conflict and week_conflict:
                conflicts.append({
                    'schedule_id': schedule.id,
                    'course_name': schedule.course_name,
                    'teacher_name': schedule.teacher_name or (
                        schedule.teacher.nickname if schedule.teacher else ''
                    ),
                    'time_slot': schedule.time_slot,
                    'weeks': schedule.weeks,
                    'conflict_time': sorted(time_conflict),
                    'conflict_weeks': sorted(week_conflict),
                })
        
        return len(conflicts) > 0, conflicts

    @staticmethod
    def check_teacher_conflict(
        teacher_id: int,
        weekday: int,
        time_slot: str,
        weeks: str,
        exclude_schedule_id: int = None
    ) -> Tuple[bool, List[Dict]]:
        """检测教师时间冲突"""
        from apps.core.utils import parse_date_range
        
        time_points = parse_date_range(time_slot)
        week_points = parse_date_range(weeks)
        
        queryset = Schedule.objects.filter(
            teacher_id=teacher_id,
            weekday=weekday,
            is_deleted=False,
            is_archived=False
        )
        
        if exclude_schedule_id:
            queryset = queryset.exclude(id=exclude_schedule_id)
        
        conflicts = []
        for schedule in queryset:
            existing_time = set(schedule.get_time_points())
            existing_weeks = set(schedule.get_week_points())
            
            time_conflict = set(time_points) & existing_time
            week_conflict = set(week_points) & existing_weeks
            
            if time_conflict and week_conflict:
                conflicts.append({
                    'schedule_id': schedule.id,
                    'course_name': schedule.course_name,
                    'laboratory_name': schedule.laboratory.name,
                    'time_slot': schedule.time_slot,
                    'weeks': schedule.weeks,
                })
        
        return len(conflicts) > 0, conflicts
