"""
备份恢复视图
"""

import os
from datetime import datetime
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema
from common.responses import ApiResponse
from common.permissions import IsSuperAdmin
from apps.core.utils import beijing_strftime
from apps.backup.services.backup_service import BackupService
from apps.backup.services.auto_backup_service import AutoBackupConfigService
from apps.core.exceptions import ValidationError


class BackupStatsView(APIView):
    """备份数据统计视图"""
    permission_classes = [IsAuthenticated, IsSuperAdmin]

    @extend_schema(description='获取备份数据统计')
    def get(self, request):
        stats = BackupService.get_backup_stats(requester=request.user)
        return ApiResponse.success(data={'stats': stats})


class BackupExportView(APIView):
    """数据备份导出视图"""
    permission_classes = [IsAuthenticated, IsSuperAdmin]

    @extend_schema(description='导出备份数据')
    def get(self, request):
        compress = request.query_params.get('compress', 'true').lower() == 'true'
        return BackupService.export_backup(
            requester=request.user,
            compress=compress,
            save_local=True
        )


class BackupInfoView(APIView):
    """备份信息视图"""
    permission_classes = [IsAuthenticated, IsSuperAdmin]

    @extend_schema(description='获取备份文件信息')
    def post(self, request):
        backup_file = request.FILES.get('backup_file')
        if not backup_file:
            return ApiResponse.error(message='请上传备份文件')

        try:
            backup_data = BackupService.parse_backup_file(backup_file)
            info = BackupService.get_backup_info(backup_data)
            return ApiResponse.success(data=info)
        except ValidationError as e:
            return ApiResponse.error(message=str(e))
        except Exception as e:
            return ApiResponse.error(message=f'读取备份文件失败: {str(e)}')


class BackupRestoreView(APIView):
    """数据恢复视图"""
    permission_classes = [IsAuthenticated, IsSuperAdmin]

    @extend_schema(description='恢复备份数据')
    def post(self, request):
        backup_file = request.FILES.get('backup_file')
        if not backup_file:
            return ApiResponse.error(message='请上传备份文件')

        try:
            backup_data = BackupService.parse_backup_file(backup_file)
        except ValidationError as e:
            return ApiResponse.error(message=str(e))
        except Exception as e:
            return ApiResponse.error(message=f'读取备份文件失败: {str(e)}')

        clear_existing = request.data.get('clear_existing', False)

        try:
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
        except ValidationError as e:
            return ApiResponse.error(message=str(e))
        except Exception as e:
            return ApiResponse.error(message=f'恢复失败: {str(e)}')


class AutoBackupConfigView(APIView):
    """自动备份配置视图"""
    permission_classes = [IsAuthenticated, IsSuperAdmin]

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
    """备份列表视图（仅超管）"""
    permission_classes = [IsAuthenticated, IsSuperAdmin]

    @extend_schema(description='获取备份文件列表')
    def get(self, request):
        from django.conf import settings
        
        backup_dir = os.path.join(settings.BASE_DIR, 'backups')
        
        if not os.path.exists(backup_dir):
            return ApiResponse.success(data={'list': [], 'total': 0})
        
        files = []
        for filename in os.listdir(backup_dir):
            if filename.startswith('lims_backup_') and (filename.endswith('.json') or filename.endswith('.json.gz')):
                filepath = os.path.join(backup_dir, filename)
                stat = os.stat(filepath)
                
                is_compressed = filename.endswith('.gz')
                file_size = stat.st_size
                
                files.append({
                    'filename': filename,
                    'size': file_size,
                    'size_display': _format_file_size(file_size),
                    'is_compressed': is_compressed,
                    'file_type': 'gzip' if is_compressed else 'json',
                    'created_at': beijing_strftime(datetime.fromtimestamp(stat.st_ctime)),
                    'can_download': True,
                })
        
        files.sort(key=lambda x: x['created_at'], reverse=True)
        
        backup_type = request.query_params.get('type', '')
        if backup_type:
            if backup_type == 'compressed':
                files = [f for f in files if f['is_compressed']]
            elif backup_type == 'json':
                files = [f for f in files if not f['is_compressed']]
        
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 10))
        
        total = len(files)
        start = (page - 1) * page_size
        end = start + page_size
        files = files[start:end]
        
        return ApiResponse.success(data={'list': files, 'total': total})


class BackupDownloadView(APIView):
    """备份下载视图（仅超管）"""
    permission_classes = [IsAuthenticated, IsSuperAdmin]

    @extend_schema(description='下载备份文件')
    def get(self, request, filename):
        from django.http import FileResponse
        from django.conf import settings
        
        backup_dir = os.path.join(settings.BASE_DIR, 'backups')
        filepath = os.path.join(backup_dir, filename)
        
        if not os.path.exists(filepath):
            return ApiResponse.error(message='文件不存在', code=404)
        
        if not filename.startswith('lims_backup_'):
            return ApiResponse.error(message='无效的备份文件', code=400)
        
        content_type = 'application/gzip' if filename.endswith('.gz') else 'application/json'
        
        response = FileResponse(
            open(filepath, 'rb'),
            as_attachment=True,
            filename=filename,
            content_type=content_type
        )
        return response


class BackupDeleteView(APIView):
    """备份删除视图（仅超管）"""
    permission_classes = [IsAuthenticated, IsSuperAdmin]

    @extend_schema(description='删除备份文件')
    def delete(self, request, filename):
        from django.conf import settings
        
        backup_dir = os.path.join(settings.BASE_DIR, 'backups')
        filepath = os.path.join(backup_dir, filename)
        
        if not os.path.exists(filepath):
            return ApiResponse.error(message='文件不存在', code=404)
        
        if not filename.startswith('lims_backup_'):
            return ApiResponse.error(message='无效的备份文件', code=400)
        
        os.remove(filepath)
        return ApiResponse.success(message='备份文件已删除')


def _format_file_size(size: int) -> str:
    """格式化文件大小显示"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024:
            return f'{size:.1f} {unit}'
        size /= 1024
    return f'{size:.1f} TB'
