"""
AI助手服务 - 完整版
支持：查询、添加、编辑（禁止删除）
"""

import re
import uuid
import logging
from django.core.cache import cache
from django.db.models import Q
from apps.users.models import User, Department
from apps.laboratories.models import Laboratory, Equipment
from apps.schedules.models import Schedule, Semester
from apps.users.services.user_service import UserService
from apps.laboratories.services.laboratory_service import LaboratoryService
from apps.laboratories.services.equipment_service import EquipmentService
from apps.schedules.services.schedule_service import ScheduleService
from apps.core.exceptions import ValidationError as CoreValidationError

logger = logging.getLogger(__name__)


class AIService:
    """AI助手服务"""

    # 意图关键词
    INTENT_KEYWORDS = {
        'query': ['查询', '查看', '显示', '列出', '获取', '找', '搜索', '有多少', '统计'],
        'add': ['添加', '新增', '创建', '增加', '加入', '新建', '建立', '录入', '登记'],
        'update': ['修改', '更新', '编辑', '更改', '变更', '改'],
        'delete': ['删除', '移除', '注销', '删掉'],
    }

    # 实体关键词
    ENTITY_KEYWORDS = {
        'laboratory': ['实训室', '实验室', '机房', '教室'],
        'user': ['用户', '账号', '成员', '人员'],
        'equipment': ['设备', '机器', '电脑', '仪器', '计算机'],
        'schedule': ['课表', '课程', '排课', '上课'],
    }

    # 必填字段
    REQUIRED_FIELDS = {
        'user': {'add': ['username', 'nickname'], 'update': ['target']},
        'laboratory': {'add': ['name', 'code'], 'update': ['target']},
        'equipment': {'add': ['name', 'code'], 'update': ['target']},
        'schedule': {'add': ['course_name', 'laboratory', 'weekday'], 'update': ['target']},
    }

    # 可选字段（精简版）
    OPTIONAL_FIELDS = {
        'user': ['phone', 'email', 'department'],
        'laboratory': ['capacity', 'department', 'admin'],
        'equipment': ['laboratory', 'category', 'brand', 'model'],
        'schedule': ['teacher', 'class_name', 'time_slot', 'weeks'],
    }

    # 字段标签
    FIELD_LABELS = {
        'user': {
            'username': '用户名', 'nickname': '姓名', 'phone': '手机号',
            'email': '邮箱', 'department': '部门', 'target': '要修改的用户',
        },
        'laboratory': {
            'name': '实训室名称', 'code': '编号', 'capacity': '工位数',
            'department': '所属部门', 'admin': '管理员', 'target': '要修改的实训室',
            'building': '所在楼宇', 'floor': '所在楼层', 'room_number': '房间号',
        },
        'equipment': {
            'name': '设备名称', 'code': '设备编号', 'laboratory': '所属实训室',
            'category': '类别', 'brand': '品牌', 'model': '型号', 'target': '要修改的设备',
            'position': '位置', 'status': '状态',
        },
        'schedule': {
            'course_name': '课程名称', 'laboratory': '实训室', 'teacher': '教师',
            'class_name': '班级', 'weekday': '星期', 'time_slot': '节次',
            'weeks': '周次', 'target': '要修改的课表',
        },
    }

    def process(self, user, text: str, session_id: str = None) -> dict:
        """处理用户请求"""
        ctx = self._get_context(session_id)

        if ctx:
            return self._continue_operation(user, text, ctx)

        intent = self._detect_intent(text)
        entity = self._detect_entity(text)

        if intent == 'delete':
            return {'success': False, 'message': '⚠️ 目前AI助手暂未开放删除功能，请手动前往管理页面操作。'}

        if intent == 'query':
            return self._execute_query(user, entity, text)

        return self._start_operation(intent, entity, text)

    def execute(self, user, token: str) -> dict:
        """执行已确认的操作"""
        ctx = cache.get(f'ai_ctx_{token}')
        if not ctx:
            return {'success': False, 'message': '操作已过期，请重新发起'}

        cache.delete(f'ai_ctx_{token}')

        intent = ctx['intent']
        entity = ctx['entity']
        params = ctx['params']

        if intent == 'add':
            return self._do_add(user, entity, params)
        elif intent == 'update':
            return self._do_update(user, entity, params)

        return {'success': False, 'message': '未知操作'}

    def cancel(self, token: str) -> dict:
        """取消操作"""
        cache.delete(f'ai_ctx_{token}')
        return {'success': True, 'message': '操作已取消'}

    # ========== 私有方法 ==========

    def _get_context(self, session_id: str) -> dict:
        if not session_id:
            return {}
        return cache.get(f'ai_ctx_{session_id}', {})

    def _save_context(self, session_id: str, ctx: dict):
        cache.set(f'ai_ctx_{session_id}', ctx, timeout=1800)

    def _detect_intent(self, text: str) -> str:
        for intent, keywords in self.INTENT_KEYWORDS.items():
            for kw in keywords:
                if kw in text:
                    return intent
        return 'query'

    def _detect_entity(self, text: str) -> str:
        for entity, keywords in self.ENTITY_KEYWORDS.items():
            for kw in keywords:
                if kw in text:
                    return entity
        return 'unknown'

    def _extract_params(self, text: str, entity: str) -> dict:
        """提取参数"""
        params = {}

        admin_kw = r'(?:管理员|负责人|实训室管理员)'
        keyword_patterns = {
            'username': r'(?:用户名|账号)[是为：:\s]*([^\s，。,\n]+)',
            'nickname': r'(?:姓名|名字)[是为：:\s]*([^\s，。,\n]+)',
            'phone': r'(?:手机|电话)[是为：:\s]*([^\s，。,\n]+)',
            'email': r'(?:邮箱)[是为：:\s]*([^\s，。,\n]+)',
            'department': r'(?:部门|所属部门|分院)[是为：:\s]*([^\s，。,\n]+)',
            'name': r'(?:名称|名字)[是为：:\s]*([^\s，。,\n]+)',
            'code': r'(?:编号|门牌号)[是为：:\s]*([^\s，。,\n]+)',
            'capacity': r'(?:工位数|座位数)[是为：:\s]*(\d+)',
            'admin': rf'{admin_kw}[是为：:\s]*([^\s，。,\n]+)',
            'laboratory': r'(?:实训室|实验室)[是为：:\s]*([^\s，。,\n]+)',
            'category': r'(?:类别|类型)[是为：:\s]*([^\s，。,\n]+)',
            'brand': r'(?:品牌)[是为：:\s]*([^\s，。,\n]+)',
            'model': r'(?:型号)[是为：:\s]*([^\s，。,\n]+)',
            'course_name': r'(?:课程名称|课程)[是为：:\s]*([^\s，。,\n]+)',
            'teacher': r'(?:教师|老师|任课教师)[是为：:\s]*([^\s，。,\n]+)',
            'class_name': r'(?:班级)[是为：:\s]*([^\s，。,\n]+)',
            'weekday': r'(?:星期|周)[是为：:\s]*([一二三四五六日\d]+)',
            'time_slot': r'(?:节次)[是为：:\s]*([^\s，。,\n]+)',
            'weeks': r'(?:周次)[是为：:\s]*([^\s，。,\n]+)',
            'building': r'(?:楼宇|所在楼宇|楼栋)[是为：:\s]*([^\s，。,\n]+)',
            'floor': r'(?:楼层|所在楼层)[是为：:\s]*(\d+)',
            'room_number': r'(?:房间号)[是为：:\s]*([^\s，。,\n]+)',
            'position': r'(?:位置)[是为：:\s]*([^\s，。,\n]+)',
            'status': r'(?:状态)[是为：:\s]*([^\s，。,\n]+)',
        }

        for field, pattern in keyword_patterns.items():
            match = re.search(pattern, text)
            if match:
                params[field] = match.group(1).strip()

        simple = re.findall(r'(\w+)[是为：:\s]+([^\s，。,\n]+)', text)
        key_map = {
            '用户名': 'username', '账号': 'username',
            '姓名': 'nickname', '名字': 'nickname',
            '手机': 'phone', '电话': 'phone',
            '邮箱': 'email',
            '部门': 'department', '所属部门': 'department',
            '名称': 'name', '编号': 'code', '门牌号': 'code',
            '工位数': 'capacity', '管理员': 'admin', '负责人': 'admin', '实训室管理员': 'admin',
            '实训室': 'laboratory', '实验室': 'laboratory', '归属于': 'laboratory', '所属实训室': 'laboratory',
            '类别': 'category', '类型': 'category',
            '品牌': 'brand', '型号': 'model',
            '课程': 'course_name', '课程名称': 'course_name',
            '教师': 'teacher', '老师': 'teacher', '任课教师': 'teacher',
            '班级': 'class_name',
            '星期': 'weekday', '节次': 'time_slot', '周次': 'weeks',
            '楼宇': 'building', '楼层': 'floor', '房间号': 'room_number',
            '位置': 'position', '状态': 'status',
        }
        for key, value in simple:
            if key in key_map:
                params[key_map[key]] = value

        words = text.split()
        if len(words) >= 2:
            if entity == 'user' and not params.get('username') and not params.get('target'):
                if re.match(r'^[a-zA-Z][a-zA-Z0-9_]*$', words[0]):
                    params['username'] = words[0]
                    params['nickname'] = words[1]
                elif re.match(r'^[a-zA-Z][a-zA-Z0-9_]*$', words[1]):
                    params['nickname'] = words[0]
                    params['username'] = words[1]

            elif entity == 'laboratory' and not params.get('name') and not params.get('target'):
                if re.match(r'^[a-zA-Z0-9]+$', words[0]):
                    params['code'] = words[0]
                    params['name'] = ' '.join(words[1:])
                elif re.match(r'^[a-zA-Z0-9]+$', words[1]):
                    params['name'] = words[0]
                    params['code'] = words[1]

            elif entity == 'equipment' and not params.get('name'):
                if re.match(r'^[a-zA-Z][a-zA-Z0-9-]*$', words[0]):
                    params['code'] = words[0]
                    params['name'] = ' '.join(words[1:])
                elif re.match(r'^[a-zA-Z][a-zA-Z0-9-]*$', words[1]):
                    params['name'] = words[0]
                    params['code'] = words[1]

        if entity in ['user', 'laboratory', 'equipment', 'schedule']:
            target_match = re.search(
                rf'(?:编辑|修改|更新)(?:{entity}|{"用户" if entity == "user" else "实训室" if entity == "laboratory" else "设备" if entity == "equipment" else "课表"})\s+(.{2,30}?)(?:\s+(?:管理员|手机|电话|邮箱|部门|名称|工位数|楼宇|楼层|房间号|类别|品牌|型号|位置|状态|课程|教师|班级|星期|节次|周次|归属于)|$)',
                text
            )
            if target_match:
                potential_target = target_match.group(1).strip()
                if potential_target and potential_target not in ['user', 'laboratory', 'equipment', 'schedule']:
                    params['target'] = potential_target

        return params

    def _continue_operation(self, user, text: str, ctx: dict) -> dict:
        """继续之前的操作"""
        intent = ctx['intent']
        entity = ctx['entity']
        params = ctx.get('params', {})

        new_params = self._extract_params(text, entity)
        params.update(new_params)

        missing = self._check_missing(intent, entity, params)

        if missing:
            ctx['params'] = params
            self._save_context(ctx['session_id'], ctx)
            return self._build_missing_response(missing, entity)

        ctx['params'] = params
        self._save_context(ctx['session_id'], ctx)

        return {
            'success': True,
            'requires_confirm': True,
            'message': self._build_confirm_msg(intent, entity, params),
            'token': ctx['session_id'],
        }

    def _start_operation(self, intent: str, entity: str, text: str) -> dict:
        """开始新操作"""
        params = self._extract_params(text, entity)
        missing = self._check_missing(intent, entity, params)

        if missing:
            session_id = str(uuid.uuid4())
            ctx = {
                'session_id': session_id,
                'intent': intent,
                'entity': entity,
                'params': params,
            }
            self._save_context(session_id, ctx)
            return self._build_missing_response(missing, entity, session_id)

        session_id = str(uuid.uuid4())
        ctx = {
            'session_id': session_id,
            'intent': intent,
            'entity': entity,
            'params': params,
        }
        self._save_context(session_id, ctx)

        return {
            'success': True,
            'requires_confirm': True,
            'message': self._build_confirm_msg(intent, entity, params),
            'token': session_id,
        }

    def _build_missing_response(self, missing: list, entity: str, session_id: str = None) -> dict:
        """构建缺失字段响应"""
        message = '请补充以下信息：\n\n【必填项】\n'
        for field in missing:
            message += f'• {field}\n'

        optional = self.OPTIONAL_FIELDS.get(entity, [])
        if optional:
            labels = self.FIELD_LABELS.get(entity, {})
            message += '\n【可选项】\n'
            for field in optional:
                label = labels.get(field, field)
                message += f'• {label}\n'

        response = {
            'success': True,
            'requires_more': True,
            'message': message,
            'missing_fields': missing,
        }
        if session_id:
            response['session_id'] = session_id

        return response

    def _check_missing(self, intent: str, entity: str, params: dict) -> list:
        """检查缺失字段"""
        if entity not in self.REQUIRED_FIELDS:
            return []

        required = self.REQUIRED_FIELDS[entity].get(intent, [])
        missing = []
        labels = self.FIELD_LABELS.get(entity, {})

        for field in required:
            if not params.get(field):
                missing.append(labels.get(field, field))

        return missing

    def _build_confirm_msg(self, intent: str, entity: str, params: dict) -> str:
        """构建确认消息"""
        action = '添加' if intent == 'add' else '修改'
        labels = self.FIELD_LABELS.get(entity, {})

        msg = f'⚠️ 即将{action}，请确认：\n\n'

        if intent == 'update' and entity == 'laboratory' and params.get('target'):
            current = self._get_current_lab_info(params['target'])
            if current:
                msg += f'【当前信息】\n'
                msg += f'• 实训室：{current.get("name", "")}\n'
                msg += f'• 编号：{current.get("code", "")}\n'
                msg += f'• 当前管理员：{current.get("admin", "未设置")}\n'
                msg += '\n'

        elif intent == 'update' and entity == 'user' and params.get('target'):
            current = self._get_current_user_info(params['target'])
            if current:
                msg += f'【当前信息】\n'
                msg += f'• 用户：{current.get("nickname", "")}（{current.get("username", "")}）\n'
                msg += f'• 手机号：{current.get("phone", "未设置")}\n'
                msg += f'• 部门：{current.get("department", "未分配")}\n'
                msg += '\n'

        elif intent == 'update' and entity == 'equipment' and params.get('target'):
            current = self._get_current_equipment_info(params['target'])
            if current:
                msg += f'【当前信息】\n'
                msg += f'• 设备：{current.get("name", "")}（{current.get("code", "")}）\n'
                msg += f'• 所属实训室：{current.get("laboratory", "未分配")}\n'
                msg += f'• 类别：{current.get("category", "未设置")}\n'
                msg += '\n'

        elif intent == 'update' and entity == 'schedule' and params.get('target'):
            current = self._get_current_schedule_info(params['target'])
            if current:
                msg += f'【当前信息】\n'
                msg += f'• 课程：{current.get("course_name", "")}\n'
                msg += f'• 实训室：{current.get("laboratory", "未设置")}\n'
                msg += f'• 教师：{current.get("teacher", "未设置")}\n'
                msg += '\n'

        msg += '【修改内容】\n'
        for key, value in params.items():
            if value and key not in ['target']:
                label = labels.get(key, key)
                msg += f'• {label}: {value}\n'
        msg += '\n✅ 点击确认执行'

        return msg

    def _get_current_lab_info(self, target: str) -> dict:
        """获取实训室当前信息"""
        lab = Laboratory.objects.filter(
            Q(name__icontains=target) | Q(code__icontains=target),
            is_deleted=False
        ).first()
        if lab:
            return {
                'name': lab.name,
                'code': lab.code,
                'admin': lab.admin.nickname if lab.admin else '未设置',
            }
        return None

    def _get_current_user_info(self, target: str) -> dict:
        """获取用户当前信息"""
        user = User.objects.filter(
            Q(username__icontains=target) | Q(nickname__icontains=target),
            is_deleted=False
        ).first()
        if user:
            return {
                'username': user.username,
                'nickname': user.nickname,
                'phone': user.phone or '未设置',
                'department': user.department.name if user.department else '未分配',
            }
        return None

    def _get_current_equipment_info(self, target: str) -> dict:
        """获取设备当前信息"""
        equipment = Equipment.objects.filter(
            Q(name__icontains=target) | Q(code__icontains=target),
            is_deleted=False
        ).first()
        if equipment:
            return {
                'name': equipment.name,
                'code': equipment.code,
                'laboratory': equipment.laboratory.name if equipment.laboratory else '未分配',
                'category': equipment.category or '未设置',
            }
        return None

    def _get_current_schedule_info(self, target: str) -> dict:
        """获取课表当前信息"""
        schedule = Schedule.objects.filter(
            Q(course_name__icontains=target),
            is_deleted=False
        ).first()
        if schedule:
            return {
                'course_name': schedule.course_name,
                'laboratory': schedule.laboratory.name if schedule.laboratory else '未设置',
                'teacher': schedule.teacher_name or '未设置',
            }
        return None

    # ========== 查询操作 ==========

    def _execute_query(self, user, entity: str, text: str) -> dict:
        """执行查询"""
        if entity == 'laboratory':
            return self._query_labs(user)
        elif entity == 'user':
            return self._query_users(user)
        elif entity == 'equipment':
            return self._query_equipment(user)
        elif entity == 'schedule':
            return self._query_schedule(user)
        else:
            return {
                'success': True,
                'message': '请明确查询对象，例如：查询所有实训室',
                'data': [],
            }

    def _query_labs(self, user) -> dict:
        """查询实训室"""
        try:
            queryset = Laboratory.objects.filter(is_deleted=False)

            if not user.is_super_admin:
                if user.is_department_admin:
                    queryset = queryset.filter(department_id=user.department_id)
                elif user.is_laboratory_admin:
                    queryset = queryset.filter(admin_id=user.id)
                else:
                    queryset = queryset.filter(department_id=user.department_id)

            labs = list(queryset.order_by('code'))

            if not labs:
                return {'success': True, 'message': '暂无实训室数据', 'data': []}

            total_count = len(labs)
            total_capacity = sum(lab.capacity for lab in labs)

            if user.is_super_admin:
                message = f'系统共有 {total_count} 个实训室，总工位数 {total_capacity} 个。\n\n'
            elif user.is_department_admin:
                dept_name = user.department.name if user.department else '本分院'
                message = f'{dept_name}共有 {total_count} 个实训室，总工位数 {total_capacity} 个。\n\n'
            else:
                message = f'当前共有 {total_count} 个实训室，总工位数 {total_capacity} 个。\n\n'

            if total_count <= 10:
                for lab in labs:
                    message += f'• {lab.name}（{lab.code}）- 工位{lab.capacity}\n'
            else:
                for lab in labs[:10]:
                    message += f'• {lab.name}（{lab.code}）- 工位{lab.capacity}\n'
                message += f'...还有 {total_count - 10} 个\n'

            return {'success': True, 'message': message.strip(), 'data': []}

        except Exception as e:
            logger.error(f'查询实训室失败: {e}')
            return {'success': False, 'message': f'查询失败: {e}', 'data': []}

    def _query_users(self, user) -> dict:
        """查询用户"""
        try:
            queryset = User.objects.filter(is_deleted=False)

            if not user.is_super_admin:
                if user.is_department_admin:
                    queryset = queryset.filter(department_id=user.department_id)
                else:
                    queryset = queryset.filter(id=user.id)

            users = list(queryset.order_by('-created_at')[:50])

            if not users:
                return {'success': True, 'message': '暂无用户数据', 'data': []}

            total_count = len(users)

            if user.is_super_admin:
                message = f'系统共有 {total_count} 个用户。\n\n'
            elif user.is_department_admin:
                dept_name = user.department.name if user.department else '本分院'
                message = f'{dept_name}共有 {total_count} 个用户。\n\n'
            else:
                message = f'当前用户信息：\n'
                message += f'• 用户名：{user.username}\n'
                message += f'• 姓名：{user.nickname}\n'
                message += f'• 部门：{user.department.name if user.department else "未分配"}\n'
                return {'success': True, 'message': message.strip(), 'data': []}

            if total_count <= 10:
                for u in users:
                    dept = u.department.name if u.department else "未分配"
                    message += f'• {u.nickname}（{u.username}）- {dept}\n'
            else:
                for u in users[:10]:
                    dept = u.department.name if u.department else "未分配"
                    message += f'• {u.nickname}（{u.username}）- {dept}\n'
                message += f'...还有 {total_count - 10} 人\n'

            return {'success': True, 'message': message.strip(), 'data': []}

        except Exception as e:
            logger.error(f'查询用户失败: {e}')
            return {'success': False, 'message': f'查询失败: {e}', 'data': []}

    def _query_equipment(self, user) -> dict:
        """查询设备"""
        try:
            queryset = Equipment.objects.filter(is_deleted=False)

            if not user.is_super_admin:
                if user.is_department_admin:
                    queryset = queryset.filter(laboratory__department_id=user.department_id)
                elif user.is_laboratory_admin:
                    queryset = queryset.filter(laboratory__admin=user)

            equipments = list(queryset.order_by('code')[:50])

            if not equipments:
                return {'success': True, 'message': '暂无设备数据', 'data': []}

            total_count = len(equipments)
            message = f'共有 {total_count} 个设备。\n\n'

            if total_count <= 10:
                for e in equipments:
                    lab_name = e.laboratory.name if e.laboratory else "未分配"
                    message += f'• {e.name}（{e.code}）- {lab_name}\n'
            else:
                for e in equipments[:10]:
                    lab_name = e.laboratory.name if e.laboratory else "未分配"
                    message += f'• {e.name}（{e.code}）- {lab_name}\n'
                message += f'...还有 {total_count - 10} 个\n'

            return {'success': True, 'message': message.strip(), 'data': []}

        except Exception as e:
            logger.error(f'查询设备失败: {e}')
            return {'success': False, 'message': f'查询失败: {e}', 'data': []}

    def _query_schedule(self, user) -> dict:
        """查询课表"""
        try:
            queryset = Schedule.objects.filter(is_deleted=False, is_archived=False)

            current_semester = Semester.get_current()
            if current_semester:
                queryset = queryset.filter(semester=current_semester)

            if not user.is_super_admin:
                if user.is_department_admin:
                    queryset = queryset.filter(laboratory__department_id=user.department_id)
                elif user.is_laboratory_admin:
                    queryset = queryset.filter(laboratory__admin=user)
                elif hasattr(user, 'is_teacher') and user.is_teacher:
                    queryset = queryset.filter(teacher=user)

            schedules = list(queryset.order_by('laboratory__code', 'weekday')[:50])

            if not schedules:
                return {'success': True, 'message': '暂无课表数据', 'data': []}

            total_count = len(schedules)
            message = f'共有 {total_count} 条课表记录。\n\n'

            weekday_map = {1: '周一', 2: '周二', 3: '周三', 4: '周四', 5: '周五', 6: '周六', 7: '周日'}

            if total_count <= 10:
                for s in schedules:
                    weekday = weekday_map.get(s.weekday, f'周{s.weekday}')
                    message += f'• {s.course_name} - {s.laboratory.name} {weekday} {s.time_slot}\n'
            else:
                for s in schedules[:10]:
                    weekday = weekday_map.get(s.weekday, f'周{s.weekday}')
                    message += f'• {s.course_name} - {s.laboratory.name} {weekday} {s.time_slot}\n'
                message += f'...还有 {total_count - 10} 条\n'

            return {'success': True, 'message': message.strip(), 'data': []}

        except Exception as e:
            logger.error(f'查询课表失败: {e}')
            return {'success': False, 'message': f'查询失败: {e}', 'data': []}

    # ========== 添加操作 ==========

    def _do_add(self, user, entity: str, params: dict) -> dict:
        """执行添加"""
        if entity == 'user':
            return self._add_user(user, params)
        elif entity == 'laboratory':
            return self._add_lab(user, params)
        elif entity == 'equipment':
            return self._add_equipment(user, params)
        elif entity == 'schedule':
            return self._add_schedule(user, params)
        return {'success': False, 'message': '不支持的操作'}

    def _add_user(self, user, params: dict) -> dict:
        """添加用户"""
        try:
            service = UserService()

            data = {
                'username': params.get('username'),
                'nickname': params.get('nickname'),
                'phone': params.get('phone', ''),
                'email': params.get('email', ''),
                'role': 1,
            }

            department = None
            if params.get('department'):
                department = Department.objects.filter(name__icontains=params['department']).first()
            elif user.department:
                department = user.department

            if department:
                data['department'] = department

            new_user = service.create_user(requester=user, data=data, request=None)

            logger.info(f'{user.username} 通过AI添加用户: {new_user.nickname}')
            return {'success': True, 'message': f'✅ 成功添加用户：{new_user.nickname}（用户名：{new_user.username}）'}

        except CoreValidationError as e:
            logger.warning(f'添加用户验证失败: {str(e)}')
            return {'success': False, 'message': f'❌ {str(e)}'}
        except Exception as e:
            logger.error(f'添加用户失败: {e}', exc_info=True)
            return {'success': False, 'message': f'添加失败: {str(e)}'}

    def _add_lab(self, user, params: dict) -> dict:
        """添加实训室"""
        try:
            service = LaboratoryService()

            data = {
                'name': params.get('name'),
                'code': params.get('code'),
            }

            if params.get('capacity'):
                try:
                    data['capacity'] = int(params['capacity'])
                except ValueError:
                    data['capacity'] = 30

            if params.get('department'):
                dept = Department.objects.filter(name__icontains=params['department']).first()
                if dept:
                    data['department_id'] = dept.id
                else:
                    return {'success': False, 'message': f'未找到部门 "{params["department"]}"'}
            elif user.department:
                data['department_id'] = user.department.id
            else:
                return {'success': False, 'message': '请指定所属部门'}

            if params.get('admin'):
                admin_user = User.objects.filter(
                    Q(nickname__icontains=params['admin']) | Q(username__icontains=params['admin'])
                ).first()
                if admin_user:
                    data['admin'] = admin_user.id
                else:
                    return {'success': False, 'message': f'未找到管理员 "{params["admin"]}"'}

            if params.get('building'):
                data['building'] = params['building']
            if params.get('floor'):
                try:
                    data['floor'] = int(params['floor'])
                except ValueError:
                    pass
            if params.get('room_number'):
                data['room_number'] = params['room_number']

            lab = service.create_laboratory(requester=user, data=data)

            logger.info(f'{user.username} 通过AI添加实训室: {lab.name}')
            return {'success': True, 'message': f'✅ 成功添加实训室：{lab.name}（编号：{lab.code}）'}

        except CoreValidationError as e:
            logger.warning(f'添加实训室验证失败: {str(e)}')
            return {'success': False, 'message': f'❌ {str(e)}'}
        except Exception as e:
            logger.error(f'添加实训室失败: {e}', exc_info=True)
            return {'success': False, 'message': f'添加失败: {str(e)}'}

    def _add_equipment(self, user, params: dict) -> dict:
        """添加设备"""
        try:
            service = EquipmentService()

            data = {
                'name': params.get('name'),
                'code': params.get('code'),
                'category': params.get('category', '计算机'),
                'brand': params.get('brand', ''),
                'model': params.get('model', ''),
            }

            if params.get('laboratory'):
                lab = Laboratory.objects.filter(
                    Q(name__icontains=params['laboratory']) | Q(code__icontains=params['laboratory'])
                ).first()
                if lab:
                    data['laboratory'] = lab
                else:
                    return {'success': False, 'message': f'未找到实训室 "{params["laboratory"]}"'}

            if params.get('position'):
                data['position'] = params['position']

            equipment = service.create_equipment(requester=user, data=data)

            logger.info(f'{user.username} 通过AI添加设备: {equipment.name}')
            return {'success': True, 'message': f'✅ 成功添加设备：{equipment.name}（编号：{equipment.code}）'}

        except CoreValidationError as e:
            logger.warning(f'添加设备验证失败: {str(e)}')
            return {'success': False, 'message': f'❌ {str(e)}'}
        except Exception as e:
            logger.error(f'添加设备失败: {e}', exc_info=True)
            return {'success': False, 'message': f'添加失败: {str(e)}'}

    def _add_schedule(self, user, params: dict) -> dict:
        """添加课表"""
        try:
            service = ScheduleService()

            data = {
                'course_name': params.get('course_name'),
                'time_slot': params.get('time_slot', '1-2'),
                'weeks': params.get('weeks', '1-18'),
            }

            if params.get('laboratory'):
                lab = Laboratory.objects.filter(
                    Q(name__icontains=params['laboratory']) | Q(code__icontains=params['laboratory'])
                ).first()
                if lab:
                    data['laboratory_id'] = lab.id
                else:
                    return {'success': False, 'message': f'未找到实训室 "{params["laboratory"]}"'}

            if params.get('teacher'):
                teacher = User.objects.filter(
                    Q(nickname__icontains=params['teacher']) | Q(username__icontains=params['teacher'])
                ).first()
                if teacher:
                    data['teacher_id'] = teacher.id

            if params.get('class_name'):
                data['class_name'] = params['class_name']

            if params.get('weekday'):
                weekday_map = {'一': 1, '二': 2, '三': 3, '四': 4, '五': 5, '六': 6, '日': 7}
                wd = params['weekday']
                if wd in weekday_map:
                    data['weekday'] = weekday_map[wd]
                else:
                    try:
                        data['weekday'] = int(wd)
                    except ValueError:
                        data['weekday'] = 1
            else:
                data['weekday'] = 1

            current_semester = Semester.get_current()
            if current_semester:
                data['semester_id'] = current_semester.id
            else:
                return {'success': False, 'message': '当前没有活跃的学期，请先创建学期'}

            schedule = service.create_schedule(requester=user, data=data)

            logger.info(f'{user.username} 通过AI添加课表: {schedule.course_name}')
            return {'success': True, 'message': f'✅ 成功添加课表：{schedule.course_name}'}

        except CoreValidationError as e:
            logger.warning(f'添加课表验证失败: {str(e)}')
            return {'success': False, 'message': f'❌ {str(e)}'}
        except Exception as e:
            logger.error(f'添加课表失败: {e}', exc_info=True)
            return {'success': False, 'message': f'添加失败: {str(e)}'}

    # ========== 编辑操作 ==========

    def _do_update(self, user, entity: str, params: dict) -> dict:
        """执行修改"""
        if entity == 'user':
            return self._update_user(user, params)
        elif entity == 'laboratory':
            return self._update_lab(user, params)
        elif entity == 'equipment':
            return self._update_equipment(user, params)
        elif entity == 'schedule':
            return self._update_schedule(user, params)
        return {'success': False, 'message': '不支持的操作'}

    def _update_user(self, user, params: dict) -> dict:
        """修改用户"""
        try:
            target = params.get('target')
            if not target:
                return {'success': False, 'message': '请指定要修改的用户'}

            target_user = User.objects.filter(
                Q(username__icontains=target) | Q(nickname__icontains=target),
                is_deleted=False
            ).first()

            if not target_user:
                return {'success': False, 'message': f'未找到用户 "{target}"'}

            updated = []
            if params.get('phone'):
                target_user.phone = params['phone']
                updated.append(f'手机号→{params["phone"]}')
            if params.get('email'):
                target_user.email = params['email']
                updated.append(f'邮箱→{params["email"]}')
            if params.get('nickname'):
                target_user.nickname = params['nickname']
                updated.append(f'姓名→{params["nickname"]}')
            if params.get('department'):
                dept = Department.objects.filter(name__icontains=params['department']).first()
                if dept:
                    target_user.department = dept
                    updated.append(f'部门→{dept.name}')

            if not updated:
                return {'success': False, 'message': '未指定要修改的内容'}

            target_user.save()
            logger.info(f'{user.username} 通过AI修改用户: {target_user.nickname}')

            return {'success': True, 'message': f'✅ 成功修改用户【{target_user.nickname}】，更新了：{"、".join(updated)}'}

        except Exception as e:
            logger.error(f'修改用户失败: {e}', exc_info=True)
            return {'success': False, 'message': f'修改失败: {str(e)}'}

    def _update_lab(self, user, params: dict) -> dict:
        """修改实训室"""
        try:
            target = params.get('target')
            if not target:
                return {'success': False, 'message': '请指定要修改的实训室'}

            lab = Laboratory.objects.filter(
                Q(name__icontains=target) | Q(code__icontains=target),
                is_deleted=False
            ).first()

            if not lab:
                return {'success': False, 'message': f'未找到实训室 "{target}"'}

            updated = []
            if params.get('capacity'):
                try:
                    lab.capacity = int(params['capacity'])
                    updated.append(f'工位数→{params["capacity"]}')
                except ValueError:
                    pass
            if params.get('name'):
                lab.name = params['name']
                updated.append(f'名称→{params["name"]}')
            if params.get('admin'):
                admin_user = User.objects.filter(
                    Q(nickname__icontains=params['admin']) | Q(username__icontains=params['admin'])
                ).first()
                if admin_user:
                    lab.admin = admin_user
                    updated.append(f'管理员→{admin_user.nickname}')
            if params.get('building'):
                lab.building = params['building']
                updated.append(f'楼宇→{params["building"]}')
            if params.get('floor'):
                try:
                    lab.floor = int(params['floor'])
                    updated.append(f'楼层→{params["floor"]}')
                except ValueError:
                    pass
            if params.get('room_number'):
                lab.room_number = params['room_number']
                updated.append(f'房间号→{params["room_number"]}')
            if params.get('department'):
                dept = Department.objects.filter(name__icontains=params['department']).first()
                if dept:
                    lab.department = dept
                    updated.append(f'部门→{dept.name}')

            if not updated:
                return {'success': False, 'message': '未指定要修改的内容'}

            lab.save()
            logger.info(f'{user.username} 通过AI修改实训室: {lab.name}')

            return {'success': True, 'message': f'✅ 成功修改实训室【{lab.name}】，更新了：{"、".join(updated)}'}

        except Exception as e:
            logger.error(f'修改实训室失败: {e}', exc_info=True)
            return {'success': False, 'message': f'修改失败: {str(e)}'}

    def _update_equipment(self, user, params: dict) -> dict:
        """修改设备"""
        try:
            target = params.get('target')
            if not target:
                return {'success': False, 'message': '请指定要修改的设备'}

            equipment = Equipment.objects.filter(
                Q(name__icontains=target) | Q(code__icontains=target),
                is_deleted=False
            ).first()

            if not equipment:
                return {'success': False, 'message': f'未找到设备 "{target}"'}

            updated = []
            if params.get('laboratory'):
                lab = Laboratory.objects.filter(
                    Q(name__icontains=params['laboratory']) | Q(code__icontains=params['laboratory'])
                ).first()
                if lab:
                    equipment.laboratory = lab
                    updated.append(f'所属实训室→{lab.name}')
            if params.get('name'):
                equipment.name = params['name']
                updated.append(f'名称→{params["name"]}')
            if params.get('category'):
                equipment.category = params['category']
                updated.append(f'类别→{params["category"]}')
            if params.get('brand'):
                equipment.brand = params['brand']
                updated.append(f'品牌→{params["brand"]}')
            if params.get('model'):
                equipment.model = params['model']
                updated.append(f'型号→{params["model"]}')
            if params.get('position'):
                equipment.position = params['position']
                updated.append(f'位置→{params["position"]}')
            if params.get('status'):
                equipment.status = params['status']
                updated.append(f'状态→{params["status"]}')

            if not updated:
                return {'success': False, 'message': '未指定要修改的内容'}

            equipment.save()
            logger.info(f'{user.username} 通过AI修改设备: {equipment.name}')

            return {'success': True, 'message': f'✅ 成功修改设备【{equipment.name}】，更新了：{"、".join(updated)}'}

        except Exception as e:
            logger.error(f'修改设备失败: {e}', exc_info=True)
            return {'success': False, 'message': f'修改失败: {str(e)}'}

    def _update_schedule(self, user, params: dict) -> dict:
        """修改课表"""
        try:
            target = params.get('target')
            if not target:
                return {'success': False, 'message': '请指定要修改的课表'}

            schedule = Schedule.objects.filter(
                Q(course_name__icontains=target),
                is_deleted=False
            ).first()

            if not schedule:
                return {'success': False, 'message': f'未找到课表 "{target}"'}

            updated = []
            if params.get('teacher'):
                teacher = User.objects.filter(
                    Q(nickname__icontains=params['teacher']) | Q(username__icontains=params['teacher'])
                ).first()
                if teacher:
                    schedule.teacher = teacher
                    schedule.teacher_name = teacher.nickname
                    updated.append(f'教师→{teacher.nickname}')
            if params.get('laboratory'):
                lab = Laboratory.objects.filter(
                    Q(name__icontains=params['laboratory']) | Q(code__icontains=params['laboratory'])
                ).first()
                if lab:
                    schedule.laboratory = lab
                    updated.append(f'实训室→{lab.name}')
            if params.get('class_name'):
                schedule.class_name = params['class_name']
                updated.append(f'班级→{params["class_name"]}')
            if params.get('weekday'):
                weekday_map = {'一': 1, '二': 2, '三': 3, '四': 4, '五': 5, '六': 6, '日': 7}
                wd = params['weekday']
                if wd in weekday_map:
                    schedule.weekday = weekday_map[wd]
                    weekday_names = {1: '周一', 2: '周二', 3: '周三', 4: '周四', 5: '周五', 6: '周六', 7: '周日'}
                    updated.append(f'星期→{weekday_names.get(schedule.weekday, wd)}')
                else:
                    try:
                        schedule.weekday = int(wd)
                        updated.append(f'星期→周{wd}')
                    except ValueError:
                        pass
            if params.get('time_slot'):
                schedule.time_slot = params['time_slot']
                updated.append(f'节次→{params["time_slot"]}')
            if params.get('weeks'):
                schedule.weeks = params['weeks']
                updated.append(f'周次→{params["weeks"]}')

            if not updated:
                return {'success': False, 'message': '未指定要修改的内容'}

            schedule.save()
            logger.info(f'{user.username} 通过AI修改课表: {schedule.course_name}')

            return {'success': True, 'message': f'✅ 成功修改课表【{schedule.course_name}】，更新了：{"、".join(updated)}'}

        except Exception as e:
            logger.error(f'修改课表失败: {e}', exc_info=True)
            return {'success': False, 'message': f'修改失败: {str(e)}'}
