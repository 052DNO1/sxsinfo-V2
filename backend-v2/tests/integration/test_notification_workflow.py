import pytest
from apps.notifications.services.notification_service import NotificationService
from apps.notifications.models import Notification, NotificationRecipient


class TestNotificationFullWorkflow:
    def test_send_read_mark_delete(self, db, wb_system_admin, wb_teacher):
        service = NotificationService()

        notif = service.send_notification(
            title='集成测试通知',
            content='集成测试内容',
            recipients=wb_teacher,
            sender=wb_system_admin,
        )
        assert notif.title == '集成测试通知'
        assert service.get_unread_count(wb_teacher) >= 1

        result = service.get_notification_detail(wb_teacher, notif.id)
        assert result['is_read'] is True
        assert service.get_unread_count(wb_teacher) == 0

        result = service.delete_notification(wb_teacher, notif.id)
        assert result is True

    def test_batch_send_and_mark_all_read(self, db, wb_system_admin, wb_teacher, wb_lab_admin):
        service = NotificationService()

        service.send_notification('批量1', '内容1', [wb_teacher, wb_lab_admin])
        service.send_notification('批量2', '内容2', [wb_teacher, wb_lab_admin])

        assert service.get_unread_count(wb_teacher) >= 2
        count = service.mark_all_as_read(wb_teacher)
        assert count >= 2
        assert service.get_unread_count(wb_teacher) == 0

    def test_different_users_see_different_notifications(self, db, wb_system_admin, wb_teacher, wb_lab_admin):
        service = NotificationService()

        service.send_notification('仅教师', '内容', wb_teacher)
        service.send_notification('仅管理员', '内容', wb_lab_admin)

        teacher_list = service.get_notification_list(user=wb_teacher)
        admin_list = service.get_notification_list(user=wb_lab_admin)

        teacher_titles = [n['title'] for n in teacher_list['notifications']]
        admin_titles = [n['title'] for n in admin_list['notifications']]

        assert '仅教师' in teacher_titles
        assert '仅管理员' in admin_titles
