# OP_CMS Payment and Writeoff Models
# Story 3.4: Settlement Payment Writeoff

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, DECIMAL, Text
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from backend.models.database_models import Base


class PaymentRecord(Base):
    """Payment record for customer payments"""
    __tablename__ = 'payment_records'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    payment_no = Column(String(36), unique=True, nullable=False, comment="Payment number (UUID)")
    customer_id = Column(Integer, ForeignKey('customers.id'), nullable=False, comment="Customer ID")
    
    # Payment details
    payment_amount = Column(DECIMAL(12, 2), nullable=False, comment="Payment amount")
    payment_method = Column(String(50), nullable=False, comment="Payment method: bank_transfer, cash, check, online")
    payment_date = Column(DateTime, nullable=False, comment="Payment date")
    payment_account = Column(String(100), comment="Bank account or payment account")
    
    # Additional info
    attachment_url = Column(String(500), comment="Attachment URL (bank receipt)")
    remarks = Column(Text, comment="Remarks")
    
    # Audit
    created_by = Column(Integer, ForeignKey('users.id'), comment="Created by user ID")
    created_at = Column(DateTime, default=datetime.utcnow, comment="Creation timestamp")
    
    # Relationships
    customer = relationship("Customer", backref="payments")
    creator = relationship("User", foreign_keys=[created_by])
    writeoffs = relationship("SettlementWriteoff", back_populates="payment")
    
    def generate_payment_no(self):
        """Generate unique payment number"""
        self.payment_no = f"PAY-{uuid.uuid4()}"
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'payment_no': self.payment_no,
            'customer_id': self.customer_id,
            'payment_amount': float(self.payment_amount) if self.payment_amount else None,
            'payment_method': self.payment_method,
            'payment_date': self.payment_date.isoformat() if self.payment_date else None,
            'payment_account': self.payment_account,
            'attachment_url': self.attachment_url,
            'remarks': self.remarks,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class SettlementWriteoff(Base):
    """Settlement writeoff record (matching payment to settlement)"""
    __tablename__ = 'settlement_writeoffs'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    writeoff_no = Column(String(36), unique=True, nullable=False, comment="Writeoff number (UUID)")
    
    # Foreign keys
    payment_id = Column(Integer, ForeignKey('payment_records.id'), nullable=False, comment="Payment ID")
    settlement_id = Column(Integer, ForeignKey('settlement_records.id'), nullable=False, comment="Settlement ID")
    
    # Writeoff details
    writeoff_amount = Column(DECIMAL(12, 2), nullable=False, comment="Writeoff amount")
    writeoff_type = Column(String(20), nullable=False, comment="Writeoff type: full, partial, merged")
    writeoff_date = Column(DateTime, default=datetime.utcnow, comment="Writeoff timestamp")
    
    # Audit
    created_by = Column(Integer, ForeignKey('users.id'), comment="Created by user ID")
    
    # Relationships
    payment = relationship("PaymentRecord", back_populates="writeoffs")
    settlement = relationship("SettlementRecord", backref="writeoffs")
    creator = relationship("User", foreign_keys=[created_by])
    
    def generate_writeoff_no(self):
        """Generate unique writeoff number"""
        self.writeoff_no = f"WOF-{uuid.uuid4()}"
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'writeoff_no': self.writeoff_no,
            'payment_id': self.payment_id,
            'settlement_id': self.settlement_id,
            'writeoff_amount': float(self.writeoff_amount) if self.writeoff_amount else None,
            'writeoff_type': self.writeoff_type,
            'writeoff_date': self.writeoff_date.isoformat() if self.writeoff_date else None,
            'created_by': self.created_by
        }
