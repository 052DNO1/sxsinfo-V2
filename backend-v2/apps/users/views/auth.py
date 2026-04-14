"""
认证视图
"""

from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiResponse
from common.responses import ApiResponse
from apps.users.serializers import (
    LoginSerializer, TokenRefreshSerializer, ChangePasswordSerializer,
    CaptchaVerifySerializer, SecurityQuestionSetSerializer,
    UserSecurityQuestionSerializer, VerifySecurityAnswerSerializer,
    ResetPasswordBySecuritySerializer, PasswordResetContactSerializer,
    AdminResetPasswordSerializer, BatchResetPasswordSerializer
)
from apps.users.services import AuthService


class CaptchaView(APIView):
    """验证码视图"""
    permission_classes = [AllowAny]

    @extend_schema(
        responses={200: OpenApiResponse(description='验证码生成成功')},
        description='生成验证码图片'
    )
    def get(self, request):
        result = AuthService.generate_captcha()
        return ApiResponse.success(data=result, message='验证码生成成功')


class CaptchaVerifyView(APIView):
    """验证码校验视图"""
    permission_classes = [AllowAny]

    @extend_schema(
        request=CaptchaVerifySerializer,
        description='校验验证码'
    )
    def post(self, request):
        serializer = CaptchaVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        AuthService.verify_captcha(
            captcha_key=serializer.validated_data['captcha_key'],
            captcha_input=serializer.validated_data['captcha']
        )
        
        return ApiResponse.success(message='验证成功')


class LoginView(APIView):
    """登录视图"""
    permission_classes = [AllowAny]

    @extend_schema(
        request=LoginSerializer,
        responses={
            200: OpenApiResponse(description='登录成功'),
            400: OpenApiResponse(description='登录失败'),
        },
        description='用户登录'
    )
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        data = serializer.validated_data
        result = AuthService.login(
            username=data['username'],
            password=data['password'],
            request=request,
            captcha_key=data.get('captcha_key'),
            captcha=data.get('captcha')
        )
        
        return ApiResponse.success(data=result, message='登录成功')


class LogoutView(APIView):
    """登出视图"""
    permission_classes = [IsAuthenticated]

    @extend_schema(description='用户登出')
    def post(self, request):
        refresh_token = request.data.get('refresh_token')
        AuthService.logout(request.user, refresh_token)
        return ApiResponse.success(message='登出成功')


class TokenRefreshView(APIView):
    """Token刷新视图"""
    permission_classes = [AllowAny]

    @extend_schema(
        request=TokenRefreshSerializer,
        description='刷新Token'
    )
    def post(self, request):
        serializer = TokenRefreshSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        result = AuthService.refresh_token(
            serializer.validated_data['refresh_token']
        )
        
        return ApiResponse.success(data=result)


class ChangePasswordView(APIView):
    """修改密码视图"""
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=ChangePasswordSerializer,
        description='修改密码'
    )
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        data = serializer.validated_data
        refresh_token = request.data.get('refresh_token')
        AuthService.change_password(
            user=request.user,
            old_password=data['old_pwd'],
            new_password=data['new_pwd'],
            confirm_password=data['confirm_pwd'],
            refresh_token=refresh_token
        )
        
        return ApiResponse.success(message='密码修改成功，请重新登录')


class AdminResetPasswordView(APIView):
    """管理员重置密码视图"""
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=AdminResetPasswordSerializer,
        description='管理员重置用户密码'
    )
    def post(self, request):
        serializer = AdminResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        result = AuthService.reset_password_by_admin(
            requester=request.user,
            target_user_id=serializer.validated_data['user_id']
        )
        
        return ApiResponse.success(
            data=result,
            message=f"已重置用户 {result['username']} 的密码为用户名前6位"
        )


class BatchResetPasswordView(APIView):
    """批量重置密码视图"""
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=BatchResetPasswordSerializer,
        description='批量重置用户密码'
    )
    def post(self, request):
        serializer = BatchResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        result = AuthService.batch_reset_password(
            requester=request.user,
            user_ids=serializer.validated_data['user_ids']
        )
        
        message = f"成功重置 {result['success_count']} 个用户密码"
        if result['failed_count'] > 0:
            message += f"，{result['failed_count']} 个失败"
        
        return ApiResponse.success(data=result, message=message)


class SecurityQuestionView(APIView):
    """密保问题视图"""
    permission_classes = [AllowAny]

    @extend_schema(description='获取预设密保问题列表')
    def get(self, request):
        questions = AuthService.get_security_questions()
        return ApiResponse.success(data={'questions': questions})

    @extend_schema(
        request=SecurityQuestionSetSerializer,
        description='设置当前用户的密保问题'
    )
    def post(self, request):
        if not request.user.is_authenticated:
            return ApiResponse.error(message='请先登录', code=401)
        
        serializer = SecurityQuestionSetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        data = serializer.validated_data
        AuthService.set_security_question(
            user=request.user,
            question=data['question'],
            answer=data['answer']
        )
        
        return ApiResponse.success(message='密保问题设置成功')


class UserSecurityQuestionView(APIView):
    """获取用户密保问题视图"""
    permission_classes = [AllowAny]

    @extend_schema(
        request=UserSecurityQuestionSerializer,
        description='获取指定用户的密保问题（忘记密码时使用）'
    )
    def post(self, request):
        serializer = UserSecurityQuestionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        result = AuthService.get_user_security_question(
            username=serializer.validated_data['username']
        )
        
        return ApiResponse.success(data=result)


class VerifySecurityAnswerView(APIView):
    """验证密保答案视图"""
    permission_classes = [AllowAny]

    @extend_schema(
        request=VerifySecurityAnswerSerializer,
        description='验证密保答案（忘记密码流程第二步）'
    )
    def post(self, request):
        serializer = VerifySecurityAnswerSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        data = serializer.validated_data
        result = AuthService.verify_security_answer(
            request=request,
            username=data['username'],
            answer=data['answer']
        )
        
        return ApiResponse.success(
            data=result,
            message='验证成功，请设置新密码'
        )


class ResetPasswordBySecurityView(APIView):
    """通过密保重置密码视图"""
    permission_classes = [AllowAny]

    @extend_schema(
        request=ResetPasswordBySecuritySerializer,
        description='通过密保验证重置密码（忘记密码流程第三步）'
    )
    def post(self, request):
        serializer = ResetPasswordBySecuritySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        data = serializer.validated_data
        AuthService.reset_password_by_security(
            reset_token=data['reset_token'],
            new_password=data['new_password'],
            confirm_password=data['confirm_password']
        )
        
        return ApiResponse.success(message='密码重置成功，请使用新密码登录')


class PasswordResetContactView(APIView):
    """密码重置联系人视图"""
    permission_classes = [AllowAny]

    @extend_schema(
        request=PasswordResetContactSerializer,
        description='获取密码重置联系人信息'
    )
    def post(self, request):
        serializer = PasswordResetContactSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        result = AuthService.get_password_reset_contact(
            username=serializer.validated_data['username']
        )
        
        return ApiResponse.success(data=result)
