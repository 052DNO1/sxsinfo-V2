import time
from rest_framework.test import APIClient
from tests.blackbox.config import API_BASE_URL, DEFAULT_PASSWORD


class BlackboxAPIClient:
    def __init__(self, base_url=None):
        self.client = APIClient()
        self.base_url = base_url or API_BASE_URL
        self._access_token = None
        self._refresh_token = None
        self._user = None

    def _url(self, path):
        if path.startswith('http'):
            return path
        return f'{self.base_url}/{path}'

    def authenticate(self, username, password=None):
        password = password or DEFAULT_PASSWORD
        url = self._url('auth/login/')
        response = self.client.post(url, {
            'username': username,
            'password': password,
        }, format='json')
        if response.status_code == 200:
            data = response.json()
            token_data = data.get('data', data)
            self._access_token = token_data.get('access') or token_data.get('access_token')
            self._refresh_token = token_data.get('refresh') or token_data.get('refresh_token')
            self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self._access_token}')
        return response

    def authenticate_with_token(self, access_token):
        self._access_token = access_token
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

    def clear_auth(self):
        self._access_token = None
        self._refresh_token = None
        self._user = None
        self.client.credentials()

    def refresh_token(self):
        if not self._refresh_token:
            return None
        url = self._url('auth/token/refresh/')
        response = self.client.post(url, {
            'refresh_token': self._refresh_token,
        }, format='json')
        if response.status_code == 200:
            data = response.json()
            token_data = data.get('data', data)
            self._access_token = token_data.get('access') or token_data.get('access_token')
            self._refresh_token = token_data.get('refresh') or token_data.get('refresh_token')
            self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self._access_token}')
        return response

    def get(self, path, params=None, **kwargs):
        return self.client.get(self._url(path), params, format=kwargs.pop('format', 'json'), **kwargs)

    def post(self, path, data=None, **kwargs):
        return self.client.post(self._url(path), data, format=kwargs.pop('format', 'json'), **kwargs)

    def put(self, path, data=None, **kwargs):
        return self.client.put(self._url(path), data, format=kwargs.pop('format', 'json'), **kwargs)

    def patch(self, path, data=None, **kwargs):
        return self.client.patch(self._url(path), data, format=kwargs.pop('format', 'json'), **kwargs)

    def delete(self, path, data=None, **kwargs):
        return self.client.delete(self._url(path), data, format=kwargs.pop('format', 'json'), **kwargs)

    @property
    def is_authenticated(self):
        return self._access_token is not None


def assert_success_response(response, message=None):
    data = response.json()
    assert response.status_code in (200, 201), \
        f'Expected 200/201, got {response.status_code}: {data}'
    assert data.get('success') is True, \
        f'Expected success=True, got: {data}'
    if message:
        assert message in data.get('message', ''), \
            f'Expected message containing "{message}", got: {data.get("message")}'
    return data


def assert_error_response(response, status_code=None, code=None):
    data = response.json()
    if status_code:
        assert response.status_code == status_code, \
            f'Expected {status_code}, got {response.status_code}: {data}'
    assert data.get('success') is False, \
        f'Expected success=False, got: {data}'
    if code:
        assert data.get('code') == code, \
            f'Expected code={code}, got: {data.get("code")}'
    return data


def assert_paginated_response(response, min_count=0):
    data = response.json()
    assert response.status_code == 200, f'Expected 200, got {response.status_code}: {data}'
    assert data.get('success') is True, f'Expected success=True, got: {data}'
    inner = data.get('data', data)
    if 'pagination' in inner:
        pagination = inner['pagination']
        assert 'total' in pagination
        assert 'page' in pagination
        assert 'page_size' in pagination
        items = inner.get('list', [])
        assert len(items) >= min_count, \
            f'Expected at least {min_count} items, got {len(items)}'
    else:
        items = inner if isinstance(inner, list) else inner.get('list', [])
        assert len(items) >= min_count if min_count > 0 else True
    return data


def extract_data(response):
    data = response.json()
    return data.get('data', data)


def extract_list(response):
    data = response.json()
    inner = data.get('data', data)
    if isinstance(inner, dict) and 'list' in inner:
        return inner['list']
    if isinstance(inner, list):
        return inner
    return []
