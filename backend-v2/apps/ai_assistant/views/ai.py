"""
AI助手视图 - 简洁版
"""

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from drf_spectacular.utils import extend_schema
from common.responses import ApiResponse
from apps.ai_assistant.services.ai_service import AIService


class AIProcessView(APIView):
    """处理AI请求"""
    permission_classes = [IsAuthenticated]

    @extend_schema(description='处理AI请求')
    def post(self, request):
        question = request.data.get('question', '').strip()
        session_id = request.data.get('session_id')

        if not question:
            return ApiResponse.error(message='请输入内容')

        service = AIService()
        result = service.process(
            user=request.user,
            text=question,
            session_id=session_id
        )

        if result.get('success'):
            return ApiResponse.success(data=result, message=result.get('message', ''))
        else:
            return ApiResponse.error(message=result.get('message', '处理失败'))


class AIExecuteView(APIView):
    """执行已确认的操作"""
    permission_classes = [IsAuthenticated]

    @extend_schema(description='执行操作')
    def post(self, request):
        token = request.data.get('token')

        if not token:
            return ApiResponse.error(message='缺少令牌')

        service = AIService()
        result = service.execute(
            user=request.user,
            token=token
        )

        if result.get('success'):
            return ApiResponse.success(data=result, message=result.get('message', '操作成功'))
        else:
            # 业务逻辑错误返回200状态码，让前端正常处理错误信息
            return ApiResponse(
                data=result,
                message=result.get('message', '操作失败'),
                success=False,
                code='BUSINESS_ERROR',
                status_code=status.HTTP_200_OK
            )


class AICancelView(APIView):
    """取消操作"""
    permission_classes = [IsAuthenticated]

    @extend_schema(description='取消操作')
    def post(self, request):
        token = request.data.get('token')

        if not token:
            return ApiResponse.error(message='缺少令牌')

        service = AIService()
        result = service.cancel(token=token)

        return ApiResponse.success(message=result.get('message', '操作已取消'))
