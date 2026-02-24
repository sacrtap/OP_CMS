#!/usr/bin/env python3
"""
Database Seed Script
Create initial data for development and testing

Usage:
    python backend/scripts/seed_data.py
"""

import sys
from os.path import abspath, dirname
sys.path.insert(0, dirname(dirname(abspath(__file__))))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.models.database_models import Base, Customer
from backend.models.auth import User
from datetime import datetime
import uuid


def seed_database():
    """Seed database with initial data"""
    
    # Database connection
    DATABASE_URL = "mysql+pymysql://op_cms_user:CHANGE_ME@localhost:3306/op_cms"
    engine = create_engine(DATABASE_URL, echo=True)
    
    # Create session
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()
    
    try:
        print("🌱 Seeding database...")
        
        # Create admin user
        admin = User(
            username='admin',
            email='admin@example.com',
            full_name='System Administrator',
            role='admin',
            is_superuser=True
        )
        admin.set_password('Admin123!')  # Default password
        
        # Create demo users
        operator = User(
            username='operator',
            email='operator@example.com',
            full_name='Demo Operator',
            role='operator'
        )
        operator.set_password('Operator123!')
        
        session.add(admin)
        session.add(operator)
        print("✅ Created users (admin, operator)")
        
        # Create demo customers
        demo_customers = [
            Customer(
                customer_id=str(uuid.uuid4()),
                company_name='示例科技公司',
                contact_name='张三',
                contact_phone='13800138000',
                credit_code='91310000MA1K3YJ12X',
                customer_type='enterprise',
                province='Shanghai',
                city='Shanghai',
                email='zhangsan@example.com',
                industry='Technology',
                status='active',
                level='vip',
                source='direct'
            ),
            Customer(
                customer_id=str(uuid.uuid4()),
                company_name='测试贸易公司',
                contact_name='李四',
                contact_phone='13900139000',
                credit_code='91310000MA1K3YJ13Y',
                customer_type='enterprise',
                province='Beijing',
                city='Beijing',
                email='lisi@example.com',
                industry='Trading',
                status='active',
                level='standard',
                source='referral'
            ),
        ]
        
        for customer in demo_customers:
            session.add(customer)
        
        print(f"✅ Created {len(demo_customers)} demo customers")
        
        session.commit()
        print("🎉 Database seeding completed!")
        
    except Exception as e:
        session.rollback()
        print(f"❌ Seeding failed: {str(e)}")
        raise
    finally:
        session.close()


if __name__ == '__main__':
    seed_database()
