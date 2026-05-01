import pytest
from django.core.cache import cache
from apps.statistics.services.statistics_service import StatisticsService
from apps.core.exceptions import ValidationError


@pytest.fixture(autouse=True)
def clear_stats_cache():
    cache.clear()
    yield
    cache.clear()


@pytest.fixture
def stats_service():
    return StatisticsService()


class TestStatisticsServiceDashboard:
    def test_dashboard_stats(self, db, wb_super_admin, wb_semester):
        service = StatisticsService()
        result = service.get_dashboard_stats(requester=wb_super_admin)
        assert 'laboratories' in result
        assert 'schedules' in result
        assert 'records' in result
        assert 'work_orders' in result
        assert 'equipment' in result
        assert 'users' in result
        assert 'usage_rate' in result
        assert 'current_semester' in result

    def test_dashboard_no_current_semester(self, db, wb_super_admin):
        from apps.schedules.models import Semester
        Semester.objects.filter(is_current=True).update(is_current=False)
        service = StatisticsService()
        with pytest.raises(ValidationError):
            service.get_dashboard_stats(requester=wb_super_admin)


class TestStatisticsServiceTeacherStats:
    def test_teacher_stats(self, db, wb_teacher, wb_semester):
        service = StatisticsService()
        result = service.get_teacher_stats(requester=wb_teacher)
        assert 'total_records' in result
        assert 'month_records' in result

    def test_teacher_stats_no_semester(self, db, wb_teacher):
        from apps.schedules.models import Semester
        Semester.objects.filter(is_current=True).update(is_current=False)
        service = StatisticsService()
        with pytest.raises(ValidationError):
            service.get_teacher_stats(requester=wb_teacher)


class TestStatisticsServiceLabAdminStats:
    def test_lab_admin_stats(self, db, wb_lab_admin, wb_semester):
        service = StatisticsService()
        result = service.get_laboratory_admin_stats(requester=wb_lab_admin)
        assert isinstance(result, dict)


class TestStatisticsServiceSuperAdminStats:
    def test_super_admin_stats(self, db, wb_super_admin, wb_semester):
        service = StatisticsService()
        result = service.get_super_admin_stats(requester=wb_super_admin)
        assert isinstance(result, dict)


class TestStatisticsServiceComprehensiveStats:
    def test_comprehensive_stats(self, db, wb_super_admin, wb_semester):
        service = StatisticsService()
        result = service.get_comprehensive_stats(requester=wb_super_admin)
        assert isinstance(result, dict)


class TestStatisticsServiceUsageRate:
    def test_usage_rate_calculation(self, db, wb_super_admin, wb_semester, wb_laboratory):
        service = StatisticsService()
        result = service.get_dashboard_stats(requester=wb_super_admin)
        usage_rate = result['usage_rate']
        assert 'schedule_rate' in usage_rate
        assert 'record_rate' in usage_rate
