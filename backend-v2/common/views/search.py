"""
全局搜索视图
"""

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema
from common.responses import ApiResponse
from common.services.search_service import GlobalSearchService


class GlobalSearchView(APIView):
    """全局搜索视图"""
    permission_classes = [IsAuthenticated]

    @extend_schema(description='全局搜索')
    def get(self, request):
        keyword = request.query_params.get('keyword', '').strip()
        limit = int(request.query_params.get('limit', 10))
        
        if not keyword:
            return ApiResponse.error(message='请输入搜索关键词')
        
        service = GlobalSearchService()
        result = service.search(
            requester=request.user,
            keyword=keyword,
            limit=limit
        )
        
        return ApiResponse.success(data=result)
