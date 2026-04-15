"""
课表服务
"""

from django.db import models, transaction
from django.core.paginator import Paginator
from apps.core.exceptions import ValidationError, NotFoundError, PermissionDenied
from apps.core.exceptions import ScheduleConflictError
from apps.schedules.models import Schedule, Semester
from apps.laboratories.models import Laboratory
from apps.users.models import User
from .conflict_checker import ConflictChecker


class ScheduleService:
    """课表服务"""

    def get_schedule_list(
        self,
        requester,
        laboratory_id: int = None,
        teacher_id: int = None,
        semester_id: int = None,
        weekday: int = None,
        search: str = None,
        page: int = 1,
        page_size: int = 20,
        no_page: bool = False
    ) -> dict:
        queryset = Schedule.objects.select_related(
            'laboratory', 'teacher', 'semester'
        ).filter(is_deleted=False, is_archived=False)
        
        if requester.is_department_admin and not requester.is_super_admin:
            queryset = queryset.filter(laboratory__department_id=requester.department_id)
        elif requester.is_laboratory_admin and not requester.is_super_admin:
            queryset = queryset.filter(laboratory__admin=requester)
        elif requester.is_teacher and not requester.is_super_admin:
            queryset = queryset.filter(teacher=requester)
        
        if laboratory_id:
            queryset = queryset.filter(laboratory_id=laboratory_id)
        if teacher_id:
            queryset = queryset.filter(teacher_id=teacher_id)
        if semester_id:
            queryset = queryset.filter(semester_id=semester_id)
        else:
            current_semester = Semester.get_current()
            if current_semester:
                queryset = queryset.filter(semester=current_semester)
        if weekday is not None:
            queryset = queryset.filter(weekday=weekday)
        if search:
            queryset = queryset.filter(
                models.Q(course_name__icontains=search) |
                models.Q(class_name__icontains=search) |
                models.Q(teacher_name__icontains=search) |
                models.Q(laboratory__name__icontains=search) |
                models.Q(laboratory__code__icontains=search)
            )
        
        queryset = queryset.order_by('laboratory__code', 'weekday', 'time_slot')
        
        if no_page:
            return {
                'list': [self._format_schedule(s) for s in queryset],
                'total': queryset.count(),
            }
        
        paginator = Paginator(queryset, page_size)
        page_obj = paginator.get_page(page)
        
        return {
            'list': [self._format_schedule(s) for s in page_obj],
            'total': paginator.count,
            'page': page,
            'page_size': page_size,
            'total_pages': paginator.num_pages,
        }

    def get_schedule_detail(self, requester, schedule_id: int) -> dict:
        try:
            schedule = Schedule.objects.select_related(
                'laboratory', 'teacher', 'semester'
            ).get(id=schedule_id, is_deleted=False)
        except Schedule.DoesNotExist:
            raise NotFoundError('课表不存在')
        
        if not self._can_view_schedule(requester, schedule):
            raise PermissionDenied('无权限查看该课表')
        
        return self._format_schedule_detail(schedule, requester)

    @transaction.atomic
    def create_schedule(self, requester, data: dict) -> Schedule:
        laboratory_id = data.get('laboratory_id') or data.get('laboratory')
        if not laboratory_id:
            raise ValidationError('实训室为必填项')
        
        try:
            laboratory = Laboratory.objects.get(id=laboratory_id, is_deleted=False)
        except Laboratory.DoesNotExist:
            raise ValidationError('指定的实训室不存在')
        
        if not self._can_manage_schedule(requester, laboratory):
            raise PermissionDenied('无权限在该实训室创建课表')
        
        semester_id = data.get('semester_id')
        if semester_id:
            try:
                semester = Semester.objects.get(id=semester_id)
            except Semester.DoesNotExist:
                raise ValidationError('指定的学期不存在')
        else:
            semester = Semester.get_current()
            if not semester:
                raise ValidationError('未设置当前学期')
        
        course_name = data.get('course_name', '').strip()
        if not course_name:
            raise ValidationError('课程名称为必填项')
        
        weekday = data.get('weekday')
        if weekday is None:
            raise ValidationError('星期为必填项')
        try:
            weekday = int(weekday)
            if weekday < 1 or weekday > 7:
                raise ValidationError('星期必须在1-7之间')
        except (ValueError, TypeError):
            raise ValidationError('星期格式错误')
        
        time_slot = data.get('time_slot', '1-4')
        weeks = data.get('weeks', '1-18')
        
        has_conflict, conflicts = ConflictChecker.check_laboratory_conflict(
            laboratory_id=laboratory_id,
            weekday=weekday,
            time_slot=time_slot,
            weeks=weeks
        )
        
        if has_conflict:
            raise ScheduleConflictError(
                message='课表时间冲突',
                data={'conflicts': conflicts}
            )
        
        teacher_id = data.get('teacher_id')
        if teacher_id:
            try:
                teacher = User.objects.get(id=teacher_id, is_deleted=False)
            except User.DoesNotExist:
                raise ValidationError('指定的教师不存在')
        
        schedule = Schedule.objects.create(
            course_name=course_name,
            course_code=data.get('course_code', ''),
            weekday=weekday,
            time_slot=time_slot,
            weeks=weeks,
            laboratory_id=laboratory_id,
            semester=semester,
            teacher_id=teacher_id,
            teacher_name=data.get('teacher_name', ''),
            class_name=data.get('class_name', ''),
            student_count=data.get('student_count', 0),
            note=data.get('note', ''),
        )
        
        return schedule

    @transaction.atomic
    def update_schedule(self, requester, schedule_id: int, data: dict) -> Schedule:
        try:
            schedule = Schedule.objects.select_related('laboratory').get(
                id=schedule_id, is_deleted=False
            )
        except Schedule.DoesNotExist:
            raise NotFoundError('课表不存在')
        
        if not self._can_edit_schedule(requester, schedule):
            raise PermissionDenied('无权限修改该课表')
        
        target_laboratory_id = data.get('laboratory_id') or data.get('laboratory', schedule.laboratory_id)
        if target_laboratory_id != schedule.laboratory_id:
            try:
                target_lab = Laboratory.objects.get(id=target_laboratory_id, is_deleted=False)
                if not self._can_manage_schedule(requester, target_lab):
                    target_laboratory_id = schedule.laboratory_id
            except Laboratory.DoesNotExist:
                raise ValidationError('指定的实训室不存在')
        
        weekday = data.get('weekday', schedule.weekday)
        time_slot = data.get('time_slot', schedule.time_slot)
        weeks = data.get('weeks', schedule.weeks)
        
        if any(k in data for k in ['weekday', 'time_slot', 'weeks', 'laboratory_id', 'laboratory']):
            has_conflict, conflicts = ConflictChecker.check_laboratory_conflict(
                laboratory_id=target_laboratory_id,
                weekday=weekday,
                time_slot=time_slot,
                weeks=weeks,
                exclude_schedule_id=schedule.id
            )
            
            if has_conflict:
                raise ScheduleConflictError(
                    message='课表时间冲突',
                    data={'conflicts': conflicts}
                )
        
        if 'course_name' in data:
            course_name = data['course_name'].strip()
            if not course_name:
                raise ValidationError('课程名称不能为空')
            schedule.course_name = course_name
        
        for field in ['course_code', 'weekday', 'time_slot', 'weeks',
                      'teacher_id', 'teacher_name', 'class_name', 
                      'student_count', 'note']:
            if field in data:
                setattr(schedule, field, data[field])
        
        if 'laboratory_id' in data or 'laboratory' in data:
            schedule.laboratory_id = target_laboratory_id
        
        schedule.save()
        return schedule

    @transaction.atomic
    def delete_schedule(self, requester, schedule_id: int) -> bool:
        try:
            schedule = Schedule.objects.select_related('laboratory').get(
                id=schedule_id, is_deleted=False
            )
        except Schedule.DoesNotExist:
            raise NotFoundError('课表不存在')
        
        if not self._can_delete_schedule(requester, schedule):
            raise PermissionDenied('无权限删除该课表')
        
        if schedule.is_archived:
            schedule.is_deleted = True
            schedule.save(update_fields=['is_deleted'])
        else:
            schedule.delete()
        return True

    @transaction.atomic
    def batch_delete_schedules(self, requester, schedule_ids: list) -> dict:
        deleted_count = 0
        failed_list = []
        
        for schedule_id in schedule_ids:
            try:
                self.delete_schedule(requester, schedule_id)
                deleted_count += 1
            except Exception as e:
                failed_list.append({'id': schedule_id, 'reason': str(e)})
        
        return {
            'deleted_count': deleted_count,
            'failed_count': len(failed_list),
            'failed_list': failed_list,
        }

    def check_conflict(
        self,
        laboratory_id: int,
        weekday: int,
        time_slot: str,
        weeks: str,
        exclude_id: int = None
    ) -> dict:
        has_conflict, conflicts = ConflictChecker.check_laboratory_conflict(
            laboratory_id=laboratory_id,
            weekday=weekday,
            time_slot=time_slot,
            weeks=weeks,
            exclude_schedule_id=exclude_id
        )
        
        return {
            'has_conflict': has_conflict,
            'conflicts': conflicts
        }

    def get_form_options(self, requester, laboratory_id: int = None) -> dict:
        current_semester = Semester.get_current()
        if not current_semester:
            raise ValidationError('未设置当前学期')
        
        if requester.is_super_admin:
            laboratories = Laboratory.objects.filter(
                is_deleted=False, is_available=True
            ).values('id', 'name', 'code')
            teachers = User.objects.annotate(
                role_bitand=models.ExpressionWrapper(
                    models.F('role').bitand(1),
                    output_field=models.IntegerField()
                )
            ).filter(
                role_bitand__gt=0,
                is_active=True,
                is_deleted=False
            ).values('id', 'username', 'nickname')
        elif requester.is_department_admin:
            laboratories = Laboratory.objects.filter(
                department_id=requester.department_id,
                is_deleted=False,
                is_available=True
            ).values('id', 'name', 'code')
            teachers = User.objects.annotate(
                role_bitand=models.ExpressionWrapper(
                    models.F('role').bitand(1),
                    output_field=models.IntegerField()
                )
            ).filter(
                department_id=requester.department_id,
                role_bitand__gt=0,
                is_active=True,
                is_deleted=False
            ).values('id', 'username', 'nickname')
        elif requester.is_laboratory_admin:
            laboratories = Laboratory.objects.filter(
                admin=requester,
                is_deleted=False,
                is_available=True
            ).values('id', 'name', 'code')
            teachers = User.objects.annotate(
                role_bitand=models.ExpressionWrapper(
                    models.F('role').bitand(1),
                    output_field=models.IntegerField()
                )
            ).filter(
                role_bitand__gt=0,
                is_active=True,
                is_deleted=False
            ).values('id', 'username', 'nickname')
        else:
            raise PermissionDenied('无权限获取选项')
        
        current_laboratory = None
        if laboratory_id:
            try:
                lab = Laboratory.objects.get(id=laboratory_id, is_deleted=False)
                if self._can_view_laboratory(requester, lab):
                    current_laboratory = {
                        'id': lab.id,
                        'name': lab.name,
                        'code': lab.code
                    }
            except Laboratory.DoesNotExist:
                pass
        
        weekday_choices = [
            {'value': 1, 'label': '周一'},
            {'value': 2, 'label': '周二'},
            {'value': 3, 'label': '周三'},
            {'value': 4, 'label': '周四'},
            {'value': 5, 'label': '周五'},
            {'value': 6, 'label': '周六'},
            {'value': 7, 'label': '周日'},
        ]
        
        return {
            'laboratories': list(laboratories),
            'teachers': list(teachers),
            'current_laboratory': current_laboratory,
            'weekday_choices': weekday_choices,
            'current_semester': {
                'id': current_semester.id,
                'name': current_semester.name
            }
        }

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

    def _can_view_schedule(self, user, schedule: Schedule) -> bool:
        if user.is_super_admin:
            return True
        if user.is_department_admin:
            return schedule.laboratory.department_id == user.department_id
        if user.is_laboratory_admin:
            return schedule.laboratory.admin_id == user.id
        if user.is_teacher:
            return schedule.teacher_id == user.id
        return False

    def _can_manage_schedule(self, user, laboratory: Laboratory) -> bool:
        if user.is_super_admin:
            return True
        if user.is_department_admin:
            return laboratory.department_id == user.department_id
        if user.is_laboratory_admin:
            return laboratory.admin_id == user.id
        return False

    def _can_edit_schedule(self, user, schedule: Schedule) -> bool:
        if user.is_super_admin:
            return True
        if user.is_department_admin:
            return schedule.laboratory.department_id == user.department_id
        if user.is_laboratory_admin:
            return schedule.laboratory.admin_id == user.id
        if user.is_teacher:
            return schedule.teacher_id == user.id
        return False

    def _can_delete_schedule(self, user, schedule: Schedule) -> bool:
        if user.is_super_admin:
            return True
        if user.is_department_admin:
            return schedule.laboratory.department_id == user.department_id
        if user.is_laboratory_admin:
            return schedule.laboratory.admin_id == user.id
        return False

    def _can_view_laboratory(self, user, laboratory: Laboratory) -> bool:
        if user.is_super_admin:
            return True
        if user.is_department_admin:
            return laboratory.department_id == user.department_id
        if user.is_laboratory_admin:
            return laboratory.admin_id == user.id
        return False

    def _format_schedule(self, schedule: Schedule) -> dict:
        weekday_map = {1: '周一', 2: '周二', 3: '周三', 4: '周四', 5: '周五', 6: '周六', 7: '周日'}
        
        return {
            'id': schedule.id,
            'course_name': schedule.course_name,
            'course_code': schedule.course_code,
            'weekday': schedule.weekday,
            'weekday_display': weekday_map.get(schedule.weekday, f"周{schedule.weekday}"),
            'time_slot': schedule.time_slot,
            'weeks': schedule.weeks,
            'laboratory_id': schedule.laboratory_id,
            'laboratory_name': schedule.laboratory.name,
            'laboratory_code': schedule.laboratory.code,
            'teacher_id': schedule.teacher_id,
            'teacher_name': schedule.teacher_name or (
                schedule.teacher.nickname if schedule.teacher else ''
            ),
            'class_name': schedule.class_name,
            'student_count': schedule.student_count,
            'semester_id': schedule.semester_id,
            'semester_name': schedule.semester.name,
            'note': schedule.note,
            'created_at': schedule.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        }

    def _format_schedule_detail(self, schedule: Schedule, requester=None) -> dict:
        schedule_data = self._format_schedule(schedule)
        schedule_data.update({
            'updated_at': schedule.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
        })
        
        if requester:
            try:
                form_options = self.get_form_options(requester, schedule.laboratory_id)
                return {
                    'class': schedule_data,
                    'teachers': form_options.get('teachers', []),
                    'laboratories': form_options.get('laboratories', []),
                    'weekday_choices': form_options.get('weekday_choices', []),
                    'current_semester': form_options.get('current_semester'),
                    'header': '编辑课表'
                }
            except Exception as e:
                weekday_choices = [
                    {'value': 1, 'label': '周一'},
                    {'value': 2, 'label': '周二'},
                    {'value': 3, 'label': '周三'},
                    {'value': 4, 'label': '周四'},
                    {'value': 5, 'label': '周五'},
                    {'value': 6, 'label': '周六'},
                    {'value': 7, 'label': '周日'},
                ]
                return {
                    'class': schedule_data,
                    'teachers': [],
                    'laboratories': [],
                    'weekday_choices': weekday_choices,
                    'current_semester': None,
                    'header': '编辑课表',
                    'warning': f'获取选项数据失败: {str(e)}'
                }
        
        return schedule_data
