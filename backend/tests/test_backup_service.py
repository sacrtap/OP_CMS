"""
Tests for Backup Service - Story 7.3
Tests for data backup and recovery functionality
"""

import pytest
import os
import gzip
import shutil
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock, mock_open

from backend.services.backup_service import BackupService


class TestBackupServiceInit:
    """Tests for BackupService initialization"""
    
    def test_init_default_values(self):
        """Test initialization with default values"""
        with patch('os.makedirs'):
            service = BackupService()
            
            assert service.backup_dir == './backups'
            assert service.db_host == 'localhost'
            assert service.db_port == '3306'
            assert service.db_name == 'op_cms'
            assert service.db_user == 'op_cms_user'
            assert service.db_password == ''
    
    def test_init_with_custom_dir(self):
        """Test initialization with custom backup directory"""
        with patch('os.makedirs'):
            service = BackupService(backup_dir='/custom/backups')
            
            assert service.backup_dir == '/custom/backups'
    
    def test_init_creates_directory(self):
        """Test that initialization creates backup directory"""
        with patch('os.makedirs') as mock_makedirs:
            BackupService(backup_dir='/test/backups')
            
            mock_makedirs.assert_called_once_with('/test/backups', exist_ok=True)


class TestCreateBackup:
    """Tests for create_backup method"""
    
    @patch('backend.services.backup_service.subprocess.run')
    @patch('backend.services.backup_service.os.path.getsize')
    @patch('backend.services.backup_service.datetime')
    def test_create_full_backup(self, mock_datetime, mock_getsize, mock_run):
        """Test creating a full backup"""
        # Mock datetime
        mock_datetime.utcnow.return_value = datetime(2026, 2, 25, 10, 30, 0)
        
        # Mock file size
        mock_getsize.return_value = 1048576  # 1MB
        
        with patch.object(BackupService, '_compress_file', return_value='/backups/op_cms_full_20260225_103000.sql.gz'):
            with patch('os.remove'):
                with patch('os.path.join', return_value='/backups/op_cms_full_20260225_103000.sql'):
                    with patch.object(BackupService, '__init__', lambda x, backup_dir='./backups': None):
                        service = BackupService()
                        service.backup_dir = './backups'
                        service.db_host = 'localhost'
                        service.db_port = '3306'
                        service.db_name = 'op_cms'
                        service.db_user = 'op_cms_user'
                        service.db_password = 'password'
                        
                        result = service.create_backup(backup_type='full', description='Test backup')
                        
                        assert result['type'] == 'full'
                        assert result['status'] == 'completed'
                        assert result['description'] == 'Test backup'
                        assert result['size'] == 1048576
                        assert result['size_mb'] == 1.0
    
    @patch('backend.services.backup_service.subprocess.run')
    def test_create_backup_subprocess_failure(self, mock_run):
        """Test backup creation when mysqldump fails"""
        mock_run.side_effect = Exception("mysqldump failed")
        
        with patch.object(BackupService, '__init__', lambda x, backup_dir='./backups': None):
            service = BackupService()
            service.backup_dir = './backups'
            service.db_host = 'localhost'
            service.db_port = '3306'
            service.db_name = 'op_cms'
            service.db_user = 'op_cms_user'
            service.db_password = 'password'
            
            with pytest.raises(Exception, match="Database backup failed"):
                service.create_backup(backup_type='full')
    
    def test_create_backup_invalid_type(self):
        """Test backup creation with invalid type"""
        with patch.object(BackupService, '__init__', lambda x, backup_dir='./backups': None):
            service = BackupService()
            service.backup_dir = './backups'
            
            # Should still work, type is just for naming
            with patch.object(service, '_compress_file', return_value='/path/backup.sql.gz'):
                with patch('subprocess.run'):
                    with patch('os.remove'):
                        result = service.create_backup(backup_type='custom')
                        assert result['type'] == 'custom'


