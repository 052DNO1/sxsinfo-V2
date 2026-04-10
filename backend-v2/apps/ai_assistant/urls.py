"""
AI助手路由
"""

from django.urls import path
from apps.ai_assistant.views import (
    AIChatView, AIExecuteView, AICancelView, AIHistoryView, AIQueryView,
    LocalAgentProcessView, LocalAgentExecuteView, LocalAgentCancelView
)

urlpatterns = [
    path('chat/', AIChatView.as_view(), name='ai-chat'),
    path('execute/', AIExecuteView.as_view(), name='ai-execute'),
    path('cancel/', AICancelView.as_view(), name='ai-cancel'),
    path('history/', AIHistoryView.as_view(), name='ai-history'),
    path('query/', AIQueryView.as_view(), name='ai-query'),
    
    path('local/process/', LocalAgentProcessView.as_view(), name='local-agent-process'),
    path('local/execute/', LocalAgentExecuteView.as_view(), name='local-agent-execute'),
    path('local/cancel/', LocalAgentCancelView.as_view(), name='local-agent-cancel'),
]
