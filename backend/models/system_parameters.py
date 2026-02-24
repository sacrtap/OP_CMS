# OP_CMS System Parameters Model
# Story 7.1: System Parameter Configuration

from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime

from backend.models.database_models import Base


class SystemParameter(Base):
    """System parameter configuration model"""
    __tablename__ = 'system_parameters'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    key = Column(String(100), unique=True, nullable=False, index=True, comment="Parameter key")
    value = Column(Text, nullable=False, comment="Parameter value")
    value_type = Column(String(20), nullable=False, default='string', comment="Value type: string, integer, boolean, json")
    description = Column(String(500), comment="Parameter description")
    category = Column(String(50), nullable=False, default='general', index=True, comment="Category: settlement, warning, import, export, general")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="Last update timestamp")
    updated_by = Column(Integer, ForeignKey('users.id'), comment="Last update user ID")
    
    # Relationships
    updater = relationship("User", foreign_keys=[updated_by])
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'key': self.key,
            'value': self.value,
            'value_type': self.value_type,
            'description': self.description,
            'category': self.category,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'updated_by': self.updated_by
        }
    
    def get_typed_value(self):
        """Get value with correct type"""
        if self.value_type == 'integer':
            try:
                return int(self.value)
            except:
                return 0
        elif self.value_type == 'boolean':
            return self.value.lower() in ['true', '1', 'yes']
        elif self.value_type == 'json':
            import json
            try:
                return json.loads(self.value)
            except:
                return {}
        else:  # string
            return self.value
    
    def set_typed_value(self, typed_value):
        """Set value with type conversion"""
        if self.value_type == 'integer':
            self.value = str(int(typed_value))
        elif self.value_type == 'boolean':
            self.value = 'true' if typed_value else 'false'
        elif self.value_type == 'json':
            import json
            self.value = json.dumps(typed_value)
        else:  # string
            self.value = str(typed_value)