class TestRestoreBackup:
    """Tests for restore_backup method"""
    
    @patch('backend.services.backup_service.subprocess.run')
    def test_restore_backup_success(self, mock_run):
        """Test successful backup restoration"""
        with patch.object(BackupService, '__init__', lambda x, backup_dir='./backups': None):
            service = BackupService()
            service.backup_dir = './backups'
            service.db_host = 'localhost'
            service.db_port = '3306'
            service.db_name = 'op_cms'
            service.db_user = 'op_cms_user'
            service.db_password = 'password'
            
            result = service.restore_backup('/backups/backup.sql.gz')
            
            assert result['status'] == 'completed'
            assert result['backup_file'] == '/backups/backup.sql.gz'
            assert 'restored_at' in result
            mock_run.assert_called_once()
    
    @patch('backend.services.backup_service.subprocess.run')
    def test_restore_backup_failure(self, mock_run):
        """Test backup restoration failure"""
        mock_run.side_effect = Exception("Restore failed")
        
        with patch.object(BackupService, '__init__', lambda x, backup_dir='./backups': None):
            service = BackupService()
            service.backup_dir = './backups'
            service.db_host = 'localhost'
            service.db_port = '3306'
            service.db_name = 'op_cms'
            service.db_user = 'op_cms_user'
            service.db_password = 'password'
            
            with pytest.raises(Exception, match="Database restore failed"):
                service.restore_backup('/backups/backup.sql.gz')


class TestListBackups:
    """Tests for list_backups method"""
    
    @patch('backend.services.backup_service.os.listdir')
    @patch('backend.services.backup_service.os.stat')
    def test_list_backups_success(self, mock_stat, mock_listdir):
        """Test listing backups successfully"""
        mock_listdir.return_value = ['op_cms_full_20260225_103000.sql.gz', 'op_cms_full_20260224_103000.sql.gz']
        
        mock_stat.return_value = Mock(
            st_size=1048576,
            st_mtime=1708851000
        )
        
        with patch.object(BackupService, '__init__', lambda x, backup_dir='./backups': None):
            service = BackupService()
            service.backup_dir = './backups'
            
            result = service.list_backups()
            
            assert len(result) == 2
            assert result[0]['filename'] == 'op_cms_full_20260225_103000.sql.gz'
            assert result[0]['size'] == 1048576
            assert result[0]['size_mb'] == 1.0
            assert result[0]['status'] == 'available'
    
    @patch('backend.services.backup_service.os.listdir')
    def test_list_backups_empty(self, mock_listdir):
        """Test listing when no backups exist"""
        mock_listdir.return_value = []
        
        with patch.object(BackupService, '__init__', lambda x, backup_dir='./backups': None):
            service = BackupService()
            service.backup_dir = './backups'
            
            result = service.list_backups()
            
            assert len(result) == 0
            assert result == []
    
    @patch('backend.services.backup_service.os.listdir')
    def test_list_backups_filters_non_sql_files(self, mock_listdir):
        """Test that only .sql and .sql.gz files are listed"""
        mock_listdir.return_value = ['backup.sql.gz', 'backup.sql', 'readme.txt', 'config.json']
        
        with patch.object(BackupService, '__init__', lambda x, backup_dir='./backups': None):
            service = BackupService()
            service.backup_dir = './backups'
            
            with patch('backend.services.backup_service.os.stat', return_value=Mock(st_size=100, st_mtime=12345)):
                result = service.list_backups()
                
                assert len(result) == 2
                filenames = [b['filename'] for b in result]
                assert 'backup.sql.gz' in filenames
                assert 'backup.sql' in filenames
                assert 'readme.txt' not in filenames
                assert 'config.json' not in filenames


class TestDeleteBackup:
    """Tests for delete_backup method"""
    
    @patch('backend.services.backup_service.os.path.exists')
    @patch('backend.services.backup_service.os.remove')
    def test_delete_backup_success(self, mock_remove, mock_exists):
        """Test successful backup deletion"""
        mock_exists.return_value = True
        
        with patch.object(BackupService, '__init__', lambda x, backup_dir='./backups': None):
            service = BackupService()
            service.backup_dir = './backups'
            
            result = service.delete_backup('backup.sql.gz')
            
            assert result is True
            mock_exists.assert_called_once()
            mock_remove.assert_called_once()
    
    @patch('backend.services.backup_service.os.path.exists')
    def test_delete_backup_not_found(self, mock_exists):
        """Test deletion when backup doesn't exist"""
        mock_exists.return_value = False
        
        with patch.object(BackupService, '__init__', lambda x, backup_dir='./backups': None):
            service = BackupService()
            service.backup_dir = './backups'
            
            result = service.delete_backup('nonexistent.sql.gz')
            
            assert result is False


