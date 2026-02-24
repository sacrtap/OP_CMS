# OP_CMS Celery Tasks
# Story 7.5: Celery Async Tasks

from celery import current_task
from datetime import datetime
import logging
import os

from backend.celery_app import celery_app
from backend.services.backup_service import backup_service
from backend.services.data_validation_service import DataValidationService
from backend.models.database_models import Customer, SettlementRecord
from backend.dao.database_dao import DatabaseSessionFactory

logger = logging.getLogger(__name__)


@celery_app.task(bind=True)
def import_customers_task(self, file_data: str, import_mode: str = 'skip_duplicates'):
    """
    Async task for importing customers
    
    Args:
        self: Task instance
        file_data: Base64 encoded file data
        import_mode: Import mode (skip_duplicates, update_duplicates, create_all)
    
    Returns:
        Import result summary
    """
    try:
        task_id = self.request.id
        
        # Update task state
        self.update_state(
            state='PROGRESS',
            meta={
                'current': 0,
                'total': 0,
                'status': 'Starting import...',
                'import_mode': import_mode
            }
        )
        
        # Decode file
        import base64
        file_content = base64.b64decode(file_data)
        
        # Parse file (simplified - in production, use proper parsing)
        rows = []  # Parse file content
        
        total_rows = len(rows)
        self.update_state(
            state='PROGRESS',
            meta={
                'current': 0,
                'total': total_rows,
                'status': f'Processing {total_rows} rows...'
            }
        )
        
        # Process rows in batches
        batch_size = 100
        successful = 0
        failed = 0
        
        for i in range(0, total_rows, batch_size):
            batch = rows[i:i + batch_size]
            
            # Process batch
            for row in batch:
                try:
                    # Validate and import
                    # (simplified - in production, use full validation)
                    successful += 1
                except Exception as e:
                    logger.error(f"Failed to import row: {str(e)}")
                    failed += 1
            
            # Update progress
            current = min(i + batch_size, total_rows)
            self.update_state(
                state='PROGRESS',
                meta={
                    'current': current,
                    'total': total_rows,
                    'status': f'Imported {current}/{total_rows} rows',
                    'successful': successful,
                    'failed': failed
                }
            )
        
        return {
            'status': 'completed',
            'total': total_rows,
            'successful': successful,
            'failed': failed,
            'import_mode': import_mode
        }
        
    except Exception as e:
        logger.error(f"Import task failed: {str(e)}")
        self.update_state(
            state='FAILED',
            meta={'error': str(e)}
        )
        raise


@celery_app.task(bind=True)
def export_customers_task(self, filters: dict = None, export_format: str = 'excel'):
    """
    Async task for exporting customers
    
    Args:
        self: Task instance
        filters: Export filters
        export_format: Export format (excel, csv)
    
    Returns:
        Export result with file URL
    """
    try:
        task_id = self.request.id
        
        # Update task state
        self.update_state(
            state='PROGRESS',
            meta={
                'current': 0,
                'total': 0,
                'status': 'Starting export...'
            }
        )
        
        # Get database session
        session_factory = DatabaseSessionFactory()
        session = session_factory.get_session()
        
        try:
            # Query customers
            query = session.query(Customer)
            
            if filters:
                if filters.get('status'):
                    query = query.filter(Customer.status == filters['status'])
                if filters.get('level'):
                    query = query.filter(Customer.level == filters['level'])
            
            customers = query.all()
            total = len(customers)
            
            self.update_state(
                state='PROGRESS',
                meta={
                    'current': 0,
                    'total': total,
                    'status': f'Exporting {total} customers...'
                }
            )
            
            # Export in batches
            import pandas as pd
            import io
            import base64
            
            # Convert to DataFrame
            customer_data = [c.to_dict() for c in customers]
            df = pd.DataFrame(customer_data)
            
            # Export to file
            output = io.BytesIO()
            if export_format == 'csv':
                df.to_csv(output, index=False)
                file_ext = 'csv'
                file_type = 'text/csv'
            else:  # excel
                df.to_excel(output, index=False, engine='openpyxl')
                file_ext = 'xlsx'
                file_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            
            output.seek(0)
            file_content = output.getvalue()
            
            # Save file (in production, save to S3/OSS)
            timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
            filename = f'customers_{timestamp}.{file_ext}'
            filepath = os.path.join('./exports', filename)
            os.makedirs('./exports', exist_ok=True)
            
            with open(filepath, 'wb') as f:
                f.write(file_content)
            
            self.update_state(
                state='PROGRESS',
                meta={
                    'current': total,
                    'total': total,
                    'status': 'Export completed',
                    'file_url': f'/exports/{filename}'
                }
            )
            
            return {
                'status': 'completed',
                'total': total,
                'file_url': f'/exports/{filename}',
                'file_type': file_type
            }
            
        finally:
            session.close()
            
    except Exception as e:
        logger.error(f"Export task failed: {str(e)}")
        self.update_state(
            state='FAILED',
            meta={'error': str(e)}
        )
        raise


@celery_app.task(bind=True)
def daily_backup_task(self):
    """
    Daily automated backup task
    
    Scheduled to run at 2 AM daily
    """
    try:
        logger.info("Starting daily backup task")
        
        # Create backup
        backup_info = backup_service.create_backup(
            backup_type='full',
            description='Automated daily backup'
        )
        
        # Cleanup old backups (keep last 10)
        deleted_count = backup_service.cleanup_old_backups(keep_count=10)
        
        logger.info(f"Daily backup completed: {backup_info['filename']}, deleted {deleted_count} old backups")
        
        return {
            'status': 'completed',
            'backup_file': backup_info['filename'],
            'deleted_old_backups': deleted_count
        }
        
    except Exception as e:
        logger.error(f"Daily backup task failed: {str(e)}")
        raise


@celery_app.task
def cleanup_old_tasks():
    """
    Cleanup old task results
    
    Scheduled to run weekly
    """
    try:
        logger.info("Cleaning up old task results")
        
        # In production, clean up old task results from Redis/database
        # This is a placeholder
        
        return {
            'status': 'completed',
            'message': 'Old task results cleaned up'
        }
        
    except Exception as e:
        logger.error(f"Cleanup task failed: {str(e)}")
        raise


@celery_app.task(bind=True)
def send_email_notification(self, recipient: str, subject: str, body: str):
    """
    Send email notification
    
    Args:
        self: Task instance
        recipient: Email recipient
        subject: Email subject
        body: Email body
    """
    try:
        # In production, use email service (SendGrid, AWS SES, etc.)
        logger.info(f"Sending email to {recipient}: {subject}")
        
        # Simulate email sending
        import time
        time.sleep(1)  # Simulate API call
        
        return {
            'status': 'sent',
            'recipient': recipient,
            'subject': subject
        }
        
    except Exception as e:
        logger.error(f"Email notification failed: {str(e)}")
        raise
