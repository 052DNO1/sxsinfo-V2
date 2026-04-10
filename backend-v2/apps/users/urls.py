"""
用户路由
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.users.views import (
    UserViewSet, ProfileView,
    CaptchaView, CaptchaVerifyView, LoginView, LogoutView,
    TokenRefreshView, ChangePasswordView, AdminResetPasswordView,
    SecurityQuestionView, UserSecurityQuestionView, VerifySecurityAnswerView,
    ResetPasswordBySecurityView, PasswordResetContactView
)

router = DefaultRouter()
router.register(r'', UserViewSet, basename='user')

urlpatterns = [
    path('profile/', ProfileView.as_view({'get': 'list', 'put': 'update'}), name='profile'),
    path('', include(router.urls)),
]
