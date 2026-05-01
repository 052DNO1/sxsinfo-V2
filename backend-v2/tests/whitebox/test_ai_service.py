import pytest
from unittest.mock import patch, MagicMock
from django.core.cache import cache
from apps.ai_assistant.services.ai_service import AIService


@pytest.fixture(autouse=True)
def clear_cache():
    cache.clear()
    yield
    cache.clear()


@pytest.fixture
def ai_service():
    return AIService()


class TestAIDetectIntent:
    def test_detect_query_intent(self, ai_service):
        assert ai_service._detect_intent('查询所有实训室') == 'query'
        assert ai_service._detect_intent('查看用户列表') == 'query'
        assert ai_service._detect_intent('显示课表') == 'query'
        assert ai_service._detect_intent('有多少设备') == 'query'

    def test_detect_add_intent(self, ai_service):
        assert ai_service._detect_intent('添加实训室') == 'add'
        assert ai_service._detect_intent('新增用户') == 'add'
        assert ai_service._detect_intent('创建课表') == 'add'

    def test_detect_update_intent(self, ai_service):
        assert ai_service._detect_intent('修改实训室') == 'update'
        assert ai_service._detect_intent('更新用户信息') == 'update'
        assert ai_service._detect_intent('编辑设备') == 'update'

    def test_detect_delete_intent(self, ai_service):
        assert ai_service._detect_intent('删除用户') == 'delete'
        assert ai_service._detect_intent('移除设备') == 'delete'

    def test_detect_default_query(self, ai_service):
        assert ai_service._detect_intent('你好') == 'query'
        assert ai_service._detect_intent('随便说点什么') == 'query'


class TestAIDetectEntity:
    def test_detect_laboratory(self, ai_service):
        assert ai_service._detect_entity('实训室信息') == 'laboratory'
        assert ai_service._detect_entity('实验室列表') == 'laboratory'
        assert ai_service._detect_entity('机房') == 'laboratory'

    def test_detect_user(self, ai_service):
        assert ai_service._detect_entity('用户管理') == 'user'
        assert ai_service._detect_entity('账号列表') == 'user'

    def test_detect_equipment(self, ai_service):
        assert ai_service._detect_entity('设备信息') == 'equipment'
        assert ai_service._detect_entity('电脑列表') == 'equipment'

    def test_detect_schedule(self, ai_service):
        assert ai_service._detect_entity('课表查询') == 'schedule'
        assert ai_service._detect_entity('课程安排') == 'schedule'

    def test_detect_unknown(self, ai_service):
        assert ai_service._detect_entity('随便说说') == 'unknown'


class TestAIProcessDelete:
    def test_delete_intent_blocked(self, db, ai_service, wb_teacher):
        result = ai_service.process(wb_teacher, '删除用户test')
        assert result['success'] is False
        assert '删除' in result['message'] or '暂未开放' in result['message']


class TestAIProcessQuery:
    def test_query_laboratories(self, db, ai_service, wb_super_admin, wb_laboratory):
        result = ai_service.process(wb_super_admin, '查询所有实训室')
        assert result['success'] is True
        assert '实训室' in result['message']

    def test_query_users(self, db, ai_service, wb_super_admin, wb_teacher):
        result = ai_service.process(wb_super_admin, '查看用户')
        assert result['success'] is True

    def test_query_equipment(self, db, ai_service, wb_super_admin, wb_equipment):
        result = ai_service.process(wb_super_admin, '查询设备')
        assert result['success'] is True

    def test_query_schedule(self, db, ai_service, wb_super_admin, wb_schedule):
        result = ai_service.process(wb_super_admin, '查看课表')
        assert result['success'] is True

    def test_query_unknown_entity(self, db, ai_service, wb_super_admin):
        result = ai_service.process(wb_super_admin, '查询天气')
        assert result['success'] is True
        assert '明确查询对象' in result['message']


class TestAIProcessAdd:
    def test_add_with_missing_fields(self, db, ai_service, wb_super_admin):
        result = ai_service.process(wb_super_admin, '添加实训室')
        assert result['success'] is True
        assert result.get('requires_more') is True
        assert 'session_id' in result

    def test_add_with_all_fields(self, db, ai_service, wb_super_admin):
        result = ai_service.process(wb_super_admin, '添加实训室 名称：测试实训室 编号：TEST001')
        assert result['success'] is True
        assert result.get('requires_confirm') is True
        assert 'token' in result


