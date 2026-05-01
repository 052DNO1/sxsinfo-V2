import pytest
from tests.blackbox.client import (
    assert_success_response, assert_error_response,
    extract_data,
)
from tests.blackbox.config import API_ENDPOINTS


class TestBackupStats:
    def test_get_backup_stats(self, authed_client):
        url = API_ENDPOINTS['backups']['stats']
        response = authed_client.get(url)
        assert response.status_code == 200


class TestBackupExport:
    def test_export_backup(self, authed_client):
        url = API_ENDPOINTS['backups']['export']
        response = authed_client.get(url)
        assert response.status_code in (200, 202)

    def test_export_backup_with_compress(self, authed_client):
        url = API_ENDPOINTS['backups']['export']
        response = authed_client.get(url, {'compress': True})
        assert response.status_code in (200, 202)


class TestBackupRestore:
    def test_restore_without_file(self, authed_client):
        url = API_ENDPOINTS['backups']['restore']
        response = authed_client.post(url)
        assert response.status_code in (400, 200)


class TestBackupAutoConfig:
    def test_get_auto_config(self, authed_client):
        url = API_ENDPOINTS['backups']['auto_config']
        response = authed_client.get(url)
        assert response.status_code == 200

    def test_set_auto_config(self, authed_client):
        url = API_ENDPOINTS['backups']['auto_config']
        response = authed_client.post(url, {
            'enabled': True,
            'period': 'weekly',
        })
        assert response.status_code == 200

    def test_set_auto_config_invalid_period(self, authed_client):
        url = API_ENDPOINTS['backups']['auto_config']
        response = authed_client.post(url, {
            'enabled': True,
            'period': 'invalid_period',
        })
        assert response.status_code in (200, 400)


class TestBackupList:
    def test_get_backup_list(self, authed_client):
        url = API_ENDPOINTS['backups']['list']
        response = authed_client.get(url)
        assert response.status_code == 200

    def test_get_backup_list_with_pagination(self, authed_client):
        url = API_ENDPOINTS['backups']['list']
        response = authed_client.get(url, {'page': 1, 'page_size': 10})
        assert response.status_code == 200

    def test_get_backup_list_filter_by_type(self, authed_client):
        url = API_ENDPOINTS['backups']['list']
        response = authed_client.get(url, {'type': 'manual'})
        assert response.status_code == 200


class TestBackupDownloadDelete:
    def test_download_nonexistent_backup(self, authed_client):
        url = API_ENDPOINTS['backups']['download'].format(filename='nonexistent.tar.gz')
        response = authed_client.get(url)
        assert response.status_code in (404, 400)

    def test_delete_nonexistent_backup(self, authed_client):
        url = API_ENDPOINTS['backups']['delete'].format(filename='nonexistent.tar.gz')
        response = authed_client.delete(url)
        assert response.status_code in (404, 400, 200)
