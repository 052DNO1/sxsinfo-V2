import pytest
from rest_framework import status
from apps.core.exceptions import (
    LIMSException, ValidationError, AuthenticationError,
    PermissionDenied, NotFoundError, ConflictError,
    ScheduleConflictError, BusinessError
)


class TestLIMSException:
    def test_default_values(self):
        exc = LIMSException()
        assert exc.message == '系统错误'
        assert exc.code == 'SYSTEM_ERROR'
        assert exc.status_code == status.HTTP_400_BAD_REQUEST
        assert exc.data is None

    def test_custom_message(self):
        exc = LIMSException(message='自定义错误')
        assert exc.message == '自定义错误'

    def test_custom_code(self):
        exc = LIMSException(code='CUSTOM_CODE')
        assert exc.code == 'CUSTOM_CODE'

    def test_custom_status_code(self):
        exc = LIMSException(status_code=500)
        assert exc.status_code == 500

    def test_custom_data(self):
        exc = LIMSException(data={'key': 'value'})
        assert exc.data == {'key': 'value'}

    def test_all_custom_params(self):
        exc = LIMSException(
            message='test', code='TEST', status_code=418, data={'a': 1}
        )
        assert exc.message == 'test'
        assert exc.code == 'TEST'
        assert exc.status_code == 418
        assert exc.data == {'a': 1}

    def test_is_exception(self):
        exc = LIMSException()
        assert isinstance(exc, Exception)

    def test_str_representation(self):
        exc = LIMSException(message='测试错误')
        assert str(exc) == '测试错误'


class TestValidationError:
    def test_default_values(self):
        exc = ValidationError()
        assert exc.message == '数据验证失败'
        assert exc.code == 'VALIDATION_ERROR'
        assert exc.status_code == status.HTTP_400_BAD_REQUEST

    def test_inherits_from_base(self):
        exc = ValidationError()
        assert isinstance(exc, LIMSException)

    def test_custom_message(self):
        exc = ValidationError(message='字段不能为空')
        assert exc.message == '字段不能为空'


class TestAuthenticationError:
    def test_default_values(self):
        exc = AuthenticationError()
        assert exc.message == '认证失败'
        assert exc.code == 'AUTHENTICATION_ERROR'
        assert exc.status_code == status.HTTP_401_UNAUTHORIZED

    def test_inherits_from_base(self):
        assert isinstance(AuthenticationError(), LIMSException)


class TestPermissionDenied:
    def test_default_values(self):
        exc = PermissionDenied()
        assert exc.message == '权限不足'
        assert exc.code == 'PERMISSION_DENIED'
        assert exc.status_code == status.HTTP_403_FORBIDDEN

    def test_inherits_from_base(self):
        assert isinstance(PermissionDenied(), LIMSException)


class TestNotFoundError:
    def test_default_values(self):
        exc = NotFoundError()
        assert exc.message == '资源不存在'
        assert exc.code == 'NOT_FOUND'
        assert exc.status_code == status.HTTP_404_NOT_FOUND

    def test_inherits_from_base(self):
        assert isinstance(NotFoundError(), LIMSException)


class TestConflictError:
    def test_default_values(self):
        exc = ConflictError()
        assert exc.message == '资源冲突'
        assert exc.code == 'CONFLICT'
        assert exc.status_code == status.HTTP_409_CONFLICT

    def test_inherits_from_base(self):
        assert isinstance(ConflictError(), LIMSException)


class TestScheduleConflictError:
    def test_default_values(self):
        exc = ScheduleConflictError()
        assert exc.message == '课表时间冲突'
        assert exc.code == 'SCHEDULE_CONFLICT'
        assert exc.status_code == status.HTTP_409_CONFLICT

    def test_inherits_from_conflict(self):
        assert isinstance(ScheduleConflictError(), ConflictError)

    def test_inherits_from_base(self):
        assert isinstance(ScheduleConflictError(), LIMSException)

    def test_with_conflict_data(self):
        conflicts = [{'schedule_id': 1, 'course_name': '数学'}]
        exc = ScheduleConflictError(data={'conflicts': conflicts})
        assert exc.data == {'conflicts': conflicts}


class TestBusinessError:
    def test_default_values(self):
        exc = BusinessError()
        assert exc.message == '业务处理失败'
        assert exc.code == 'BUSINESS_ERROR'
        assert exc.status_code == status.HTTP_400_BAD_REQUEST

    def test_inherits_from_base(self):
        assert isinstance(BusinessError(), LIMSException)


class TestExceptionHierarchy:
    def test_all_inherit_from_limsexception(self):
        exceptions = [
            ValidationError, AuthenticationError, PermissionDenied,
            NotFoundError, ConflictError, ScheduleConflictError, BusinessError
        ]
        for exc_cls in exceptions:
            assert issubclass(exc_cls, LIMSException)

    def test_schedule_conflict_inherits_from_conflict(self):
        assert issubclass(ScheduleConflictError, ConflictError)

    def test_catch_by_base_class(self):
        with pytest.raises(LIMSException):
            raise ValidationError('test')

        with pytest.raises(LIMSException):
            raise ScheduleConflictError('test')

    def test_catch_conflict_catches_schedule_conflict(self):
        with pytest.raises(ConflictError):
            raise ScheduleConflictError('test')
