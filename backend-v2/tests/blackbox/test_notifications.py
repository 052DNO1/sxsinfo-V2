import pytest
from tests.blackbox.client import (
    assert_success_response, assert_error_response,
    assert_paginated_response, extract_data, extract_list,
)
from tests.blackbox.config import API_ENDPOINTS


class TestNotificationList:
    def test_get_notification_list(self, authed_client):
        url = API_ENDPOINTS['notifications']['list']
        response = authed_client.get(url)
        assert response.status_code == 200

    def test_get_notification_list_with_pagination(self, authed_client):
        url = API_ENDPOINTS['notifications']['list']
        response = authed_client.get(url, {'page': 1, 'page_size': 10})
        assert response.status_code == 200

    def test_get_notification_list_filter_by_read_status(self, authed_client):
        url = API_ENDPOINTS['notifications']['list']
        response = authed_client.get(url, {'is_read': False})
        assert response.status_code == 200

    def test_get_notification_list_filter_by_type(self, authed_client):
        url = API_ENDPOINTS['notifications']['list']
        response = authed_client.get(url, {'notification_type': 'SYSTEM'})
        assert response.status_code == 200

    def test_get_notification_list_search(self, authed_client):
        url = API_ENDPOINTS['notifications']['list']
        response = authed_client.get(url, {'search': '测试'})
        assert response.status_code == 200


class TestNotificationDetail:
    def test_get_notification_detail(self, authed_client, db, system_admin):
        from apps.notifications.models import Notification, NotificationRecipient
        notif = Notification.objects.create(
            title='黑盒测试通知',
            content='黑盒测试通知内容',
            notification_type='SYSTEM',
            priority='NORMAL',
            sender=system_admin,
        )
        NotificationRecipient.objects.create(
            notification=notif,
            user=system_admin,
        )
        url = API_ENDPOINTS['notifications']['detail'].format(id=notif.id)
        response = authed_client.get(url)
        assert response.status_code == 200

    def test_get_notification_detail_not_found(self, authed_client):
        url = API_ENDPOINTS['notifications']['detail'].format(id=99999)
        response = authed_client.get(url)
        assert response.status_code in (400, 404)


class TestNotificationMarkRead:
    def test_mark_read(self, authed_client, db, system_admin):
        from apps.notifications.models import Notification, NotificationRecipient
        notif = Notification.objects.create(
            title='标记已读通知', content='内容',
            notification_type='SYSTEM', priority='NORMAL', sender=system_admin,
        )
        NotificationRecipient.objects.create(
            notification=notif, user=system_admin, is_read=False,
        )
        url = API_ENDPOINTS['notifications']['mark_read'].format(id=notif.id)
        response = authed_client.post(url)
        assert response.status_code == 200

    def test_mark_all_read(self, authed_client, db, system_admin):
        from apps.notifications.models import Notification, NotificationRecipient
        for i in range(3):
            notif = Notification.objects.create(
                title=f'批量已读{i}', content='内容',
                notification_type='SYSTEM', priority='NORMAL', sender=system_admin,
            )
            NotificationRecipient.objects.create(
                notification=notif, user=system_admin, is_read=False,
            )
        url = API_ENDPOINTS['notifications']['mark_all_read']
        response = authed_client.post(url)
        assert response.status_code == 200


class TestNotificationDelete:
    def test_delete_notification(self, authed_client, db, system_admin):
        from apps.notifications.models import Notification, NotificationRecipient
        notif = Notification.objects.create(
            title='待删除通知', content='内容',
            notification_type='SYSTEM', priority='NORMAL', sender=system_admin,
        )
        NotificationRecipient.objects.create(
            notification=notif, user=system_admin,
        )
        url = API_ENDPOINTS['notifications']['delete'].format(id=notif.id)
        response = authed_client.delete(url)
        assert response.status_code == 200


class TestNotificationUnreadCount:
    def test_get_unread_count(self, authed_client):
        url = API_ENDPOINTS['notifications']['unread_count']
        response = authed_client.get(url)
        assert response.status_code == 200


class TestNotificationSend:
    def test_send_notification(self, authed_client, teacher):
        url = API_ENDPOINTS['notifications']['send']
        response = authed_client.post(url, {
            'title': '黑盒发送通知',
            'content': '黑盒发送通知内容',
            'recipient_ids': [teacher.id],
            'notification_type': 'SYSTEM',
            'priority': 'NORMAL',
        })
        assert response.status_code == 200

    def test_send_notification_missing_title(self, authed_client, teacher):
        url = API_ENDPOINTS['notifications']['send']
        response = authed_client.post(url, {
            'content': '无标题通知',
            'recipient_ids': [teacher.id],
        })
        assert response.status_code in (200, 400)

    def test_send_notification_missing_recipients(self, authed_client):
        url = API_ENDPOINTS['notifications']['send']
        response = authed_client.post(url, {
            'title': '无收件人通知',
            'content': '内容',
        })
        assert response.status_code in (200, 400)


class TestNotificationBroadcast:
    def test_broadcast_notification(self, authed_client):
        url = API_ENDPOINTS['notifications']['broadcast']
        response = authed_client.post(url, {
            'title': '黑盒广播通知',
            'content': '黑盒广播通知内容',
            'notification_type': 'ALERT',
            'priority': 'HIGH',
        })
        assert response.status_code == 200

    def test_broadcast_missing_title(self, authed_client):
        url = API_ENDPOINTS['notifications']['broadcast']
        response = authed_client.post(url, {
            'content': '无标题广播',
        })
        assert response.status_code in (200, 400)
