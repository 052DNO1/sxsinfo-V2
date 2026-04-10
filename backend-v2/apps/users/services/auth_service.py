"""
认证服务
"""

import re
import uuid
import random
import io
import base64
from datetime import timedelta
from django.utils import timezone
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.password_validation import validate_password, ValidationError as PasswordValidationError
from django.core.cache import cache
from rest_framework_simplejwt.tokens import RefreshToken
from PIL import Image, ImageDraw, ImageFont

from apps.core.exceptions import AuthenticationError, ValidationError
from apps.core.constants import ACCESS_TOKEN_LIFETIME, REFRESH_TOKEN_LIFETIME
from apps.users.models import User


CAPTCHA_CACHE_PREFIX = 'captcha_'
CAPTCHA_EXPIRE_SECONDS = 300
LOGIN_FAILED_PREFIX = 'login_failed_'
SECURITY_RESET_PREFIX = 'security_reset_'
SECURITY_RESET_EXPIRE = 300

SECURITY_QUESTIONS = [
    '您的母亲姓名是？',
    '您的父亲姓名是？',
    '您的出生城市是？',
    '您的第一所学校名称是？',
    '您最喜欢的颜色是？',
    '您的宠物名字是？',
    '您的配偶姓名是？',
    '您的小学班主任姓名是？',
]


