# OP_CMS Database Access Layer (DAO)
# MySQL 8.0+ Implementation
# Python SQLAlchemy DAO Pattern

"""
OP_CMS Database Access Layer (DAO)

This module implements the Data Access Object (DAO) pattern for database operations.
It provides a clean separation between business logic and database access.

Pattern: Repository Pattern with SQLAlchemy ORM
Database: MySQL 8.0+
Programming Language: Python 3.9+
"""

from typing import Optional, List, Dict, Any, TypeVar, Generic, Type
from sqlalchemy.orm import Session
from sqlalchemy import select, update, delete, func, and_, or_
from .database_models import Base, Customer, PriceConfig, SettlementRecord


# Type variables for generic DAO
T = TypeVar('T', bound=Base)


class BaseDAO(Generic[T]):
    """Base DAO class with common CRUD operations"""
    
    def __init__(self, session: Session, model_class: Type[T]):
        self.session = session
        self.model_class = model_class
    
    def get_by_id(self, id: int) -> Optional[T]:
        """Get record by ID"""
        return self.session.query(self.model_class).filter(
            self.model_class.id == id
        ).first()
    
    def get_by_customer_id(self, customer_id: str) -> Optional[T]:
        """Get record by customer_id (UUID)"""
        return self.session.query(self.model_class).filter(
            self.model_class.customer_id == customer_id
        ).first()
    
    def get_all(self, limit: int = 100, offset: int = 0) -> List[T]:
        """Get all records with pagination"""
        query = select(self.model_class).offset(offset).limit(limit)
        result = self.session.execute(query)
        return result.scalars().all()
    
    def create(self, entity: T) -> T:
        """Create new record"""
        self.session.add(entity)
        self.session.commit()
        self.session.refresh(entity)
        return entity
    
    def update(self, entity: T) -> T:
        """Update existing record"""
        self.session.commit()
        self.session.refresh(entity)
        return entity
    
    def delete(self, entity: T) -> bool:
        """Delete record"""
        self.session.delete(entity)
        self.session.commit()
        return True
    
    def bulk_create(self, entities: List[T]) -> List[T]:
        """Bulk create records"""
        self.session.add_all(entities)
        self.session.commit()
        for entity in entities:
            self.session.refresh(entity)
        return entities


class CustomerDAO(BaseDAO[Customer]):
    """Customer DAO with specific operations"""
    
    def __init__(self, session: Session):
        super().__init__(session, Customer)
    
    def get_by_customer_id(self, customer_id: str) -> Optional[Customer]:
        """Get customer by customer_id (UUID)"""
        return self.session.query(Customer).filter(
            Customer.customer_id == customer_id
        ).first()
    
    def get_by_name(self, name: str) -> List[Customer]:
        """Get customers by name (fuzzy search)"""
        return self.session.query(Customer).filter(
            Customer.name.contains(name)
        ).all()
    
    def get_by_status(self, status: str) -> List[Customer]:
        """Get customers by status"""
        return self.session.query(Customer).filter(
            Customer.status == status
        ).all()
    
    def get_active_customers(self) -> List[Customer]:
        """Get all active customers"""
        return self.session.query(Customer).filter(
            Customer.status == 'active'
        ).all()


class PriceConfigDAO(BaseDAO[PriceConfig]):
    """Price Configuration DAO with specific operations"""
    
    def __init__(self, session: Session):
        super().__init__(session, PriceConfig)
    
    def get_by_customer_id(self, customer_id: int) -> List[PriceConfig]:
        """Get price configs by customer ID"""
        return self.session.query(PriceConfig).filter(
            PriceConfig.customer_id == customer_id
        ).all()
    
    def get_active_configs(self) -> List[PriceConfig]:
        """Get all active price configurations"""
        return self.session.query(PriceConfig).filter(
            PriceConfig.is_active == True
        ).all()
    
    def get_config_by_model(
        self, customer_id: int, price_model: str
    ) -> Optional[PriceConfig]:
        """Get price config by customer and model type"""
        return self.session.query(PriceConfig).filter(
            and_(
                PriceConfig.customer_id == customer_id,
                PriceConfig.price_model == price_model
            )
        ).first()


class SettlementRecordDAO(BaseDAO[SettlementRecord]):
    """Settlement Record DAO with specific operations"""
    
    def __init__(self, session: Session):
        super().__init__(session, SettlementRecord)
    
    def get_by_customer_id(self, customer_id: int) -> List[SettlementRecord]:
        """Get settlement records by customer ID"""
        return self.session.query(SettlementRecord).filter(
            SettlementRecord.customer_id == customer_id
        ).all()
    
    def get_by_period(
        self, period_start: str, period_end: str
    ) -> List[SettlementRecord]:
        """Get settlement records by period"""
        return self.session.query(SettlementRecord).filter(
            and_(
                SettlementRecord.period_start >= period_start,
                SettlementRecord.period_end <= period_end
            )
        ).all()
    
    def get_by_status(self, status: str) -> List[SettlementRecord]:
        """Get settlement records by status"""
        return self.session.query(SettlementRecord).filter(
            SettlementRecord.status == status
        ).all()
    
    def get_pending_settlements(self) -> List[SettlementRecord]:
        """Get all pending settlement records"""
        return self.session.query(SettlementRecord).filter(
            SettlementRecord.status == 'pending'
        ).all()
    
    def update_status(
        self, record_id: str, status: str, approved_at: Optional[str] = None,
        paid_at: Optional[str] = None
    ) -> bool:
        """Update settlement record status"""
        stmt = update(SettlementRecord).where(
            SettlementRecord.record_id == record_id
        ).values(status=status)
        
        if approved_at:
            stmt = stmt.values(approved_at=approved_at)
        if paid_at:
            stmt = stmt.values(paid_at=paid_at)
        
        result = self.session.execute(stmt)
        self.session.commit()
        return result.rowcount > 0


# Database session factory
class DatabaseSessionFactory:
    """Factory for creating database sessions"""
    
    def __init__(self, connection_string: str):
        self.connection_string = connection_string
        self.engine = None
        self.SessionLocal = None
    
    def initialize(self, connection_string: str = None):
        """Initialize database connection"""
        if connection_string:
            self.connection_string = connection_string
        
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        
        self.engine = create_engine(self.connection_string, pool_pre_ping=True)
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )
    
    def get_session(self) -> Session:
        """Get database session"""
        if self.SessionLocal is None:
            raise RuntimeError("Database not initialized. Call initialize() first.")
        return self.SessionLocal() 
    
    def close(self):
        """Close database connection"""
        if self.engine:
            self.engine.dispose()


# Usage example
"""
# Example usage of DAOs

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Create database connection
engine = create_engine(
    "mysql+pymysql://user:password@localhost:3306/op_cms",
    pool_pre_ping=True
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Get session
session = SessionLocal()

# Create DAO instances
customer_dao = CustomerDAO(session)
price_config_dao = PriceConfigDAO(session)
settlement_dao = SettlementRecordDAO(session)

# Example: Get all active customers
active_customers = customer_dao.get_active_customers()

# Example: Create new customer
new_customer = Customer(
    customer_id="550e8400-e29b-41d4-a716-446655440003",
    name="New Customer",
    contact_type="individual",
    contact_name="John Doe",
    phone="+86-13800138000",
    email="john@example.com",
    status="active"
)
created_customer = customer_dao.create(new_customer)

# Example: Get pending settlements
pending_settlements = settlement_dao.get_pending_settlements()

# Close session
session.close()
"""
