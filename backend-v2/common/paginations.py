"""
分页器
"""

from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from apps.core.constants import PAGINATION_PAGE_SIZE, PAGINATION_MAX_PAGE_SIZE


class StandardPagination(PageNumberPagination):
    """标准分页器"""
    page_size = PAGINATION_PAGE_SIZE
    page_size_query_param = 'page_size'
    max_page_size = PAGINATION_MAX_PAGE_SIZE
    page_query_param = 'page'

    def get_paginated_response(self, data):
        return Response({
            'success': True,
            'code': 'SUCCESS',
            'message': '查询成功',
            'data': {
                'list': data,
                'pagination': {
                    'total': self.page.paginator.count,
                    'page': self.page.number,
                    'page_size': self.page_size,
                    'total_pages': self.page.paginator.num_pages,
                }
            }
        })


class LargePagination(PageNumberPagination):
    """大分页器"""
    page_size = 100
    max_page_size = 500


class SmallPagination(PageNumberPagination):
    """小分页器"""
    page_size = 10
    max_page_size = 50
