"""
本地Agent视图 - 不依赖外部AI模型的意图识别
"""

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema
from common.responses import ApiResponse
from apps.ai_assistant.services.local_agent_service import LocalAgentService


class LocalAgentProcessView(APIView):
    """本地Agent处理视图"""
    permission_classes = [IsAuthenticated]

    @extend_schema(description='处理用户请求（本地意图识别）')
    def post(self, request):
        question = request.data.get('question', '').strip()
        session_id = request.data.get('session_id')

        if not question:
            return ApiResponse.error(message='请输入问题')

        service = LocalAgentService()
        result = service.process_request(
            user=request.user,
            question=question,
            session_id=session_id
        )

        if result['success']:
            return ApiResponse.success(data=result, message=result.get('message', ''))
        else:
            return ApiResponse.error(message=result.get('error', '处理失败'))


class LocalAgentExecuteView(APIView):
    """本地Agent执行视图"""
    permission_classes = [IsAuthenticated]

    @extend_schema(description='执行已确认的操作')
    def post(self, request):
        auth_token = request.data.get('auth_token')

        if not auth_token:
            return ApiResponse.error(message='缺少认证令牌')

        service = LocalAgentService()
        result = service.execute_operation(
            user=request.user,
            auth_token=auth_token
        )

        if result['success']:
            return ApiResponse.success(data=result, message=result.get('message', '操作成功'))
        else:
            return ApiResponse.error(message=result.get('error', '操作失败'))


class LocalAgentCancelView(APIView):
    """本地Agent取消视图"""
    permission_classes = [IsAuthenticated]

    @extend_schema(description='取消操作')
    def post(self, request):
        auth_token = request.data.get('auth_token')

        if not auth_token:
            return ApiResponse.error(message='缺少认证令牌')

        service = LocalAgentService()
        result = service.cancel_operation(auth_token=auth_token)

        return ApiResponse.success(message=result.get('message', '操作已取消'))
