import pytest
from apps.schedules.services.semester_service import SemesterService
from apps.schedules.models import Semester
from apps.core.exceptions import ValidationError


class TestSemesterArchiveWorkflow:
    def test_create_set_current_archive(self, db, wb_super_admin):
        Semester.objects.filter(is_current=True).update(is_current=False)
        service = SemesterService()
        sem = service.create_semester(
            requester=wb_super_admin,
            data={
                'name': '归档测试学期',
                'code': 'WF_ARCHIVE',
                'start_date': '2025-02-01',
                'end_date': '2025-06-30',
                'is_current': True,
            },
        )
        assert sem.is_current is True

        sem2 = service.create_semester(
            requester=wb_super_admin,
            data={
                'name': '新学期',
                'code': 'WF_NEW',
                'start_date': '2025-09-01',
                'end_date': '2026-01-15',
                'is_current': False,
            },
        )
        service.set_current_semester(wb_super_admin, sem2.id)
        sem.refresh_from_db()
        assert sem.is_current is False

        service.archive_semester(wb_super_admin, sem.id)
        sem.refresh_from_db()
        assert sem.is_archived is True

    def test_cannot_delete_current(self, db, wb_super_admin, wb_semester):
        service = SemesterService()
        with pytest.raises(ValidationError, match='不能删除当前学期'):
            service.delete_semester(wb_super_admin, wb_semester.id)

    def test_cannot_archive_current(self, db, wb_super_admin, wb_semester):
        service = SemesterService()
        with pytest.raises(ValidationError, match='不能归档当前学期'):
            service.archive_semester(wb_super_admin, wb_semester.id)
