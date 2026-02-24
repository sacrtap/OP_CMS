"""
OP_CMS Backend Tests
Tests for database models and DAO layer
"""

import pytest
from decimal import Decimal
from datetime import datetime
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from backend.models.database_models import (
    Base, Customer, PriceConfig, SettlementRecord,
    CustomerCreate, PriceConfigCreate, SettlementRecordCreate,
    DatabaseConnection
)
from backend.dao.database_dao import (
    BaseDAO, CustomerDAO, PriceConfigDAO, SettlementRecordDAO,
    DatabaseSessionFactory
)


# ==================== Pytest Fixtures ====================

@pytest.fixture
def test_db_url() -> str:
    """Test database connection URL"""
    return "mysql+pymysql://root:@localhost:3306/op_cms_test"


@pytest.fixture
def engine(test_db_url: str):
    """Create test database engine"""
    return create_engine(test_db_url, pool_pre_ping=True)


@pytest.fixture
def session(engine) -> Generator[Session, None, None]:
    """Create database session for tests"""
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def db_session(session) -> Generator[Session, None, None]:
    """Database session with cleanup for integration tests"""
    try:
        yield session
        session.rollback()
    finally:
        session.close()


# ==================== Model Tests ====================
