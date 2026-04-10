"""
AI助手服务
"""

import re
import uuid
import logging
from django.core.cache import cache
from apps.core.exceptions import ValidationError
from apps.laboratories.models import Laboratory
from apps.users.models import User, Department

logger = logging.getLogger(__name__)


class AIAssistantService:
    """AI助手服务 - 基于规则的意图识别"""

    INTENT_PATTERNS = {
        'add': [r'添加|新增|创建|增加|加入|新建|建立'],
        'query': [r'查询|查看|显示|列出|获取|找|搜索|有多少|统计'],
        'update': [r'修改|更新|编辑|更改|变更'],
        'delete': [r'删除|移除|注销|去掉'],
    }

    ENTITY_PATTERNS = {
        'laboratory': [r'实训室|实验室|机房|教室'],
        'user': [r'用户|账号|成员|人员'],
        'equipment': [r'设备|机器|电脑|仪器'],
        'schedule': [r'课表|课程|排课'],
    }

    FIELD_PATTERNS = {
        'laboratory': {
            'name': [r'名称|名字|实训室名称'],
            'code': [r'编号|门牌号|房间号'],
            'capacity': [r'工位数|座位数|容量|人数'],
        },
        'user': {
            'username': [r'用户名|账号|登录名'],
            'nickname': [r'姓名|昵称|名字'],
            'email': [r'邮箱|邮件'],
            'phone': [r'手机|电话|联系方式'],
        },
    }

    REQUIRED_FIELDS = {
        'laboratory': ['name', 'code'],
        'user': ['username', 'nickname'],
    }

    FIELD_LABELS = {
        'laboratory': {
            'name': '实训室名称',
            'code': '实训室编号',
            'capacity': '工位数',
            'building': '所在楼栋',
            'laboratory_type': '实训室类型',
        },
        'user': {
            'username': '用户名',
            'nickname': '姓名',
            'email': '邮箱',
            'phone': '手机号',
            'role': '角色',
        },
    }

    def process_request(self, user, question: str, session_id: str = None) -> dict:
        context = {}
        if session_id:
            context = cache.get(f'ai_session_{session_id}', {})

        intent_type = self._detect_intent(question)
        target_entity = self._detect_entity(question)

        if context.get('target_entity') and target_entity == 'unknown':
            target_entity = context.get('target_entity')

        params = self._extract_params(question, target_entity)

        if context.get('params'):
            params = {**context.get('params', {}), **params}

        missing_fields = self._get_missing_fields(target_entity, params)

        context.update({
            'intent_type': intent_type,
            'target_entity': target_entity,
            'params': params,
            'question': question
        })

        if missing_fields:
            new_session_id = session_id or str(uuid.uuid4())
            cache.set(f'ai_session_{new_session_id}', context, timeout=3600)

            return {
                'success': True,
                'intent_type': intent_type,
                'target_entity': target_entity,
                'params': params,
                'requires_more_info': True,
                'missing_fields': missing_fields,
                'session_id': new_session_id,
                'message': self._build_missing_fields_message(intent_type, target_entity, missing_fields)
            }

        if intent_type in ['add', 'update', 'delete']:
            new_session_id = session_id or str(uuid.uuid4())
            cache.set(f'ai_session_{new_session_id}', context, timeout=3600)

            return {
                'success': True,
                'intent_type': intent_type,
                'target_entity': target_entity,
                'params': params,
                'requires_auth': True,
                'auth_token': new_session_id,
                'message': self._build_confirm_message(intent_type, target_entity, params)
            }

        if intent_type == 'query':
            query_result = self._execute_query(user, target_entity, params)

            return {
                'success': True,
                'intent_type': intent_type,
                'message': query_result['message'],
                'data': query_result.get('data'),
            }

        return {
            'success': False,
            'error': '无法识别您的意图，请换一种方式提问'
        }

    def execute_operation(self, user, auth_token: str) -> dict:
        context = cache.get(f'ai_session_{auth_token}')
        if not context:
            return {
                'success': False,
                'error': '操作已过期，请重新发起请求'
            }

        intent_type = context.get('intent_type')
        target_entity = context.get('target_entity')
        params = context.get('params')

        cache.delete(f'ai_session_{auth_token}')

        if intent_type == 'add':
            result = self._execute_add(user, target_entity, params)
        elif intent_type == 'update':
            result = self._execute_update(user, target_entity, params)
        elif intent_type == 'delete':
            result = self._execute_delete(user, target_entity, params)
        else:
            result = {
                'success': False,
                'error': f'未知的操作类型: {intent_type}'
            }

        return result

    def cancel_operation(self, auth_token: str) -> dict:
        cache.delete(f'ai_session_{auth_token}')
        return {
            'success': True,
            'message': '操作已取消'
        }

    def _detect_intent(self, text: str) -> str:
        for intent, patterns in self.INTENT_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, text):
                    return intent
        return 'query'

    def _detect_entity(self, text: str) -> str:
        for entity, patterns in self.ENTITY_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, text):
                    return entity
        return 'unknown'

    def _extract_params(self, text: str, entity: str) -> dict:
        params = {}

        if entity not in self.FIELD_PATTERNS:
            return params

        field_patterns = self.FIELD_PATTERNS[entity]

        for field, patterns in field_patterns.items():
            for pattern in patterns:
                match = re.search(rf'{pattern}[是为：:]\s*([^\s，。,\n]+)', text)
                if match:
                    params[field] = match.group(1).strip()
                    break

        return params

    def _get_missing_fields(self, entity: str, params: dict) -> list:
        missing = []

        if entity not in self.REQUIRED_FIELDS:
            return missing

        required = self.REQUIRED_FIELDS[entity]
        field_labels = self.FIELD_LABELS.get(entity, {})

        for field in required:
            if field not in params or not params[field]:
                missing.append({
                    'field': field,
                    'label': field_labels.get(field, field),
                    'required': True
                })

        return missing

    def _build_missing_fields_message(self, intent_type: str, target_entity: str, missing_fields: list) -> str:
        entity_label = self._get_entity_label(target_entity)
        action_label = self._get_action_label(intent_type)

        message = f"好的，我理解您想要{action_label}{entity_label}。\n\n请补充以下信息：\n"

        for field in missing_fields:
            message += f"- {field['label']}\n"

        return message

    def _build_confirm_message(self, intent_type: str, target_entity: str, params: dict) -> str:
        entity_label = self._get_entity_label(target_entity)
        action_label = self._get_action_label(intent_type)
        field_labels = self.FIELD_LABELS.get(target_entity, {})

        message = f"确认要{action_label}{entity_label}吗？\n\n参数预览：\n"

        for key, value in params.items():
            label = field_labels.get(key, key)
            message += f"- {label}: {value}\n"

        return message

    def _get_entity_label(self, entity: str) -> str:
        labels = {
            'laboratory': '实训室',
            'user': '用户',
            'equipment': '设备',
            'schedule': '课表'
        }
        return labels.get(entity, entity)

    def _get_action_label(self, intent_type: str) -> str:
        labels = {
            'add': '添加',
            'update': '修改',
            'delete': '删除',
            'query': '查询'
        }
        return labels.get(intent_type, intent_type)

    def _execute_query(self, user, target_entity: str, params: dict) -> dict:
        if target_entity == 'laboratory':
            return self._query_laboratories(user, params)
        elif target_entity == 'user':
            return self._query_users(user, params)
        else:
            return {
                'success': False,
                'error': f'暂不支持查询{self._get_entity_label(target_entity)}'
            }

    def _query_laboratories(self, user, params: dict) -> dict:
        queryset = Laboratory.objects.filter(is_deleted=False)

        if user.is_department_admin and not user.is_super_admin:
            queryset = queryset.filter(department_id=user.department_id)
        elif user.is_laboratory_admin and not user.is_super_admin:
            queryset = queryset.filter(admin=user)

        count = queryset.count()
        total_capacity = queryset.aggregate(total=sum('capacity'))['total'] or 0

        return {
            'success': True,
            'message': f'共有 {count} 个实训室，总工位数 {total_capacity}',
            'data': {
                'count': count,
                'total_capacity': total_capacity,
            }
        }

    def _query_users(self, user, params: dict) -> dict:
        queryset = User.objects.filter(is_deleted=False)

        if user.is_department_admin and not user.is_super_admin:
            queryset = queryset.filter(department_id=user.department_id)

        count = queryset.count()

        return {
            'success': True,
            'message': f'共有 {count} 个用户',
            'data': {
                'count': count,
            }
        }

    def _execute_add(self, user, target_entity: str, params: dict) -> dict:
        if target_entity == 'laboratory':
            return self._add_laboratory(user, params)
        elif target_entity == 'user':
            return self._add_user(user, params)
        else:
            return {
                'success': False,
                'error': f'暂不支持添加{self._get_entity_label(target_entity)}'
            }

    def _add_laboratory(self, user, params: dict) -> dict:
        try:
            if not user.is_department_admin and not user.is_super_admin:
                return {
                    'success': False,
                    'error': '只有管理员可以添加实训室'
                }

            name = params.get('name')
            code = params.get('code')

            if not name or not code:
                return {
                    'success': False,
                    'error': '实训室名称和编号为必填项'
                }

            if Laboratory.objects.filter(code=code).exists():
                return {
                    'success': False,
                    'error': f'实训室编号 {code} 已存在'
                }

            department_id = user.department_id if not user.is_super_admin else None

            laboratory = Laboratory.objects.create(
                name=name,
                code=code,
                capacity=params.get('capacity', 30),
                department_id=department_id,
            )

            return {
                'success': True,
                'message': f'成功添加实训室：{name}（{code}）',
                'data': {
                    'id': laboratory.id,
                    'name': laboratory.name,
                    'code': laboratory.code
                }
            }

        except Exception as e:
            logger.error(f"添加实训室失败: {str(e)}")
            return {
                'success': False,
                'error': f'添加实训室失败: {str(e)}'
            }

    def _add_user(self, user, params: dict) -> dict:
        try:
            if not user.is_department_admin and not user.is_super_admin:
                return {
                    'success': False,
                    'error': '只有管理员可以添加用户'
                }

            username = params.get('username')
            nickname = params.get('nickname')

            if not username or not nickname:
                return {
                    'success': False,
                    'error': '用户名和姓名为必填项'
                }

            if User.objects.filter(username=username).exists():
                return {
                    'success': False,
                    'error': f'用户名 {username} 已存在'
                }

            new_user = User.objects.create_user(
                username=username,
                nickname=nickname,
                email=params.get('email', ''),
                phone=params.get('phone', ''),
            )

            return {
                'success': True,
                'message': f'成功添加用户：{nickname}（{username}）',
                'data': {
                    'id': new_user.id,
                    'username': new_user.username,
                    'nickname': new_user.nickname
                }
            }

        except Exception as e:
            logger.error(f"添加用户失败: {str(e)}")
            return {
                'success': False,
                'error': f'添加用户失败: {str(e)}'
            }

    def _execute_update(self, user, target_entity: str, params: dict) -> dict:
        return {
            'success': False,
            'error': '修改功能暂未实现'
        }

    def _execute_delete(self, user, target_entity: str, params: dict) -> dict:
        return {
            'success': False,
            'error': '删除功能暂未实现'
        }
