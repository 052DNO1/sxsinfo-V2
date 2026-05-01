import pytest
from apps.schedules.services.semester_service import SemesterService
from apps.schedules.models import Semester
from apps.core.exceptions import ValidationError, NotFoundError, PermissionDenied


@pytest.fixture
def semester_service():
    return SemesterService()


class TestSemesterServiceCreate:
    def test_create_success(self, db, wb_super_admin):
        Semester.objects.filter(is_current=True).update(is_current=False)
        service = SemesterService()
        semester = service.create_semester(
            requester=wb_super_admin,
            data={
                'name': '白盒新建学期',
                'code': 'WB_NEW_SEM',
                'start_date': '2026-02-01',
                'end_date': '2026-06-30',
                'is_current': False,
            },
        )
        assert semester.name == '白盒新建学期'
        assert semester.code == 'WB_NEW_SEM'

    def test_create_no_permission(self, db, wb_teacher):
        service = SemesterService()
        with pytest.raises(PermissionDenied):
            service.create_semester(requester=wb_teacher, data={})

    def test_create_empty_name(self, db, wb_super_admin):
        service = SemesterService()
        with pytest.raises(ValidationError, match='学期名称不能为空'):
            service.create_semester(requester=wb_super_admin, data={'name': ''})

    def test_create_duplicate_name(self, db, wb_super_admin, wb_semester):
        service = SemesterService()
        with pytest.raises(ValidationError, match='已存在'):
            service.create_semester(
                requester=wb_super_admin,
                data={'name': wb_semester.name},
            )

    def test_create_duplicate_code_auto_increment(self, db, wb_super_admin):
        Semester.objects.filter(is_current=True).update(is_current=False)
        service = SemesterService()
        sem1 = service.create_semester(
            requester=wb_super_admin,
            data={'name': '唯一学期A', 'code': 'WB_DUP_CODE', 'is_current': False,
                  'start_date': '2026-02-01', 'end_date': '2026-06-30'},
        )
        sem2 = service.create_semester(
            requester=wb_super_admin,
            data={'name': '唯一学期B', 'code': 'WB_DUP_CODE', 'is_current': False,
                  'start_date': '2026-09-01', 'end_date': '2027-01-15'},
        )
        assert sem1.code != sem2.code
        assert sem2.code == 'WB_DUP_CODE_1'

    def test_create_end_before_start(self, db, wb_super_admin):
        service = SemesterService()
        with pytest.raises(ValidationError, match='开始日期不能晚于结束日期'):
            service.create_semester(
                requester=wb_super_admin,
                data={
                    'name': '测试学期',
                    'start_date': '2026-06-30',
                    'end_date': '2026-02-01',
                    'is_current': False,
                },
            )

    def test_create_current_when_existing_current(self, db, wb_super_admin, wb_semester):
        service = SemesterService()
        with pytest.raises(ValidationError, match='当前已有正在进行的学期'):
            service.create_semester(
                requester=wb_super_admin,
                data={
                    'name': '新当前学期',
                    'is_current': True,
                },
            )


class TestSemesterServiceUpdate:
    def test_update_name(self, db, wb_super_admin, wb_semester_not_current):
        service = SemesterService()
        semester = service.update_semester(
            requester=wb_super_admin,
            semester_id=wb_semester_not_current.id,
            data={'name': '更新后学期'},
        )
        assert semester.name == '更新后学期'

    def test_update_archived_semester(self, db, wb_super_admin, wb_semester_not_current):
        wb_semester_not_current.is_archived = True
        wb_semester_not_current.save()
        service = SemesterService()
        with pytest.raises(ValidationError, match='已归档的学期无法修改'):
            service.update_semester(
                requester=wb_super_admin,
                semester_id=wb_semester_not_current.id,
                data={'name': '尝试修改'},
            )

    def test_update_no_permission(self, db, wb_teacher, wb_semester):
        service = SemesterService()
        with pytest.raises(PermissionDenied):
            service.update_semester(
                requester=wb_teacher,
                semester_id=wb_semester.id,
                data={'name': 'test'},
            )

    def test_update_nonexistent(self, db, wb_super_admin):
        service = SemesterService()
        with pytest.raises(NotFoundError):
            service.update_semester(
                requester=wb_super_admin,
                semester_id=99999,
                data={'name': 'test'},
            )


