import pytest
from apps.laboratories.services.laboratory_service import LaboratoryService
from apps.laboratories.models import Laboratory
from apps.users.models import User


class TestLaboratoryFullCRUDWorkflow:

    @pytest.fixture
    def service(self):
        return LaboratoryService()

    def test_complete_create_read_update_delete_workflow(
        self, service, super_admin_user, test_department, lab_admin_user
    ):
        lab = service.create_laboratory(
            requester=super_admin_user,
            data={
                'name': '集成测试实训室',
                'code': 'INT_TEST_001',
                'building': '主楼',
                'floor': 3,
                'room_number': '301',
                'capacity': 40,
                'laboratory_type': 'COMPUTER',
                'department_id': test_department.id,
                'admin': lab_admin_user.id,
                'description': '用于集成测试',
            },
        )
        assert lab is not None
        lab_id = lab.id

        lab_obj = Laboratory.objects.get(id=lab_id)
        assert lab_obj.is_deleted is False
        assert lab_obj.name == '集成测试实训室'

        detail = service.get_laboratory_detail(
            requester=super_admin_user,
            laboratory_id=lab_id,
        )
        assert detail['id'] == lab_id
        assert detail['name'] == '集成测试实训室'
        assert detail['code'] == 'INT_TEST_001'

        updated_lab = service.update_laboratory(
            requester=super_admin_user,
            laboratory_id=lab_id,
            data={
                'name': '更新后的名称',
                'capacity': 50,
                'admin': None,
                'note': '更新备注',
            },
        )
        assert updated_lab.name == '更新后的名称'
        assert updated_lab.capacity == 50
        assert updated_lab.admin is None

        detail_after_update = service.get_laboratory_detail(
            requester=super_admin_user,
            laboratory_id=lab_id,
        )
        assert detail_after_update['name'] == '更新后的名称'
        assert detail_after_update['admin_name'] is None or detail_after_update['admin_name'] == ''

        updated_lab2 = service.update_laboratory(
            requester=super_admin_user,
            laboratory_id=lab_id,
            data={'admin': lab_admin_user.id},
        )
        assert updated_lab2.admin == lab_admin_user

        delete_result = service.delete_laboratory(
            requester=super_admin_user,
            laboratory_id=lab_id,
        )
        assert delete_result['success'] is True

        assert not Laboratory.objects.filter(id=lab_id, is_deleted=False).exists()

        with pytest.raises(Exception):
            service.get_laboratory_detail(
                requester=super_admin_user,
                laboratory_id=lab_id,
            )


class TestLaboratoryAdminAssignmentScenarios:

    @pytest.fixture
    def service(self):
        return LaboratoryService()

    def test_assign_admin_to_unassigned_lab(
        self, service, super_admin_user, test_department, lab_admin_user
    ):
        lab = Laboratory.objects.create(
            name='无管理员实训室',
            code='NO_ADMIN_LAB',
            building='测试楼',
            floor=1,
            room_number='101',
            capacity=30,
            laboratory_type='COMPUTER',
            department=test_department,
            admin=None,
            status=1,
        )
        result = service.update_laboratory(
            requester=super_admin_user,
            laboratory_id=lab.id,
            data={'admin': lab_admin_user.id},
        )
        assert result.admin == lab_admin_user
        lab.refresh_from_db()
        assert lab.admin == lab_admin_user

    def test_reassign_admin_to_different_user(
        self, service, super_admin_user, test_laboratory
    ):
        new_admin = User.objects.create_user(
            username='replacement_admin',
            password='test123456',
            nickname='替换管理员',
            role=2,
            is_active=True,
        )
        result = service.update_laboratory(
            requester=super_admin_user,
            laboratory_id=test_laboratory.id,
            data={'admin': new_admin.id},
        )
        assert result.admin == new_admin

    def test_batch_operations_consistency(
        self, service, super_admin_user, test_department
    ):
        labs = []
        for i in range(5):
            lab = service.create_laboratory(
                requester=super_admin_user,
                data={
                    'name': f'批量测试实训室_{i}',
                    'code': f'BATCH_{i:03d}',
                    'building': '批量楼',
                    'floor': i + 1,
                    'room_number': f'{i + 1}01',
                    'capacity': 30 + i * 5,
                    'laboratory_type': 'COMPUTER',
                    'department_id': test_department.id,
                },
            )
            labs.append(lab)

        list_result = service.get_laboratory_list(
            requester=super_admin_user,
            page=1,
            page_size=20,
            no_page=True,
        )
        assert len(list_result['list']) >= 5

        for lab in labs:
            service.update_laboratory(
                requester=super_admin_user,
                laboratory_id=lab.id,
                data={'note': f'批量更新备注_{lab.id}'},
            )

        for lab in labs:
            detail = service.get_laboratory_detail(
                requester=super_admin_user,
                laboratory_id=lab.id,
            )
            assert f'批量更新备注_{lab.id}' in detail.get('note', '')


class TestLaboratoryEdgeCases:

    @pytest.fixture
    def service(self):
        return LaboratoryService()

    def test_concurrent_updates(self, service, super_admin_user, test_laboratory):
        service.update_laboratory(
            requester=super_admin_user,
            laboratory_id=test_laboratory.id,
            data={'name': '第一次更新'},
        )
        service.update_laboratory(
            requester=super_admin_user,
            laboratory_id=test_laboratory.id,
            data={'capacity': 100},
        )
        test_laboratory.refresh_from_db()
        assert test_laboratory.name == '第一次更新'
        assert test_laboratory.capacity == 100

    def test_unicode_and_special_characters(
        self, service, super_admin_user, test_department
    ):
        lab = service.create_laboratory(
            requester=super_admin_user,
            data={
                'name': '中文实训室名称 🎓',
                'code': 'UNICODE_001',
                'building': '测试楼 αβγ',
                'floor': 1,
                'room_number': '101',
                'capacity': 30,
                'laboratory_type': 'COMPUTER',
                'department_id': test_department.id,
                'description': '特殊字符测试：<>&"\'',
            },
        )
        assert lab is not None
        assert '🎓' in lab.name

        detail = service.get_laboratory_detail(
            requester=super_admin_user,
            laboratory_id=lab.id,
        )
        assert detail['name'] == '中文实训室名称 🎓'
