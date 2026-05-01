import pytest
from rest_framework import status
from common.responses import ApiResponse


class TestApiResponseSuccess:
    def test_default_success(self):
        response = ApiResponse.success()
        assert response.status_code == status.HTTP_200_OK
        data = response.data
        assert data['success'] is True
        assert data['code'] == 'SUCCESS'
        assert data['message'] == '操作成功'
        assert data['data'] is None

    def test_success_with_data(self):
        response = ApiResponse.success(data={'id': 1, 'name': 'test'})
        assert response.data['data'] == {'id': 1, 'name': 'test'}

    def test_success_with_custom_message(self):
        response = ApiResponse.success(message='查询成功')
        assert response.data['message'] == '查询成功'

    def test_success_with_data_and_message(self):
        response = ApiResponse.success(data=[1, 2, 3], message='列表获取成功')
        assert response.data['data'] == [1, 2, 3]
        assert response.data['message'] == '列表获取成功'


class TestApiResponseError:
    def test_default_error(self):
        response = ApiResponse.error()
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.data
        assert data['success'] is False
        assert data['code'] == 'ERROR'
        assert data['message'] == '操作失败'

    def test_error_with_custom_message(self):
        response = ApiResponse.error(message='参数错误')
        assert response.data['message'] == '参数错误'

    def test_error_with_custom_code(self):
        response = ApiResponse.error(code='VALIDATION_ERROR')
        assert response.data['code'] == 'VALIDATION_ERROR'

    def test_error_with_custom_status(self):
        response = ApiResponse.error(status_code=422)
        assert response.status_code == 422

    def test_error_with_data(self):
        response = ApiResponse.error(data={'field': '必填项'})
        assert response.data['data'] == {'field': '必填项'}


class TestApiResponseCreated:
    def test_created(self):
        response = ApiResponse.created(data={'id': 1})
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['success'] is True
        assert response.data['code'] == 'CREATED'
        assert response.data['data'] == {'id': 1}

    def test_created_with_custom_message(self):
        response = ApiResponse.created(message='用户创建成功')
        assert response.data['message'] == '用户创建成功'


class TestApiResponseNotFound:
    def test_not_found(self):
        response = ApiResponse.not_found()
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.data['success'] is False
        assert response.data['code'] == 'NOT_FOUND'

    def test_not_found_custom_message(self):
        response = ApiResponse.not_found(message='用户不存在')
        assert response.data['message'] == '用户不存在'


class TestApiResponseForbidden:
    def test_forbidden(self):
        response = ApiResponse.forbidden()
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.data['success'] is False
        assert response.data['code'] == 'FORBIDDEN'

    def test_forbidden_custom_message(self):
        response = ApiResponse.forbidden(message='无权限访问')
        assert response.data['message'] == '无权限访问'


class TestApiResponseUnauthorized:
    def test_unauthorized(self):
        response = ApiResponse.unauthorized()
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.data['success'] is False
        assert response.data['code'] == 'UNAUTHORIZED'

    def test_unauthorized_custom_message(self):
        response = ApiResponse.unauthorized(message='Token已过期')
        assert response.data['message'] == 'Token已过期'


class TestApiResponseFormat:
    def test_response_data_structure(self):
        response = ApiResponse.success(data={'key': 'value'})
        assert 'success' in response.data
        assert 'code' in response.data
        assert 'message' in response.data
        assert 'data' in response.data

    def test_kwargs_extra_fields(self):
        response = ApiResponse.success(data=None, pagination={'total': 100})
        assert response.data['pagination'] == {'total': 100}
