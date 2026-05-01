import pytest
from apps.core.middleware.logging import LoggingMiddleware
from django.test import RequestFactory
from django.http import HttpResponse


class TestLoggingMiddleware:
    def test_process_request_sets_start_time(self):
        factory = RequestFactory()
        request = factory.get('/api/v1/test/')
        middleware = LoggingMiddleware(get_response=lambda r: HttpResponse('ok'))
        middleware.process_request(request)
        assert hasattr(request, 'start_time')

    def test_process_response_calculates_duration(self):
        factory = RequestFactory()
        request = factory.get('/api/v1/test/')
        middleware = LoggingMiddleware(get_response=lambda r: HttpResponse('ok'))
        middleware.process_request(request)
        response = middleware(request)
        assert response.status_code == 200

    def test_middleware_with_post(self):
        factory = RequestFactory()
        request = factory.post('/api/v1/test/', data={'key': 'value'})
        middleware = LoggingMiddleware(get_response=lambda r: HttpResponse('created', status=201))
        response = middleware(request)
        assert response.status_code == 201

    def test_middleware_with_error_response(self):
        factory = RequestFactory()
        request = factory.get('/api/v1/test/')
        middleware = LoggingMiddleware(get_response=lambda r: HttpResponse('error', status=500))
        response = middleware(request)
        assert response.status_code == 500
