"""
用户模型
"""

from django.contrib.auth.models import AbstractUser
from django.db import models
from apps.core.models import BaseModel
from apps.core.constants import UserRole, UserStatus


class User(AbstractUser, BaseModel):
    """用户模型"""
    
    nickname = models.CharField('昵称', max_length=50, blank=True, default='')
    phone = models.CharField('手机号', max_length=11, blank=True, default='')
    avatar = models.ImageField('头像', upload_to='avatars/', blank=True, null=True)
    email = models.EmailField('邮箱', blank=True, default='')
    
    role = models.IntegerField(
        '用户角色',
        default=UserRole.TEACHER,
        help_text='使用位运算，可组合多个角色'
    )
    status = models.IntegerField(
        '用户状态',
        default=UserStatus.ACTIVE,
        choices=[(s.value, s.name) for s in UserStatus]
    )
    
    department = models.ForeignKey(
        'Department',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='所属部门',
        related_name='users'
    )
    
    last_login_ip = models.GenericIPAddressField('最后登录IP', blank=True, null=True)
    first_login = models.BooleanField('首次登录', default=True)
    password_changed_at = models.DateTimeField('密码修改时间', blank=True, null=True)
    
    security_question = models.CharField('密保问题', max_length=100, blank=True, default='')
    security_answer = models.CharField('密保答案', max_length=255, blank=True, default='')

    class Meta:
        db_table = 'users'
        verbose_name = '用户'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['username']),
            models.Index(fields=['phone']),
            models.Index(fields=['department', 'status']),
        ]

    def __str__(self):
        return self.nickname or self.username

    @property
    def is_teacher(self):
        if self.role is None:
            return False
        return bool(self.role & UserRole.TEACHER)

    @property
    def is_laboratory_admin(self):
        if self.role is None:
            return False
        return bool(self.role & UserRole.LABORATORY_ADMIN)

    @property
    def is_department_admin(self):
        if self.role is None:
            return False
        return bool(self.role & UserRole.DEPARTMENT_ADMIN)

    @property
    def is_super_admin(self):
        return self.is_superuser or (self.role is not None and bool(self.role & UserRole.SUPER_ADMIN))

    @property
    def is_system_admin(self):
        return self.is_superuser or (self.role is not None and bool(self.role & UserRole.SYSTEM_ADMIN))

    def has_role(self, role):
        if self.role is None:
            return False
        try:
            return bool(self.role & role)
        except TypeError:
            return False

    def add_role(self, role):
        if self.role is None:
            self.role = 0
        self.role |= role

    def remove_role(self, role):
        if self.role is None:
            return
        self.role &= ~role

    def get_roles(self):
        roles = []
        if self.role is None:
            return roles
        try:
            for role in UserRole:
                if self.has_role(role):
                    roles.append({'value': role.value, 'name': role.name})
        except Exception:
            pass
        return roles
