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
        notif = service.send_notification(
            title='测试通知',
            content='测试内容',
            recipients=wb_teacher,
        )
        assert notif.title == '测试通知'
        assert NotificationRecipient.objects.filter(notification=notif).count() == 1

    def test_send_to_multiple_users(self, db, wb_teacher, wb_lab_admin):
        service = NotificationService()
        notif = service.send_notification(
            title='群发通知',
            content='群发内容',
            recipients=[wb_teacher, wb_lab_admin],
        )
        assert NotificationRecipient.objects.filter(notification=notif).count() == 2

    def test_send_with_sender(self, db, wb_system_admin, wb_teacher):
        service = NotificationService()
        notif = service.send_notification(
            title='有发送者的通知',
            content='内容',
            recipients=wb_teacher,
            sender=wb_system_admin,
        )
        assert notif.sender == wb_system_admin

    def test_send_with_type_and_priority(self, db, wb_teacher):
        service = NotificationService()
        notif = service.send_notification(
            title='紧急通知',
            content='紧急内容',
            recipients=wb_teacher,
            notification_type='URGENT',
            priority='HIGH',
        )
        assert notif.notification_type == 'URGENT'
        assert notif.priority == 'HIGH'


class TestNotificationServiceList:
    def test_list_notifications(self, db, wb_teacher, wb_notification):
        service = NotificationService()
        result = service.get_notification_list(user=wb_teacher)
        assert 'notifications' in result
        assert result['total'] >= 1

    def test_list_unread_count(self, db, wb_teacher, wb_notification):
        service = NotificationService()
        result = service.get_notification_list(user=wb_teacher)
        assert 'unread_count' in result
        assert result['unread_count'] >= 1

    def test_filter_by_read_status(self, db, wb_teacher, wb_notification):
        service = NotificationService()
        result = service.get_notification_list(user=wb_teacher, is_read=False)
        assert result['total'] >= 1

    def test_filter_by_type(self, db, wb_teacher, wb_notification):
        service = NotificationService()
        result = service.get_notification_list(
            user=wb_teacher, notification_type='SYSTEM'
        )
        assert result['total'] >= 1


class TestNotificationServiceDetail:
    def test_detail_marks_as_read(self, db, wb_teacher, wb_notification):
        service = NotificationService()
        result = service.get_notification_detail(
            user=wb_teacher,
            notification_id=wb_notification.id,
        )
        assert result['is_read'] is True

    def test_detail_already_read_stays_read(self, db, wb_teacher, wb_notification):
        service = NotificationService()
        service.get_notification_detail(user=wb_teacher, notification_id=wb_notification.id)
        result = service.get_notification_detail(user=wb_teacher, notification_id=wb_notification.id)
        assert result['is_read'] is True

    def test_detail_nonexistent(self, db, wb_teacher):
        service = NotificationService()
        with pytest.raises(NotFoundError, match='通知不存在'):
            service.get_notification_detail(user=wb_teacher, notification_id=99999)


class TestNotificationServiceMarkRead:
    def test_mark_as_read(self, db, wb_teacher, wb_notification):
        service = NotificationService()
        result = service.mark_as_read(user=wb_teacher, notification_id=wb_notification.id)
        assert result is True
        nr = NotificationRecipient.objects.get(
            notification=wb_notification, user=wb_teacher
        )
        assert nr.is_read is True

    def test_mark_already_read(self, db, wb_teacher, wb_notification):
        service = NotificationService()
        service.mark_as_read(user=wb_teacher, notification_id=wb_notification.id)
        result = service.mark_as_read(user=wb_teacher, notification_id=wb_notification.id)
        assert result is True

    def test_mark_nonexistent(self, db, wb_teacher):
        service = NotificationService()
        with pytest.raises(NotFoundError):
            service.mark_as_read(user=wb_teacher, notification_id=99999)


class TestNotificationServiceMarkAllRead:
    def test_mark_all_as_read(self, db, wb_system_admin, wb_teacher):
        service = NotificationService()
        service.send_notification('通知1', '内容1', wb_teacher)
        service.send_notification('通知2', '内容2', wb_teacher)
        count = service.mark_all_as_read(user=wb_teacher)
        assert count >= 2
        assert service.get_unread_count(wb_teacher) == 0


class TestNotificationServiceDelete:
    def test_delete_notification(self, db, wb_teacher, wb_notification):
        service = NotificationService()
        result = service.delete_notification(user=wb_teacher, notification_id=wb_notification.id)
        assert result is True
        assert not NotificationRecipient.objects.filter(
            notification=wb_notification, user=wb_teacher
        ).exists()

    def test_delete_nonexistent(self, db, wb_teacher):
        service = NotificationService()
        with pytest.raises(NotFoundError):
            service.delete_notification(user=wb_teacher, notification_id=99999)


class TestNotificationServiceUnreadCount:
    def test_unread_count(self, db, wb_teacher, wb_notification):
        service = NotificationService()
        count = service.get_unread_count(wb_teacher)
        assert count >= 1

    def test_unread_count_zero(self, db, wb_teacher):
        service = NotificationService()
        count = service.get_unread_count(wb_teacher)
        assert count == 0
