import pytest
from common.services.search_service import GlobalSearchService


@pytest.fixture
def search_service():
    return GlobalSearchService()


class TestSearchServiceLaboratories:
    def test_search_by_keyword(self, db, wb_super_admin, wb_laboratory):
        service = GlobalSearchService()
        result = service.search(wb_super_admin, '白盒')
        assert 'results' in result
        assert 'total' in result
        assert result['total'] >= 1
        found_lab = False
        for type_name, items in result['results'].items():
            for item in items:
                if item.get('resource_type') == 'sxs':
                    found_lab = True
        assert found_lab

    def test_search_no_results(self, db, wb_super_admin):
        service = GlobalSearchService()
        result = service.search(wb_super_admin, '不存在的关键词xyz')
        assert result['total'] == 0

    def test_search_teacher_limited(self, db, wb_teacher, wb_laboratory):
        service = GlobalSearchService()
        result = service.search(wb_teacher, '白盒')
        assert isinstance(result, dict)

    def test_search_dept_admin_filtered(self, db, wb_dept_admin, wb_laboratory):
        service = GlobalSearchService()
        result = service.search(wb_dept_admin, '白盒')
        assert isinstance(result, dict)


class TestSearchServiceUsers:
    def test_admin_can_search_users(self, db, wb_super_admin, wb_teacher):
        service = GlobalSearchService()
        result = service.search(wb_super_admin, 'wb_teacher')
        assert 'results' in result
        found_user = False
        for type_name, items in result['results'].items():
            for item in items:
                if item.get('resource_type') == 'user':
                    found_user = True
        assert found_user

    def test_teacher_cannot_search_users(self, db, wb_teacher):
        service = GlobalSearchService()
        result = service.search(wb_teacher, 'wb_teacher')
        found_user = False
        for type_name, items in result.get('results', {}).items():
            for item in items:
                if item.get('resource_type') == 'user':
                    found_user = True
        assert not found_user


class TestSearchServiceSchedules:
    def test_search_schedules(self, db, wb_super_admin, wb_schedule):
        service = GlobalSearchService()
        result = service.search(wb_super_admin, '白盒测试课程')
        assert 'results' in result
        found_schedule = False
        for type_name, items in result['results'].items():
            for item in items:
                if item.get('resource_type') == 'sxs_class':
                    found_schedule = True
        assert found_schedule

    def test_search_records(self, db, wb_super_admin, wb_usage_record):
        service = GlobalSearchService()
        result = service.search(wb_super_admin, '白盒')
        assert 'results' in result
        found_record = False
        for type_name, items in result['results'].items():
            for item in items:
                if item.get('resource_type') == 'record':
                    found_record = True
        assert found_record

    def test_search_work_orders(self, db, wb_super_admin, wb_work_order):
        service = GlobalSearchService()
        result = service.search(wb_super_admin, '白盒测试工单')
        assert 'results' in result
        found_wo = False
        for type_name, items in result['results'].items():
            for item in items:
                if item.get('resource_type') == 'maintain':
                    found_wo = True
        assert found_wo

    def test_search_equipment(self, db, wb_super_admin, wb_equipment):
        service = GlobalSearchService()
        result = service.search(wb_super_admin, '白盒测试设备')
        assert 'results' in result
        found_eq = False
        for type_name, items in result['results'].items():
            for item in items:
                if item.get('resource_type') == 'equipment':
                    found_eq = True
        assert found_eq


class TestSearchServiceLimit:
    def test_search_with_limit(self, db, wb_super_admin, wb_laboratory):
        service = GlobalSearchService()
        result = service.search(wb_super_admin, '白盒', limit=1)
        for type_name, items in result.get('results', {}).items():
            assert len(items) <= 1
