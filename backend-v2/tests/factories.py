"""
测试工厂
"""

import factory
from factory.django import DjangoModelFactory
from apps.users.models import User, Department


class DepartmentFactory(DjangoModelFactory):
    class Meta:
        model = Department
    
    name = factory.Sequence(lambda n: f'部门{n}')
    code = factory.Sequence(lambda n: f'DEPT{n:03d}')


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User
    
    username = factory.Sequence(lambda n: f'user{n}')
    nickname = factory.Sequence(lambda n: f'用户{n}')
    department = factory.SubFactory(DepartmentFactory)
