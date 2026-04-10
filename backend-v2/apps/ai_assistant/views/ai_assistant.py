"""
AI助手视图
"""

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema
from common.responses import ApiResponse
from common.paginations import StandardPagination
from apps.ai_assistant.services.ai_assistant_service import AIAssistantService


class AIChatView(APIView):
    """AI对话视图"""
    permission_classes = [IsAuthenticated]

    @extend_schema(description='发送消息给AI助手')
    def post(self, request):
        question = request.data.get('question', '').strip()
        session_id = request.data.get('session_id')

        if not question:
            return ApiResponse.error(message='请输入问题')

        service = AIAssistantService()
        result = service.process_request(
            user=request.user,
            question=question,
            session_id=session_id
        )

        return ApiResponse.success(data=result)


class AIExecuteView(APIView):
    """AI执行操作视图"""
    permission_classes = [IsAuthenticated]

    @extend_schema(description='执行AI确认的操作')
    def post(self, request):
        auth_token = request.data.get('auth_token')

        if not auth_token:
            return ApiResponse.error(message='缺少认证令牌')

        service = AIAssistantService()
        result = service.execute_operation(
            user=request.user,
            auth_token=auth_token
        )

        if result['success']:
            return ApiResponse.success(data=result, message=result.get('message', '操作成功'))
        else:
            return ApiResponse.error(message=result.get('error', '操作失败'))


class AICancelView(APIView):
    """AI取消操作视图"""
    permission_classes = [IsAuthenticated]

    @extend_schema(description='取消AI操作')
    def post(self, request):
        auth_token = request.data.get('auth_token')

        if not auth_token:
            return ApiResponse.error(message='缺少认证令牌')

        service = AIAssistantService()
        result = service.cancel_operation(auth_token=auth_token)

        return ApiResponse.success(message=result.get('message', '操作已取消'))


class AIHistoryView(APIView):
    """AI对话历史视图"""
    permission_classes = [IsAuthenticated]
    pagination_class = StandardPagination

    @extend_schema(description='获取AI对话历史')
    def get(self, request):
        from apps.ai_assistant.models import AIConversationHistory
        
        queryset = AIConversationHistory.objects.filter(
            user=request.user
        ).order_by('-created_at')
        
        paginator = StandardPagination()
        page = paginator.paginate_queryset(queryset, request)
        
        history = [
            {
                'id': h.id,
                'question': h.question,
                'answer': h.answer,
                'intent_type': h.intent_type,
                'created_at': h.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            }
            for h in page
        ]
        
        return ApiResponse.success(data={
            'list': history,
            'total': queryset.count(),
        })


class AIQueryView(APIView):
    """AI查询视图"""
    permission_classes = [IsAuthenticated]

    @extend_schema(description='AI智能查询')
    def post(self, request):
        query_type = request.data.get('query_type', 'general')
        params = request.data.get('params', {})
        
        service = AIAssistantService()
        result = service.execute_query(
            user=request.user,
            query_type=query_type,
            params=params
        )
        
        return ApiResponse.success(data=result)