class AuthService:
    """认证服务"""

    @staticmethod
    def generate_captcha():
        """生成验证码"""
        chars = '23456789ABCDEFGHJKLMNPQRSTUVWXYZ'
        captcha_text = ''.join(random.choice(chars) for _ in range(4))
        captcha_key = str(uuid.uuid4())
        
        cache.set(CAPTCHA_CACHE_PREFIX + captcha_key, captcha_text.lower(), CAPTCHA_EXPIRE_SECONDS)
        
        image = Image.new('RGB', (140, 40), (240, 249, 235))
        draw = ImageDraw.Draw(image)
        
        try:
            font = ImageFont.truetype("arial.ttf", 24)
        except:
            font = ImageFont.load_default()
        
        text_width = draw.textlength(captcha_text, font=font)
        x = (140 - text_width) / 2
        y = 8
        
        for i, char in enumerate(captcha_text):
            offset_x = random.randint(-2, 2)
            offset_y = random.randint(-2, 2)
            draw.text((x + i * (text_width / 4) + offset_x, y + offset_y), char, font=font, fill=(103, 194, 58))
        
        for _ in range(3):
            x1 = random.randint(0, 140)
            y1 = random.randint(0, 40)
            x2 = random.randint(0, 140)
            y2 = random.randint(0, 40)
            draw.line([(x1, y1), (x2, y2)], fill=(200, 200, 200), width=1)
        
        buffer = io.BytesIO()
        image.save(buffer, format='PNG')
        image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        
        return {
            'captcha_key': captcha_key,
            'captcha_image': f'data:image/png;base64,{image_base64}'
        }

    @staticmethod
    def verify_captcha(captcha_key: str, captcha_input: str) -> bool:
        """验证验证码"""
        if not captcha_key or not captcha_input:
            raise ValidationError('验证码不能为空')
        
        cached_captcha = cache.get(CAPTCHA_CACHE_PREFIX + captcha_key)
        cache.delete(CAPTCHA_CACHE_PREFIX + captcha_key)
        
        if not cached_captcha:
            raise ValidationError('验证码已过期')
        
        if cached_captcha != captcha_input.strip().lower():
            raise ValidationError('验证码错误')
        
        return True

    @staticmethod
    def login(username: str, password: str, request=None, captcha_key: str = None, captcha: str = None) -> dict:
        """用户登录"""
        if not username or not password:
            raise ValidationError('请输入用户名和密码')
        
        if not re.match(r'^[a-zA-Z0-9@.\-_]+$', username):
            raise ValidationError('用户名格式不正确')
        
        if captcha_key and captcha:
            AuthService.verify_captcha(captcha_key, captcha)
        
        ip = request.META.get('REMOTE_ADDR', '') if request else ''
        lock_key = f"{LOGIN_FAILED_PREFIX}{ip}"
        failed_count = cache.get(lock_key, 0)
        
        if failed_count >= 5:
            raise AuthenticationError('登录失败次数过多，请10分钟后再试')
        
        user = authenticate(username=username, password=password)
        
        if not user:
            cache.set(lock_key, failed_count + 1, 600)
            raise AuthenticationError('用户名或密码错误')
        
        if not user.is_active:
            raise AuthenticationError('账户已被禁用')
        
        if user.is_deleted:
            raise AuthenticationError('用户不存在')
        
        cache.delete(lock_key)
        
        refresh = RefreshToken.for_user(user)
        refresh.set_exp(lifetime=timedelta(days=REFRESH_TOKEN_LIFETIME))
        access_token = refresh.access_token
        access_token.set_exp(lifetime=timedelta(hours=ACCESS_TOKEN_LIFETIME))
        
        if request:
            user.last_login_ip = request.META.get('REMOTE_ADDR')
        user.first_login = False
        user.save(update_fields=['last_login_ip', 'first_login'])
        
        return {
            'access_token': str(access_token),
            'refresh_token': str(refresh),
            'user': {
                'id': user.id,
                'username': user.username,
                'nickname': user.nickname,
                'role': user.role,
                'roles': user.get_roles(),
                'is_superuser': user.is_superuser,
                'is_super_admin': user.is_super_admin,
                'is_systemadmin': user.is_system_admin,
                'is_system_admin': user.is_system_admin,
                'is_departadmin': user.is_department_admin,
                'is_department_admin': user.is_department_admin,
                'is_sxsadmin': user.is_laboratory_admin,
                'is_laboratory_admin': user.is_laboratory_admin,
                'is_teacher': user.is_teacher,
                'department_id': user.department_id,
                'department_name': user.department.name if user.department else None,
                'avatar': user.avatar.url if user.avatar else None,
                'first_login': user.first_login,
            }
        }

    @staticmethod
    def logout(user: User, refresh_token: str = None) -> bool:
        """用户登出"""
        if refresh_token:
            try:
                token = RefreshToken(refresh_token)
                token.blacklist()
            except Exception:
                pass
        return True

    @staticmethod
    def refresh_token(refresh_token: str) -> dict:
        """刷新Token"""
        try:
            refresh = RefreshToken(refresh_token)
            refresh.set_exp(lifetime=timedelta(days=REFRESH_TOKEN_LIFETIME))
            access_token = refresh.access_token
            access_token.set_exp(lifetime=timedelta(hours=ACCESS_TOKEN_LIFETIME))
            
            return {
                'access_token': str(access_token),
                'refresh_token': str(refresh),
            }
        except Exception:
            raise AuthenticationError('Token无效或已过期')

    @staticmethod
    def change_password(user: User, old_password: str, new_password: str, confirm_password: str) -> bool:
        """修改密码"""
        if new_password != confirm_password:
            raise ValidationError('两次密码输入不一致')
        
        if not user.check_password(old_password):
            raise ValidationError('原密码错误')
        
        try:
            validate_password(new_password)
        except PasswordValidationError as e:
            raise ValidationError('; '.join(e.messages))
        
        user.set_password(new_password)
        user.first_login = False
        user.save(update_fields=['password', 'first_login'])
        
        return True

    @staticmethod
    def reset_password_by_admin(requester: User, target_user_id: int) -> dict:
        """管理员重置用户密码"""
        if not requester.is_super_admin and not requester.is_department_admin:
            raise AuthenticationError('无权限重置密码')
        
        try:
            target_user = User.objects.get(id=target_user_id, is_deleted=False)
        except User.DoesNotExist:
            raise ValidationError('用户不存在')
        
        if requester.is_department_admin and not requester.is_super_admin:
            if target_user.department_id != requester.department_id:
                raise AuthenticationError('只能重置本部门用户密码')
        
        new_password = target_user.username[:6] if len(target_user.username) >= 6 else target_user.username
        target_user.set_password(new_password)
        target_user.first_login = True
        target_user.save(update_fields=['password', 'first_login'])
        
        return {
            'user_id': target_user.id,
            'username': target_user.username,
            'new_password': new_password
        }

    @staticmethod
    def batch_reset_password(requester: User, user_ids: list) -> dict:
        """批量重置用户密码"""
        if not requester.is_super_admin and not requester.is_department_admin:
            raise AuthenticationError('无权限重置密码')
        
        success_count = 0
        failed_list = []
        results = []
        
        for user_id in user_ids:
            try:
                target_user = User.objects.get(id=user_id, is_deleted=False)
                
                if requester.is_department_admin and not requester.is_super_admin:
                    if target_user.department_id != requester.department_id:
                        failed_list.append({'user_id': user_id, 'reason': '只能重置本部门用户密码'})
                        continue
                
                new_password = target_user.username[:6] if len(target_user.username) >= 6 else target_user.username
                target_user.set_password(new_password)
                target_user.first_login = True
                target_user.save(update_fields=['password', 'first_login'])
                
                results.append({
                    'user_id': target_user.id,
                    'username': target_user.username,
                    'new_password': new_password
                })
                success_count += 1
            except User.DoesNotExist:
                failed_list.append({'user_id': user_id, 'reason': '用户不存在'})
            except Exception as e:
                failed_list.append({'user_id': user_id, 'reason': str(e)})
        
        return {
            'success_count': success_count,
            'failed_count': len(failed_list),
            'failed_list': failed_list,
            'results': results
        }

    @staticmethod
    def get_security_questions() -> list:
        """获取密保问题列表"""
        return SECURITY_QUESTIONS

    @staticmethod
    def set_security_question(user: User, question: str, answer: str) -> bool:
        """设置密保问题"""
        if not question or not answer:
            raise ValidationError('请选择问题并填写答案')
        
        if question not in SECURITY_QUESTIONS:
            raise ValidationError('请选择预设的密保问题')
        
        if len(answer) < 2 or len(answer) > 50:
            raise ValidationError('答案长度应在2-50个字符之间')
        
        user.security_question = question
        user.security_answer = make_password(answer.strip().lower())
        user.save(update_fields=['security_question', 'security_answer'])
        
        return True

    @staticmethod
    def get_user_security_question(username: str) -> dict:
        """获取用户密保问题"""
        if not username:
            raise ValidationError('请输入用户名')
        
        try:
            user = User.objects.get(username=username, is_deleted=False)
        except User.DoesNotExist:
            raise ValidationError('用户不存在')
        
        if not user.security_question:
            return {
                'has_question': False,
                'username': username
            }
        
        return {
            'has_question': True,
            'question': user.security_question,
            'username': username
        }

    @staticmethod
    def verify_security_answer(request, username: str, answer: str) -> dict:
        """验证密保答案"""
        if not username or not answer:
            raise ValidationError('请填写完整信息')
        
        ip = request.META.get('REMOTE_ADDR', '') if request else ''
        lock_key = f"security_verify_{ip}"
        failed_count = cache.get(lock_key, 0)
        
        if failed_count >= 5:
            raise AuthenticationError('验证失败次数过多，请10分钟后再试')
        
        try:
            user = User.objects.get(username=username, is_deleted=False)
        except User.DoesNotExist:
            cache.set(lock_key, failed_count + 1, 600)
            raise ValidationError('用户不存在')
        
        if not user.security_question or not user.security_answer:
            cache.set(lock_key, failed_count + 1, 600)
            raise ValidationError('该用户未设置密保问题')
        
        if not check_password(answer.strip().lower(), user.security_answer):
            cache.set(lock_key, failed_count + 1, 600)
            remaining = 5 - (failed_count + 1)
            raise ValidationError(f'答案错误，还剩{remaining}次机会')
        
        cache.delete(lock_key)
        
        reset_token = str(uuid.uuid4())
        cache.set(SECURITY_RESET_PREFIX + reset_token, user.id, SECURITY_RESET_EXPIRE)
        
        return {
            'reset_token': reset_token,
            'expires_in': SECURITY_RESET_EXPIRE
        }

    @staticmethod
    def reset_password_by_security(reset_token: str, new_password: str, confirm_password: str) -> bool:
        """通过密保重置密码"""
        if not reset_token or not new_password or not confirm_password:
            raise ValidationError('请填写完整信息')
        
        if new_password != confirm_password:
            raise ValidationError('两次密码不一致')
        
        user_id = cache.get(SECURITY_RESET_PREFIX + reset_token)
        
        if not user_id:
            raise ValidationError('重置令牌已过期')
        
        try:
            user = User.objects.get(id=user_id, is_deleted=False)
        except User.DoesNotExist:
            raise ValidationError('用户不存在')
        
        try:
            validate_password(new_password)
        except PasswordValidationError as e:
            raise ValidationError('; '.join(e.messages))
        
        user.set_password(new_password)
        user.first_login = False
        user.save(update_fields=['password', 'first_login'])
        
        cache.delete(SECURITY_RESET_PREFIX + reset_token)
        
        return True

    @staticmethod
    def get_password_reset_contact(username: str) -> dict:
        """获取密码重置联系人"""
        try:
            user = User.objects.get(username=username, is_deleted=False)
            
            if user.is_superuser:
                return {
                    'found': True,
                    'user_type': 'superuser',
                    'message': '您是超级管理员，请联系系统技术支持',
                    'contact': {
                        'name': '系统技术支持',
                        'phone': '',
                        'email': ''
                    }
                }
            
            if user.is_department_admin:
                return {
                    'found': True,
                    'user_type': 'departadmin',
                    'message': '您是分院管理员，请联系超级管理员重置密码',
                    'contact': AuthService._get_superuser_contact()
                }
            
            return {
                'found': True,
                'user_type': 'teacher_or_sxsadmin',
                'message': f'请联系您所在分院【{user.department.name if user.department else "未知"}】的管理员',
                'contact': AuthService._get_department_admin_contact(user.department)
            }
            
        except User.DoesNotExist:
            return {
                'found': False,
                'user_type': 'unknown',
                'message': '用户不存在，请联系超级管理员',
                'contact': AuthService._get_superuser_contact()
            }

    @staticmethod
    def _get_department_admin_contact(department):
        """获取部门管理员联系信息"""
        if not department:
            return AuthService._get_superuser_contact()
        
        admin = User.objects.filter(
            department=department,
            role__in=[4, 5, 6, 7],
            is_active=True
        ).exclude(role=1).first()
        
        if admin:
            return {
                'name': admin.nickname or admin.username,
                'phone': admin.phone or '未填写',
                'email': admin.email or '未填写',
                'depart': department.name
            }
        
        return AuthService._get_superuser_contact()

    @staticmethod
    def _get_superuser_contact():
        """获取超级管理员联系信息"""
        superuser = User.objects.filter(is_superuser=True, is_active=True).first()
        
        if superuser:
            return {
                'name': superuser.nickname or superuser.username,
                'phone': superuser.phone or '未填写',
                'email': superuser.email or '未填写',
                'depart': '系统管理'
            }
        
        return {
            'name': '系统管理员',
            'phone': '请联系相关部门',
            'email': '请联系相关部门',
            'depart': '系统管理'
        }
