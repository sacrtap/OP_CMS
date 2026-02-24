# OP_CMS Reminder Models
# Story 3.5: Overdue Reminder Functionality

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta
import uuid

from backend.models.database_models import Base


class ReminderRecord(Base):
    """Reminder record for overdue settlements"""
    __tablename__ = 'reminder_records'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    reminder_no = Column(String(36), unique=True, nullable=False, comment="Reminder number (UUID)")
    
    # Foreign keys
    settlement_id = Column(Integer, ForeignKey('settlement_records.id'), nullable=False, comment="Settlement ID")
    customer_id = Column(Integer, ForeignKey('customers.id'), nullable=False, comment="Customer ID")
    
    # Reminder details
    reminder_type = Column(String(20), nullable=False, comment="Reminder type: email, sms, phone")
    reminder_method = Column(String(50), comment="Reminder method: email_template, sms_template")
    recipient = Column(String(255), nullable=False, comment="Recipient (email or phone)")
    reminder_content = Column(Text, comment="Reminder content")
    
    # Status
    send_status = Column(String(20), nullable=False, default='pending', comment="Send status: pending, sent, delivered, failed")
    sent_at = Column(DateTime, comment="Sent timestamp")
    reminder_count = Column(Integer, default=1, comment="Reminder count (1st, 2nd, 3rd...)")
    
    # Audit
    created_by = Column(Integer, ForeignKey('users.id'), comment="Created by user ID")
    created_at = Column(DateTime, default=datetime.utcnow, comment="Creation timestamp")
    
    # Relationships
    settlement = relationship("SettlementRecord", backref="reminders")
    customer = relationship("Customer", backref="reminders")
    creator = relationship("User", foreign_keys=[created_by])
    
    def generate_reminder_no(self):
        """Generate unique reminder number"""
        self.reminder_no = f"REM-{uuid.uuid4()}"
    
    def is_overdue(self, days_threshold: int = 30) -> bool:
        """Check if settlement is overdue beyond threshold"""
        if not self.settlement or not self.settlement.created_at:
            return False
        
        due_date = self.settlement.created_at + timedelta(days=30)  # Assuming 30-day payment term
        return datetime.utcnow() > due_date + timedelta(days=days_threshold)
    
    def get_overdue_days(self) -> int:
        """Get number of overdue days"""
        if not self.settlement or not self.settlement.created_at:
            return 0
        
        due_date = self.settlement.created_at + timedelta(days=30)  # 30-day payment term
        overdue = datetime.utcnow() - due_date
        return max(0, overdue.days)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'reminder_no': self.reminder_no,
            'settlement_id': self.settlement_id,
            'customer_id': self.customer_id,
            'reminder_type': self.reminder_type,
            'reminder_method': self.reminder_method,
            'recipient': self.recipient,
            'reminder_content': self.reminder_content,
            'send_status': self.send_status,
            'sent_at': self.sent_at.isoformat() if self.sent_at else None,
            'reminder_count': self.reminder_count,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'overdue_days': self.get_overdue_days(),
            'is_overdue': self.is_overdue()
        }
