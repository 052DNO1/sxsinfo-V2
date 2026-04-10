"""
通知视图
"""

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema
from common.responses import ApiResponse
from apps.notifications.services.notification_service import NotificationService


class NotificationListView(APIView):
    """通知列表视图"""
    permission_classes = [IsAuthenticated]

    @extend_schema(description='获取通知列表')
    def get(self, request):
        service = NotificationService()
        
        is_read = request.query_params.get('is_read')
        if is_read == 'true':
            is_read = True
        elif is_read == 'false':
            is_read = False
        else:
            is_read = None
        
        result = service.get_notification_list(
            user=request.user,
            is_read=is_read,
            notification_type=request.query_params.get('notification_type'),
            search=request.query_params.get('search'),
            page=int(request.query_params.get('page', 1)),
            page_size=int(request.query_params.get('page_size', 10))
        )
        
        return ApiResponse.success(data=result)


class NotificationDetailView(APIView):
    """通知详情视图"""
    permission_classes = [IsAuthenticated]

    @extend_schema(description='获取通知详情')
    def get(self, request, notification_id):
        service = NotificationService()
        result = service.get_notification_detail(
            user=request.user,
            notification_id=notification_id
        )
        return ApiResponse.success(data={'notification': result})


class NotificationMarkReadView(APIView):
    """标记通知已读视图"""
    permission_classes = [IsAuthenticated]

    @extend_schema(description='标记通知为已读')
    def post(self, request, notification_id):
        service = NotificationService()
        service.mark_as_read(
            user=request.user,
            notification_id=notification_id
        )
        return ApiResponse.success(message='已标记为已读')


class NotificationMarkAllReadView(APIView):
    """标记所有通知已读视图"""
    permission_classes = [IsAuthenticated]

    @extend_schema(description='标记所有通知为已读')
    def post(self, request):
        service = NotificationService()
        count = service.mark_all_as_read(user=request.user)
        return ApiResponse.success(message=f'已将 {count} 条通知标记为已读')


class NotificationDeleteView(APIView):
    """删除通知视图"""
    permission_classes = [IsAuthenticated]

    @extend_schema(description='删除通知')
    def delete(self, request, notification_id):
        service = NotificationService()
        service.delete_notification(
            user=request.user,
            notification_id=notification_id
        )
        return ApiResponse.success(message='通知已删除')


class NotificationUnreadCountView(APIView):
    """未读通知数量视图"""
    permission_classes = [IsAuthenticated]

    @extend_schema(description='获取未读通知数量')
    def get(self, request):
        service = NotificationService()
        count = service.get_unread_count(user=request.user)
        return ApiResponse.success(data={'unread_count': count})


class SendNotificationView(APIView):
    """发送通知视图"""
    permission_classes = [IsAuthenticated]

    @extend_schema(description='发送通知')
    def post(self, request):
        if not request.user.is_department_admin and not request.user.is_super_admin:
            return ApiResponse.error(message='无权限发送通知', code=403)
        
        title = request.data.get('title', '').strip()
        content = request.data.get('content', '').strip()
        recipient_ids = request.data.get('recipient_ids', [])
        notification_type = request.data.get('notification_type', 'SYSTEM')
        priority = request.data.get('priority', 'NORMAL')
        
        if not title:
            return ApiResponse.error(message='标题不能为空')
        if not content:
            return ApiResponse.error(message='内容不能为空')
        if not recipient_ids:
            return ApiResponse.error(message='接收者不能为空')
        
        from apps.users.models import User
        recipients = User.objects.filter(id__in=recipient_ids, is_deleted=False)
        
        if not recipients.exists():
            return ApiResponse.error(message='未找到有效的接收者')
        
        service = NotificationService()
        notification = service.send_notification(
            title=title,
            content=content,
            recipients=list(recipients),
            notification_type=notification_type,
            priority=priority,
            sender=request.user
        )
        
        return ApiResponse.success(
            data={'id': notification.id},
            message='通知发送成功'
        )


class BroadcastNotificationView(APIView):
    """广播通知视图"""
    permission_classes = [IsAuthenticated]

    @extend_schema(description='广播通知（发送给所有用户）')
    def post(self, request):
        if not request.user.is_super_admin:
            return ApiResponse.error(message='只有超级管理员可以广播通知', code=403)
        
        title = request.data.get('title', '').strip()
        content = request.data.get('content', '').strip()
        notification_type = request.data.get('notification_type', 'SYSTEM')
        priority = request.data.get('priority', 'NORMAL')
        
        if not title:
            return ApiResponse.error(message='标题不能为空')
        if not content:
            return ApiResponse.error(message='内容不能为空')
        
        from apps.users.models import User
        recipients = User.objects.filter(is_deleted=False, is_active=True)
        
        service = NotificationService()
        notification = service.send_notification(
            title=title,
            content=content,
            recipients=list(recipients),
            notification_type=notification_type,
            priority=priority,
            sender=request.user
        )
        
        return ApiResponse.success(
            data={'id': notification.id, 'recipient_count': recipients.count()},
            message=f'广播通知已发送给 {recipients.count()} 个用户'
        )
