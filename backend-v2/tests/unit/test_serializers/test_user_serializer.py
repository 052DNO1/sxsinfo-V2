import pytest
from apps.users.serializers.user import (
    UserSerializer, UserCreateSerializer, UserUpdateSerializer,
    UserProfileSerializer, DepartmentSerializer, BatchDeleteSerializer
)
from apps.users.models import User, Department


class TestUserCreateSerializer:
    def test_valid_data(self, db, wb_department):
        import uuid
        data = {
            'username': f'ser_user_{uuid.uuid4().hex[:6]}',
            'nickname': '序列化器用户',
            'role': 1,
            'department': wb_department.id,
        }
        serializer = UserCreateSerializer(data=data)
        assert serializer.is_valid(), serializer.errors

    def test_empty_username(self, db):
        data = {'username': '', 'nickname': 'test'}
        serializer = UserCreateSerializer(data=data)
        assert not serializer.is_valid()
        assert 'username' in serializer.errors

    def test_invalid_username_format(self, db):
        data = {'username': 'user name!', 'nickname': 'test'}
        serializer = UserCreateSerializer(data=data)
        assert not serializer.is_valid()

    def test_duplicate_username(self, db, wb_teacher):
        data = {'username': wb_teacher.username, 'nickname': 'test'}
        serializer = UserCreateSerializer(data=data)
        assert not serializer.is_valid()
        assert 'username' in serializer.errors

    def test_default_password_is_username_prefix(self, db, wb_department):
        import uuid
        uname = f'defpwd_{uuid.uuid4().hex[:6]}'
        data = {
            'username': uname,
            'nickname': '默认密码测试',
            'role': 1,
            'department': wb_department.id,
        }
        serializer = UserCreateSerializer(data=data)
        assert serializer.is_valid(), serializer.errors
        user = serializer.save()
        assert user.check_password(uname[:6])

    def test_custom_password(self, db, wb_department):
        import uuid
        data = {
            'username': f'custpwd_{uuid.uuid4().hex[:6]}',
            'password': 'Custom@123',
            'nickname': '自定义密码',
            'role': 1,
            'department': wb_department.id,
        }
        serializer = UserCreateSerializer(data=data)
        assert serializer.is_valid()
        user = serializer.save()
        assert user.check_password('Custom@123')

    def test_department_null(self, db):
        import uuid
        data = {'username': f'nodept_{uuid.uuid4().hex[:6]}', 'nickname': '无部门', 'role': 1}
        serializer = UserCreateSerializer(data=data)
        assert serializer.is_valid()


class TestUserUpdateSerializer:
    def test_update_nickname(self, db, wb_teacher):
        data = {'nickname': '更新昵称', 'role': wb_teacher.role, 'status': wb_teacher.status}
        serializer = UserUpdateSerializer(instance=wb_teacher, data=data, partial=True)
        assert serializer.is_valid(), serializer.errors

    def test_update_role(self, db, wb_teacher):
        data = {'role': 2}
        serializer = UserUpdateSerializer(instance=wb_teacher, data=data, partial=True)
        assert serializer.is_valid()


class TestUserProfileSerializer:
    def test_read_only_fields(self, db, wb_teacher):
        data = {
            'nickname': '新昵称',
            'role': 32,
            'status': False,
            'department': None,
        }
        serializer = UserProfileSerializer(instance=wb_teacher, data=data, partial=True)
        assert serializer.is_valid()
        user = serializer.save()
        assert user.nickname == '新昵称'
        assert user.role != 32
        assert user.status is not False


class TestUserSerializer:
    def test_includes_roles(self, db, wb_teacher):
        serializer = UserSerializer(wb_teacher)
        assert 'roles' in serializer.data
        assert isinstance(serializer.data['roles'], list)

    def test_includes_department_name(self, db, wb_teacher):
        serializer = UserSerializer(wb_teacher)
        assert 'department_name' in serializer.data

    def test_formatted_dates(self, db, wb_teacher):
        serializer = UserSerializer(wb_teacher)
        assert 'created_at' in serializer.data
        assert 'updated_at' in serializer.data


class TestDepartmentSerializer:
    def test_includes_user_count(self, db, wb_department):
        serializer = DepartmentSerializer(wb_department)
        assert 'user_count' in serializer.data

    def test_includes_manager_names(self, db, wb_department):
        serializer = DepartmentSerializer(wb_department)
        assert 'manager_names' in serializer.data
        assert isinstance(serializer.data['manager_names'], list)


class TestBatchDeleteSerializer:
    def test_valid_ids(self):
        data = {'ids': [1, 2, 3]}
        serializer = BatchDeleteSerializer(data=data)
        assert serializer.is_valid()

    def test_empty_ids(self):
        data = {'ids': []}
        serializer = BatchDeleteSerializer(data=data)
        assert serializer.is_valid()

    def test_missing_ids(self):
        data = {}
        serializer = BatchDeleteSerializer(data=data)
        assert not serializer.is_valid()
