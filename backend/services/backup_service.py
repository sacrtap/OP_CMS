# OP_CMS Data Backup Service
# Story 7.3: Data Backup & Recovery

import os
import subprocess
import gzip
import shutil
from datetime import datetime
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class BackupService:
    """Service for database and file backup operations"""
    
    def __init__(self, backup_dir: str = './backups'):
        self.backup_dir = backup_dir
        self.db_host = os.getenv('DB_HOST', 'localhost')
        self.db_port = os.getenv('DB_PORT', '3306')
        self.db_name = os.getenv('DB_NAME', 'op_cms')
        self.db_user = os.getenv('DB_USER', 'op_cms_user')
        self.db_password = os.getenv('DB_PASSWORD', '')
        
        # Ensure backup directory exists
        os.makedirs(self.backup_dir, exist_ok=True)
    
    def create_backup(self, backup_type: str = 'full', description: str = '') -> Dict[str, Any]:
        """
        Create database backup
        
        Args:
            backup_type: Type of backup (full, incremental)
            description: Backup description
            
        Returns:
            Backup information
        """
        try:
            timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
            backup_filename = f'{self.db_name}_{backup_type}_{timestamp}.sql'
            backup_path = os.path.join(self.backup_dir, backup_filename)
            
            # Create mysqldump command
            dump_cmd = [
                'mysqldump',
                f'--host={self.db_host}',
                f'--port={self.db_port}',
                f'--user={self.db_user}',
                f'--password={self.db_password}',
                '--single-transaction',
                '--routines',
                '--triggers',
                self.db_name
            ]
            
            # Execute dump
            logger.info(f"Creating backup: {backup_path}")
            with open(backup_path, 'w') as f:
                subprocess.run(dump_cmd, stdout=f, check=True)
            
            # Compress backup
            compressed_path = self._compress_file(backup_path)
            
            # Remove uncompressed file
            os.remove(backup_path)
            
            # Get file size
            file_size = os.path.getsize(compressed_path)
            
            backup_info = {
                'filename': os.path.basename(compressed_path),
                'path': compressed_path,
                'type': backup_type,
                'size': file_size,
                'size_mb': round(file_size / (1024 * 1024), 2),
                'description': description,
                'created_at': datetime.utcnow().isoformat(),
                'status': 'completed'
            }
            
            logger.info(f"Backup created successfully: {backup_info['filename']} ({backup_info['size_mb']} MB)")
            
            return backup_info
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Backup failed: {str(e)}")
            raise Exception(f"Database backup failed: {str(e)}")
        except Exception as e:
            logger.error(f"Backup failed: {str(e)}")
            raise
    
    def restore_backup(self, backup_path: str) -> Dict[str, Any]:
        """
        Restore database from backup
        
        Args:
            backup_path: Path to backup file
            
        Returns:
            Restore information
        """
        try:
            logger.info(f"Restoring backup: {backup_path}")
            
            # Decompress if needed
            if backup_path.endswith('.gz'):
                decompressed_path = self._decompress_file(backup_path)
            else:
                decompressed_path = backup_path
            
            # Create mysql command
            restore_cmd = [
                'mysql',
                f'--host={self.db_host}',
                f'--port={self.db_port}',
                f'--user={self.db_user}',
                f'--password={self.db_password}',
                self.db_name
            ]
            
            # Execute restore
            with open(decompressed_path, 'r') as f:
                subprocess.run(restore_cmd, stdin=f, check=True)
            
            # Remove decompressed file if it was compressed
            if backup_path.endswith('.gz'):
                os.remove(decompressed_path)
            
            restore_info = {
                'backup_file': backup_path,
                'status': 'completed',
                'restored_at': datetime.utcnow().isoformat(),
                'message': 'Database restored successfully'
            }
            
            logger.info(f"Backup restored successfully: {backup_path}")
            
            return restore_info
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Restore failed: {str(e)}")
            raise Exception(f"Database restore failed: {str(e)}")
        except Exception as e:
            logger.error(f"Restore failed: {str(e)}")
            raise
    
    def list_backups(self) -> List[Dict[str, Any]]:
        """
        List all backups
        
        Returns:
            List of backup information
        """
        backups = []
        
        try:
            for filename in os.listdir(self.backup_dir):
                if filename.endswith('.sql.gz') or filename.endswith('.sql'):
                    file_path = os.path.join(self.backup_dir, filename)
                    file_stat = os.stat(file_path)
                    
                    # Parse backup info from filename
                    parts = filename.replace('.sql.gz', '').replace('.sql', '').split('_')
                    backup_type = parts[-2] if len(parts) > 2 else 'full'
                    
                    backups.append({
                        'filename': filename,
                        'path': file_path,
                        'type': backup_type,
                        'size': file_stat.st_size,
                        'size_mb': round(file_stat.st_size / (1024 * 1024), 2),
                        'created_at': datetime.fromtimestamp(file_stat.st_mtime).isoformat(),
                        'status': 'available'
                    })
            
            # Sort by creation time (newest first)
            backups.sort(key=lambda x: x['created_at'], reverse=True)
            
        except Exception as e:
            logger.error(f"Failed to list backups: {str(e)}")
        
        return backups
    
    def delete_backup(self, backup_filename: str) -> bool:
        """
        Delete backup file
        
        Args:
            backup_filename: Name of backup file to delete
            
        Returns:
            True if deleted successfully
        """
        try:
            backup_path = os.path.join(self.backup_dir, backup_filename)
            
            if os.path.exists(backup_path):
                os.remove(backup_path)
                logger.info(f"Backup deleted: {backup_filename}")
                return True
            else:
                logger.warning(f"Backup not found: {backup_filename}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to delete backup: {str(e)}")
            raise
    
    def _compress_file(self, file_path: str) -> str:
        """Compress file using gzip"""
        compressed_path = file_path + '.gz'
        
        with open(file_path, 'rb') as f_in:
            with gzip.open(compressed_path, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        
        return compressed_path
    
    def _decompress_file(self, file_path: str) -> str:
        """Decompress gzip file"""
        decompressed_path = file_path[:-3]  # Remove .gz
        
        with gzip.open(file_path, 'rb') as f_in:
            with open(decompressed_path, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        
        return decompressed_path
    
    def cleanup_old_backups(self, keep_count: int = 10) -> int:
        """
        Delete old backups, keeping only the most recent ones
        
        Args:
            keep_count: Number of backups to keep
            
        Returns:
            Number of backups deleted
        """
        backups = self.list_backups()
        deleted = 0
        
        # Delete backups beyond keep_count
        if len(backups) > keep_count:
            for backup in backups[keep_count:]:
                if self.delete_backup(backup['filename']):
                    deleted += 1
        
        logger.info(f"Cleaned up {deleted} old backups, keeping {keep_count} most recent")
        return deleted


# Global backup service instance
backup_service = BackupService()
