"""
备份恢复视图
"""

import json
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema
from common.responses import ApiResponse
from apps.backup.services.backup_service import BackupService
from apps.backup.services.auto_backup_service import AutoBackupConfigService


class BackupStatsView(APIView):
    """备份数据统计视图"""
    permission_classes = [IsAuthenticated]

    @extend_schema(description='获取备份数据统计')
    def get(self, request):
        stats = BackupService.get_backup_stats(requester=request.user)
        return ApiResponse.success(data={'stats': stats})


class BackupExportView(APIView):
    """数据备份导出视图"""
    permission_classes = [IsAuthenticated]

    @extend_schema(description='导出备份数据')
    def get(self, request):
        return BackupService.export_backup(requester=request.user)


class BackupInfoView(APIView):
    """备份信息视图"""
    permission_classes = [IsAuthenticated]

    @extend_schema(description='获取备份文件信息')
    def post(self, request):
        backup_file = request.FILES.get('backup_file')
        if not backup_file:
            return ApiResponse.error(message='请上传备份文件')

        try:
            backup_data = json.load(backup_file)
        except json.JSONDecodeError:
            return ApiResponse.error(message='备份文件格式错误')

        info = BackupService.get_backup_info(backup_data)
        return ApiResponse.success(data=info)


class BackupRestoreView(APIView):
    """数据恢复视图"""
    permission_classes = [IsAuthenticated]

    @extend_schema(description='恢复备份数据')
    def post(self, request):
        backup_file = request.FILES.get('backup_file')
        if not backup_file:
            return ApiResponse.error(message='请上传备份文件')

        try:
            backup_data = json.load(backup_file)
        except json.JSONDecodeError:
            return ApiResponse.error(message='备份文件格式错误')

        clear_existing = request.data.get('clear_existing', False)

        results = BackupService.restore_backup(
            requester=request.user,
            backup_data=backup_data,
            options={'clear_existing': clear_existing}
        )

        if results['success']:
            return ApiResponse.success(
                data=results,
                message='数据恢复成功'
            )
        else:
            return ApiResponse.error(
                message=results.get('errors', ['恢复失败'])[0]
            )


class AutoBackupConfigView(APIView):
    """自动备份配置视图"""
    permission_classes = [IsAuthenticated]

    @extend_schema(description='获取自动备份配置')
    def get(self, request):
        service = AutoBackupConfigService()
        config = service.get_config(requester=request.user)
        return ApiResponse.success(data=config)

    @extend_schema(description='保存自动备份配置')
    def post(self, request):
        service = AutoBackupConfigService()
        result = service.save_config(
            requester=request.user,
            data=request.data
        )
        return ApiResponse.success(data=result, message=result.get('message', '配置保存成功'))


class BackupListView(APIView):
    """备份列表视图"""
    permission_classes = [IsAuthenticated]

    @extend_schema(description='获取备份文件列表')
    def get(self, request):
        import os
        from django.conf import settings
        
        backup_dir = os.path.join(settings.BASE_DIR, 'backups')
        
        if not os.path.exists(backup_dir):
            return ApiResponse.success(data={'list': [], 'total': 0})
        
        files = []
        for filename in os.listdir(backup_dir):
            if filename.endswith('.json'):
                filepath = os.path.join(backup_dir, filename)
                stat = os.stat(filepath)
                files.append({
                    'filename': filename,
                    'size': stat.st_size,
                    'created_at': stat.st_ctime,
                })
        
        files.sort(key=lambda x: x['created_at'], reverse=True)
        
        return ApiResponse.success(data={'list': files, 'total': len(files)})


class BackupDownloadView(APIView):
    """备份下载视图"""
    permission_classes = [IsAuthenticated]

    @extend_schema(description='下载备份文件')
    def get(self, request, filename):
        import os
        from django.http import HttpResponse, FileResponse
        from django.conf import settings
        
        backup_dir = os.path.join(settings.BASE_DIR, 'backups')
        filepath = os.path.join(backup_dir, filename)
        
        if not os.path.exists(filepath):
            return ApiResponse.error(message='文件不存在', code=404)
        
        response = FileResponse(
            open(filepath, 'rb'),
            as_attachment=True,
            filename=filename
        )
        return response


class BackupDeleteView(APIView):
    """备份删除视图"""
    permission_classes = [IsAuthenticated]

    @extend_schema(description='删除备份文件')
    def delete(self, request, filename):
        import os
        from django.conf import settings
        
        backup_dir = os.path.join(settings.BASE_DIR, 'backups')
        filepath = os.path.join(backup_dir, filename)
        
        if not os.path.exists(filepath):
            return ApiResponse.error(message='文件不存在', code=404)
        
        os.remove(filepath)
        return ApiResponse.success(message='备份文件已删除')
