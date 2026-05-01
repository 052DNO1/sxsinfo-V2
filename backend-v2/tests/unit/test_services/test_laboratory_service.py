import pytest
from apps.laboratories.services.laboratory_service import LaboratoryService
from apps.laboratories.models import Laboratory
from apps.users.models import User


class TestLaboratoryServiceCRUD:

    @pytest.fixture
    def service(self):
        return LaboratoryService()

    def test_create_laboratory_success(self, service, super_admin_user, test_department):
        data = {
            'name': '新实训室',
            'code': 'SERVICE_TEST_001',
            'building': '测试楼',
            'floor': 2,
            'room_number': '201',
            'capacity': 35,
            'laboratory_type': 'COMPUTER',
            'department_id': test_department.id,
            'description': '通过服务层创建',
        }
        lab = service.create_laboratory(
            requester=super_admin_user,
            data=data,
        )
        assert lab is not None
        assert lab.name == '新实训室'
        assert lab.code == 'SERVICE_TEST_001'
        assert Laboratory.objects.filter(code='SERVICE_TEST_001').exists()

    def test_create_duplicate_code_should_fail(self, service, super_admin_user, test_department, test_laboratory):
        data = {
            'name': '重复编号',
            'code': test_laboratory.code,
            'building': '测试楼',
            'floor': 1,
            'room_number': '101',
            'capacity': 20,
            'laboratory_type': 'COMPUTER',
            'department_id': test_department.id,
        }
        with pytest.raises(Exception):
            service.create_laboratory(requester=super_admin_user, data=data)

    def test_update_laboratory_success(self, service, super_admin_user, test_laboratory):
        data = {
            'name': '更新后的名称',
            'capacity': 50,
        }
        result = service.update_laboratory(
            requester=super_admin_user,
            laboratory_id=test_laboratory.id,
            data=data,
        )
        assert result is not None
        assert result.name == '更新后的名称'
        assert result.capacity == 50
        test_laboratory.refresh_from_db()
        assert test_laboratory.name == '更新后的名称'

    def test_update_laboratory_set_admin_to_none(self, service, super_admin_user, test_laboratory, lab_admin_user):
        assert test_laboratory.admin is not None
        data = {'admin': None}
        result = service.update_laboratory(
            requester=super_admin_user,
            laboratory_id=test_laboratory.id,
            data=data,
        )
        assert result is not None
        assert result.admin is None
        test_laboratory.refresh_from_db()
        assert test_laboratory.admin is None

    def test_update_laboratory_change_admin(self, service, super_admin_user, test_laboratory):
        new_admin = User.objects.create_user(
            username='new_lab_admin_svc',
            password='test123456',
            nickname='新管理员',
            role=2,
            is_active=True,
        )
        data = {'admin': new_admin.id}
        result = service.update_laboratory(
            requester=super_admin_user,
            laboratory_id=test_laboratory.id,
            data=data,
        )
        assert result.admin == new_admin

    def test_update_nonexistent_laboratory_should_fail(self, service, super_admin_user):
        data = {'name': '不存在'}
        with pytest.raises(Exception):
            service.update_laboratory(
                requester=super_admin_user,
                laboratory_id=99999,
                data=data,
            )

    def test_get_laboratory_list_pagination(self, service, super_admin_user, test_laboratory):
        result = service.get_laboratory_list(
            requester=super_admin_user,
            page=1,
            page_size=10,
        )
        assert 'pagination' in result
        assert 'list' in result
        assert result['pagination']['total'] >= 1

    def test_get_laboratory_detail(self, service, super_admin_user, test_laboratory):
        result = service.get_laboratory_detail(
            requester=super_admin_user,
            laboratory_id=test_laboratory.id,
        )
        assert result is not None
        assert result['id'] == test_laboratory.id
        assert result['name'] == test_laboratory.name

    def test_delete_laboratory_success(self, service, super_admin_user, test_department):
        lab = Laboratory.objects.create(
            name='待删除的实训室',
            code='TO_DELETE_001',
            building='测试楼',
            floor=1,
            room_number='101',
            capacity=20,
            laboratory_type='COMPUTER',
            department=test_department,
            status=1,
        )
        lab_id = lab.id
        result = service.delete_laboratory(
            requester=super_admin_user,
            laboratory_id=lab_id,
        )
        assert result['success'] is True
        assert 'deleted_counts' in result
        assert 'preserved_counts' in result
        assert not Laboratory.objects.filter(id=lab_id, is_deleted=False).exists()

    def test_delete_nonexistent_laboratory_should_fail(self, service, super_admin_user):
        with pytest.raises(Exception):
            service.delete_laboratory(
                requester=super_admin_user,
                laboratory_id=99999,
            )


class TestLaboratoryServicePermissions:

    @pytest.fixture
    def service(self):
        return LaboratoryService()

    @pytest.fixture(autouse=True)
    def clear_cache(self):
        from django.core.cache import cache
        cache.clear()
        yield
        cache.clear()

    def test_super_admin_can_access_all_labs(self, service, super_admin_user, test_laboratory):
        result = service.get_laboratory_list(requester=super_admin_user)
        assert result['pagination']['total'] >= 1

    def test_department_admin_can_access_own_dept_labs(self, service, department_admin_user, test_laboratory, test_department):
        test_laboratory.department = test_department
        department_admin_user.department = test_department
        department_admin_user.save()
        test_laboratory.save()
        result = service.get_laboratory_list(requester=department_admin_user)
        assert result['pagination']['total'] >= 1

    def test_lab_admin_can_access_own_labs(self, service, lab_admin_user, test_laboratory):
        test_laboratory.admin = lab_admin_user
        test_laboratory.save()
        result = service.get_laboratory_list(requester=lab_admin_user)
        assert result['pagination']['total'] >= 1


class TestLaboratoryServiceFormatting:

    @pytest.fixture
    def service(self):
        return LaboratoryService()

    def test_format_includes_status_display(self, service, test_laboratory):
        detail = service.get_laboratory_detail(
            requester=User.objects.filter(is_superuser=True).first(),
            laboratory_id=test_laboratory.id,
        )
        assert 'status_display' in detail
        assert isinstance(detail['status_display'], dict)
        assert 'text' in detail['status_display']

    def test_format_includes_schedule_count(self, service, test_laboratory):
        detail = service.get_laboratory_detail(
            requester=User.objects.filter(is_superuser=True).first(),
            laboratory_id=test_laboratory.id,
        )
        assert 'schedule_count' in detail
        assert isinstance(detail['schedule_count'], int)

    def test_format_handles_empty_note(self, service, test_laboratory):
        test_laboratory.note = ''
        test_laboratory.save()
        detail = service.get_laboratory_detail(
            requester=User.objects.filter(is_superuser=True).first(),
            laboratory_id=test_laboratory.id,
        )
        assert 'note' in detail