class TestSemesterServiceDelete:
    def test_delete_non_current(self, db, wb_super_admin, wb_semester_not_current):
        service = SemesterService()
        result = service.delete_semester(
            requester=wb_super_admin,
            semester_id=wb_semester_not_current.id,
        )
        assert result is True

    def test_delete_current_semester(self, db, wb_super_admin, wb_semester):
        service = SemesterService()
        with pytest.raises(ValidationError, match='不能删除当前学期'):
            service.delete_semester(
                requester=wb_super_admin,
                semester_id=wb_semester.id,
            )

    def test_delete_archived_semester(self, db, wb_super_admin, wb_semester_not_current):
        wb_semester_not_current.is_archived = True
        wb_semester_not_current.save()
        service = SemesterService()
        with pytest.raises(ValidationError, match='已归档的学期禁止删除'):
            service.delete_semester(
                requester=wb_super_admin,
                semester_id=wb_semester_not_current.id,
            )

    def test_delete_no_permission(self, db, wb_teacher, wb_semester_not_current):
        service = SemesterService()
        with pytest.raises(PermissionDenied):
            service.delete_semester(
                requester=wb_teacher,
                semester_id=wb_semester_not_current.id,
            )


class TestSemesterServiceSetCurrent:
    def test_set_current(self, db, wb_super_admin, wb_semester_not_current):
        service = SemesterService()
        semester = service.set_current_semester(
            requester=wb_super_admin,
            semester_id=wb_semester_not_current.id,
        )
        semester.refresh_from_db()
        assert semester.is_current is True

    def test_set_current_archived(self, db, wb_super_admin, wb_semester_not_current):
        wb_semester_not_current.is_archived = True
        wb_semester_not_current.save()
        service = SemesterService()
        with pytest.raises(ValidationError, match='不能将已归档的学期设为当前学期'):
            service.set_current_semester(
                requester=wb_super_admin,
                semester_id=wb_semester_not_current.id,
            )


class TestSemesterServiceArchive:
    def test_archive_non_current(self, db, wb_super_admin, wb_semester_not_current):
        service = SemesterService()
        semester = service.archive_semester(
            requester=wb_super_admin,
            semester_id=wb_semester_not_current.id,
        )
        semester.refresh_from_db()
        assert semester.is_archived is True

    def test_archive_current(self, db, wb_super_admin, wb_semester):
        service = SemesterService()
        with pytest.raises(ValidationError, match='不能归档当前学期'):
            service.archive_semester(
                requester=wb_super_admin,
                semester_id=wb_semester.id,
            )

    def test_archive_already_archived(self, db, wb_super_admin, wb_semester_not_current):
        wb_semester_not_current.is_archived = True
        wb_semester_not_current.save()
        service = SemesterService()
        with pytest.raises(ValidationError, match='该学期已归档'):
            service.archive_semester(
                requester=wb_super_admin,
                semester_id=wb_semester_not_current.id,
            )


class TestSemesterServiceArchiveSettings:
    def test_save_settings(self, db, wb_super_admin):
        service = SemesterService()
        result = service.save_archive_settings(
            requester=wb_super_admin,
            retention_months=12,
        )
        assert result['retention_months'] == 12

    def test_save_settings_zero(self, db, wb_super_admin):
        service = SemesterService()
        result = service.save_archive_settings(
            requester=wb_super_admin,
            retention_months=0,
        )
        assert result['retention_months'] == 0

    def test_save_settings_negative(self, db, wb_super_admin):
        service = SemesterService()
        with pytest.raises(ValidationError, match='有效的月份数值'):
            service.save_archive_settings(
                requester=wb_super_admin,
                retention_months=-1,
            )

    def test_save_settings_no_permission(self, db, wb_teacher):
        service = SemesterService()
        with pytest.raises(PermissionDenied):
            service.save_archive_settings(
                requester=wb_teacher,
                retention_months=12,
            )