class TestAIExtractParams:
    def test_extract_username(self, ai_service):
        params = ai_service._extract_params('用户名：zhangsan', 'user')
        assert params.get('username') == 'zhangsan'

    def test_extract_nickname(self, ai_service):
        params = ai_service._extract_params('姓名：张三', 'user')
        assert params.get('nickname') == '张三'

    def test_extract_phone(self, ai_service):
        params = ai_service._extract_params('手机：13800138000', 'user')
        assert params.get('phone') == '13800138000'

    def test_extract_email(self, ai_service):
        params = ai_service._extract_params('邮箱：test@example.com', 'user')
        assert params.get('email') == 'test@example.com'

    def test_extract_capacity(self, ai_service):
        params = ai_service._extract_params('工位数：40', 'laboratory')
        assert params.get('capacity') == '40'

    def test_extract_code(self, ai_service):
        params = ai_service._extract_params('编号：LAB001', 'laboratory')
        assert params.get('code') == 'LAB001'

    def test_extract_course_name(self, ai_service):
        params = ai_service._extract_params('课程名称：高等数学', 'schedule')
        assert params.get('course_name') == '高等数学'

    def test_extract_weekday_chinese(self, ai_service):
        params = ai_service._extract_params('星期：三', 'schedule')
        assert params.get('weekday') == '三'

    def test_extract_weekday_number(self, ai_service):
        params = ai_service._extract_params('星期：3', 'schedule')
        assert params.get('weekday') == '3'

    def test_extract_two_word_user(self, ai_service):
        params = ai_service._extract_params('zhangsan 张三', 'user')
        assert params.get('username') == 'zhangsan'
        assert params.get('nickname') == '张三'

    def test_extract_two_word_lab(self, ai_service):
        params = ai_service._extract_params('LAB001 测试实训室', 'laboratory')
        assert params.get('code') == 'LAB001'
        assert params.get('name') == '测试实训室'

    def test_extract_empty_text(self, ai_service):
        params = ai_service._extract_params('', 'user')
        assert params == {}


class TestAICheckMissing:
    def test_missing_required_user_add(self, ai_service):
        missing = ai_service._check_missing('add', 'user', {})
        assert '用户名' in missing
        assert '姓名' in missing

    def test_missing_required_lab_add(self, ai_service):
        missing = ai_service._check_missing('add', 'laboratory', {})
        assert '实训室名称' in missing
        assert '编号' in missing

    def test_no_missing_with_all_fields(self, ai_service):
        missing = ai_service._check_missing('add', 'user', {'username': 'test', 'nickname': '测试'})
        assert missing == []

    def test_missing_update_target(self, ai_service):
        missing = ai_service._check_missing('update', 'user', {})
        assert '要修改的用户' in missing

    def test_unknown_entity_no_missing(self, ai_service):
        missing = ai_service._check_missing('add', 'unknown', {})
        assert missing == []


class TestAIContextManagement:
    def test_save_and_get_context(self, ai_service):
        session_id = 'test_session_123'
        ctx = {'intent': 'add', 'entity': 'user', 'params': {}}
        ai_service._save_context(session_id, ctx)
        retrieved = ai_service._get_context(session_id)
        assert retrieved['intent'] == 'add'
        assert retrieved['entity'] == 'user'

    def test_get_nonexistent_context(self, ai_service):
        ctx = ai_service._get_context('nonexistent')
        assert ctx == {}

    def test_get_context_no_session(self, ai_service):
        ctx = ai_service._get_context(None)
        assert ctx == {}


class TestAIExecute:
    def test_execute_expired_token(self, db, ai_service, wb_super_admin):
        result = ai_service.execute(wb_super_admin, 'nonexistent_token')
        assert result['success'] is False
        assert '过期' in result['message']


class TestAICancel:
    def test_cancel_success(self, ai_service):
        session_id = 'cancel_test_session'
        ctx = {'intent': 'add', 'entity': 'user'}
        ai_service._save_context(session_id, ctx)
        result = ai_service.cancel(session_id)
        assert result['success'] is True
        assert ai_service._get_context(session_id) == {}

    def test_cancel_nonexistent(self, ai_service):
        result = ai_service.cancel('nonexistent')
        assert result['success'] is True


class TestAIMultiTurnDialog:
    def test_continue_operation_with_missing_fields(self, db, ai_service, wb_super_admin):
        result1 = ai_service.process(wb_super_admin, '添加实训室')
        assert result1.get('requires_more') is True
        session_id = result1.get('session_id')
        assert session_id is not None

        result2 = ai_service.process(
            wb_super_admin, '名称：测试实训室 编号：TEST002', session_id=session_id
        )
        assert result2.get('requires_confirm') is True or result2.get('requires_more') is True
