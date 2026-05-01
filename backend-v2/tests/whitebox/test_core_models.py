import pytest
from django.utils import timezone
from apps.core.models import BaseModel, SoftDeleteModel, TimeStampedModel, SingletonModel, SystemOperationLog
from apps.core.constants import UserRole
from django.contrib.auth import get_user_model

User = get_user_model()


class TestSoftDeleteModel:
    def test_soft_delete_marks_deleted(self, db, wb_teacher):
        wb_teacher.soft_delete(user=None)
        wb_teacher.refresh_from_db()
        assert wb_teacher.is_deleted is True
        assert wb_teacher.deleted_at is not None

    def test_soft_delete_with_user(self, db, wb_teacher, wb_super_admin):
        wb_teacher.soft_delete(user=wb_super_admin)
        wb_teacher.refresh_from_db()
        assert wb_teacher.is_deleted is True
        assert wb_teacher.deleted_by == wb_super_admin

    def test_soft_delete_without_user(self, db, wb_teacher):
        wb_teacher.soft_delete(user=None)
        wb_teacher.refresh_from_db()
        assert wb_teacher.is_deleted is True
        assert wb_teacher.deleted_by is None

    def test_restore(self, db, wb_teacher):
        wb_teacher.soft_delete(user=None)
        wb_teacher.restore()
        wb_teacher.refresh_from_db()
        assert wb_teacher.is_deleted is False
        assert wb_teacher.deleted_at is None
        assert wb_teacher.deleted_by is None

    def test_default_not_deleted(self, db, wb_teacher):
        assert wb_teacher.is_deleted is False
        assert wb_teacher.deleted_at is None
        assert wb_teacher.deleted_by is None


class TestBaseModel:
    def test_has_timestamps(self, db, wb_teacher):
        assert wb_teacher.created_at is not None
        assert wb_teacher.updated_at is not None

    def test_has_soft_delete_fields(self, db, wb_teacher):
        assert hasattr(wb_teacher, 'is_deleted')
        assert hasattr(wb_teacher, 'deleted_at')
        assert hasattr(wb_teacher, 'deleted_by')


class TestSystemOperationLog:
    def test_create_log_basic(self, db, wb_mock_request):
        log = SystemOperationLog.create_log(
            request=wb_mock_request,
            module='user',
            operation_type='user_create',
            target_type='User',
            target_id=1,
            target_name='测试用户',
            description='创建了测试用户',
        )
        assert log.module == 'user'
        assert log.operation_type == 'user_create'
        assert log.target_id == 1
        assert log.operator == wb_mock_request.user
        assert log.ip_address == '127.0.0.1'

    def test_create_log_without_request(self, db):
        log = SystemOperationLog.create_log(
            request=None,
            module='system',
            operation_type='system_setting_update',
        )
        assert log.operator is None
        assert log.operator_username == ''

    def test_create_log_with_detail(self, db, wb_mock_request):
        detail = {'old': 'value1', 'new': 'value2'}
        log = SystemOperationLog.create_log(
            request=wb_mock_request,
            module='user',
            operation_type='user_update',
            detail=detail,
        )
        assert log.detail == detail

    def test_target_name_truncated(self, db, wb_mock_request):
        long_name = 'A' * 300
        log = SystemOperationLog.create_log(
            request=wb_mock_request,
            module='user',
            operation_type='user_create',
            target_name=long_name,
        )
        assert len(log.target_name) <= 200

    def test_get_module_operations(self):
        user_ops = SystemOperationLog.get_module_operations('user')
        assert len(user_ops) > 0
        for op_code, op_name in user_ops:
            assert op_code.startswith('user')

    def test_module_choices(self):
        assert len(SystemOperationLog.MODULE_CHOICES) > 0

    def test_operation_type_choices(self):
        assert len(SystemOperationLog.OPERATION_TYPE_CHOICES) > 0
