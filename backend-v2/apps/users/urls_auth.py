"""
用户认证路由
"""

from django.urls import path
from apps.users.views import (
    CaptchaView, CaptchaVerifyView, LoginView, LogoutView,
    TokenRefreshView, ChangePasswordView, AdminResetPasswordView,
    BatchResetPasswordView,
    SecurityQuestionView, UserSecurityQuestionView, VerifySecurityAnswerView,
    ResetPasswordBySecurityView, PasswordResetContactView
)

urlpatterns = [
    path('captcha/', CaptchaView.as_view(), name='captcha'),
    path('captcha/verify/', CaptchaVerifyView.as_view(), name='captcha-verify'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('password/change/', ChangePasswordView.as_view(), name='password-change'),
    path('password/reset/', AdminResetPasswordView.as_view(), name='password-reset-admin'),
    path('password/batch-reset/', BatchResetPasswordView.as_view(), name='password-batch-reset'),
    path('security-question/', SecurityQuestionView.as_view(), name='security-question'),
    path('security-question/user/', UserSecurityQuestionView.as_view(), name='user-security-question'),
    path('security-question/verify/', VerifySecurityAnswerView.as_view(), name='verify-security-answer'),
    path('password/reset-by-security/', ResetPasswordBySecurityView.as_view(), name='password-reset-security'),
    path('password-reset-contact/', PasswordResetContactView.as_view(), name='password-reset-contact'),
]
