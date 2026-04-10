"""
进度查询视图
"""

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema
from common.responses import ApiResponse
from common.services.progress_service import ProgressService


class ProgressView(APIView):
    """进度查询视图"""
    permission_classes = [IsAuthenticated]

    @extend_schema(description='获取任务进度')
    def get(self, request):
        task_type = request.query_params.get('type', 'import')
        
        progress = ProgressService.get_progress(
            user_id=request.user.id,
            task_type=task_type
        )
        
        return ApiResponse.success(data=progress)