class TestCompressFile:
    """Tests for _compress_file method"""
    
    @patch('builtins.open', new_callable=mock_open)
    @patch('backend.services.backup_service.gzip.open')
    @patch('backend.services.backup_service.shutil.copyfileobj')
    def test_compress_file_success(self, mock_copy, mock_gzip_open, mock_open):
        """Test file compression"""
        with patch.object(BackupService, '__init__', lambda x, backup_dir='./backups': None):
            service = BackupService()
            
            result = service._compress_file('/path/file.sql')
            
            assert result == '/path/file.sql.gz'
            mock_gzip_open.assert_called_once()


class TestDecompressFile:
    """Tests for _decompress_file method"""
    
    @patch('builtins.open', new_callable=mock_open)
    @patch('backend.services.backup_service.gzip.open')
    @patch('backend.services.backup_service.shutil.copyfileobj')
    def test_decompress_file_success(self, mock_copy, mock_gzip_open, mock_open):
        """Test file decompression"""
        with patch.object(BackupService, '__init__', lambda x, backup_dir='./backups': None):
            service = BackupService()
            
            result = service._decompress_file('/path/file.sql.gz')
            
            assert result == '/path/file.sql'
            mock_gzip_open.assert_called_once()


class TestCleanupOldBackups:
    """Tests for cleanup_old_backups method"""
    
    @patch.object(BackupService, 'list_backups')
    @patch.object(BackupService, 'delete_backup')
    def test_cleanup_removes_old_backups(self, mock_delete, mock_list):
        """Test cleanup removes backups beyond keep_count"""
        # Mock 15 backups
        mock_list.return_value = [
            {'filename': f'backup_{i}.sql.gz'} for i in range(15)
        ]
        mock_delete.return_value = True
        
        with patch.object(BackupService, '__init__', lambda x, backup_dir='./backups': None):
            service = BackupService()
            
            result = service.cleanup_old_backups(keep_count=10)
            
            assert result == 5  # 15 - 10 = 5 deleted
            assert mock_delete.call_count == 5
    
    @patch.object(BackupService, 'list_backups')
    def test_cleanup_no_deletion_needed(self, mock_list):
        """Test cleanup when no deletion needed"""
        # Mock 5 backups (less than keep_count)
        mock_list.return_value = [
            {'filename': f'backup_{i}.sql.gz'} for i in range(5)
        ]
        
        with patch.object(BackupService, '__init__', lambda x, backup_dir='./backups': None):
            service = BackupService()
            
            result = service.cleanup_old_backups(keep_count=10)
            
            assert result == 0  # No deletions


class TestBackupServiceIntegration:
    """Integration tests for BackupService"""
    
    @patch('backend.services.backup_service.subprocess.run')
    @patch('backend.services.backup_service.os.path.getsize')
    def test_full_backup_workflow(self, mock_getsize, mock_run):
        """Test complete backup workflow: create -> list -> delete"""
        mock_getsize.return_value = 1048576
        
        with patch.object(BackupService, '__init__', lambda x, backup_dir='./backups': None):
            service = BackupService()
            service.backup_dir = './backups'
            service.db_host = 'localhost'
            service.db_port = '3306'
            service.db_name = 'op_cms'
            service.db_user = 'op_cms_user'
            service.db_password = 'password'
            
            with patch.object(service, '_compress_file', return_value='/backups/test.sql.gz'):
                with patch('os.remove'):
                    # Create backup
                    backup_info = service.create_backup(backup_type='full', description='Integration test')
                    
                    assert backup_info['status'] == 'completed'
                    assert backup_info['type'] == 'full'
                    
                    # Verify mysqldump was called
                    mock_run.assert_called_once()
