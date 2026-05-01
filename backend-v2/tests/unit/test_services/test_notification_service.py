import pytest
from apps.notifications.services.notification_service import NotificationService
from apps.notifications.models import Notification, NotificationRecipient
from apps.core.exceptions import NotFoundError


@pytest.fixture
def notif_service():
    return NotificationService()


class TestNotificationServiceSend:
    def test_send_to_single_user(self, db, wb_teacher):
        service = NotificationService()
        notif = service.send_notification('测试通知', '内容', wb_teacher)
        assert notif.title == '测试通知'
        assert NotificationRecipient.objects.filter(notification=notif).count() == 1

    def test_send_to_multiple_users(self, db, wb_teacher, wb_lab_admin):
        service = NotificationService()
        notif = service.send_notification('群发', '内容', [wb_teacher, wb_lab_admin])
        assert NotificationRecipient.objects.filter(notification=notif).count() == 2


class TestNotificationServiceRead:
    def test_detail_marks_as_read(self, db, wb_teacher, wb_notification):
        service = NotificationService()
        result = service.get_notification_detail(wb_teacher, wb_notification.id)
        assert result['is_read'] is True

    def test_mark_all_as_read(self, db, wb_system_admin, wb_teacher):
        service = NotificationService()
        service.send_notification('通知1', '内容1', wb_teacher)
        service.send_notification('通知2', '内容2', wb_teacher)
        count = service.mark_all_as_read(wb_teacher)
        assert count >= 2
        assert service.get_unread_count(wb_teacher) == 0

    def test_unread_count(self, db, wb_teacher, wb_notification):
        service = NotificationService()
        count = service.get_unread_count(wb_teacher)
        assert count >= 1


class TestNotificationServiceDelete:
    def test_delete_notification(self, db, wb_teacher, wb_notification):
        service = NotificationService()
        result = service.delete_notification(wb_teacher, wb_notification.id)
        assert result is True

    def test_delete_nonexistent(self, db, wb_teacher):
        service = NotificationService()
        with pytest.raises(NotFoundError):
            service.delete_notification(wb_teacher, 99999)
