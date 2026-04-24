"""
AI助手路由 - 简洁版
"""

from django.urls import path
from apps.ai_assistant.views.ai import AIProcessView, AIExecuteView, AICancelView

urlpatterns = [
    path('process/', AIProcessView.as_view(), name='ai-process'),
    path('execute/', AIExecuteView.as_view(), name='ai-execute'),
    path('cancel/', AICancelView.as_view(), name='ai-cancel'),
]
