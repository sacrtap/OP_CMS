#!/usr/bin/env python3
# OP_CMS Database Initialization Script
# MySQL 8.0+ Database Schema Setup
"""
Database Initialization Script for OP_CMS

This script creates the database schema and initializes the database
with the required tables for the OP_CMS system.

Usage:
    python init_db.py
"""

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import os
import sys
from datetime import datetime


def load_config():
    """Load database configuration from environment or default"""
    config = {
        'DB_HOST': os.environ.get('DB_HOST', 'localhost'),
        'DB_PORT': int(os.environ.get('DB_PORT', 3306)),
        'DB_NAME': os.environ.get('DB_NAME', 'op_cms'),
        'DB_USER': os.environ.get('DB_USER', 'root'),
        'DB_PASSWORD': os.environ.get('DB_PASSWORD', ''),
    }
    
    if not config['DB_PASSWORD']:
        print("⚠️  WARNING: No database password provided. Using empty password.")
        print("Please set DB_PASSWORD environment variable for production use.")
    
    return config


def create_connection_string(config):
    """Build MySQL connection string"""
    return (
        f"mysql+pymysql://{config['DB_USER']}:{config['DB_PASSWORD']}@"
        f"{config['DB_HOST']}:{config['DB_PORT']}"
    )


def create_database(engine, db_name):
    """Create database if not exists"""
    try:
        with engine.connect() as conn:
            conn.execute(text(f"CREATE DATABASE IF NOT EXISTS `{db_name}` "
                             "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"))
            conn.commit()
            print(f"✅ Database `{db_name}` created or already exists")
    except Exception as e:
        print(f"❌ Failed to create database: {str(e)}")
        raise


def create_tables(engine, db_name):
    """Create all required tables"""
    try:
        with engine.connect() as conn:
            conn.execute(text(f"USE `{db_name}`"))
            
            # Create customers table
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS `customers` (
                    `id` INT PRIMARY KEY AUTO_INCREMENT,
                    `customer_id` VARCHAR(36) NOT NULL UNIQUE,
                    `name` VARCHAR(100) NOT NULL,
                    `contact_type` VARCHAR(20) NOT NULL,
                    `contact_name` VARCHAR(100) NOT NULL,
                    `phone` VARCHAR(20),
                    `email` VARCHAR(100),
                    `address` VARCHAR(500),
                    `status` VARCHAR(20) DEFAULT 'active',
                    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
                    `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    `metadata` JSON,
                    INDEX `idx_customer_name` (`name`),
                    INDEX `idx_customer_contact` (`contact_name`),
                    INDEX `idx_customer_status` (`status`)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """))
            
            # Create price_configs table
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS `price_configs` (
                    `id` INT PRIMARY KEY AUTO_INCREMENT,
                    `config_id` VARCHAR(36) NOT NULL UNIQUE,
                    `customer_id` INT NOT NULL,
                    `name` VARCHAR(100) NOT NULL,
                    `description` TEXT,
                    `price_model` VARCHAR(20) NOT NULL,
                    `currency` VARCHAR(3) DEFAULT 'CNY',
                    `min_quantity` DECIMAL(10, 2),
                    `max_quantity` DECIMAL(10, 2),
                    `unit_price` DECIMAL(12, 4),
                    `base_price` DECIMAL(12, 4),
                    `volume_discount` DECIMAL(5, 2),
                    `pricing_rules` JSON,
                    `is_active` BOOLEAN DEFAULT TRUE,
                    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
                    `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    INDEX `idx_price_config_customer` (`customer_id`),
                    INDEX `idx_price_config_active` (`is_active`),
                    FOREIGN KEY (`customer_id`) REFERENCES `customers`(`id`) ON DELETE CASCADE
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """))
            
            # Create settlement_records table
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS `settlement_records` (
                    `id` INT PRIMARY KEY AUTO_INCREMENT,
                    `record_id` VARCHAR(36) NOT NULL UNIQUE,
                    `customer_id` INT NOT NULL,
                    `config_id` INT NOT NULL,
                    `period_start` DATETIME NOT NULL,
                    `period_end` DATETIME NOT NULL,
                    `usage_quantity` DECIMAL(10, 2) NOT NULL,
                    `unit` VARCHAR(20) NOT NULL,
                    `price_model` VARCHAR(20) NOT NULL,
                    `unit_price` DECIMAL(12, 4) NOT NULL,
                    `total_amount` DECIMAL(12, 2) NOT NULL,
                    `currency` VARCHAR(3) DEFAULT 'CNY',
                    `status` VARCHAR(20) DEFAULT 'pending',
                    `remarks` TEXT,
                    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
                    `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    `approved_at` DATETIME,
                    `paid_at` DATETIME,
                    INDEX `idx_settlement_customer` (`customer_id`),
                    INDEX `idx_settlement_period` (`period_start`, `period_end`),
                    INDEX `idx_settlement_status` (`status`),
                    INDEX `idx_settlement_record_id` (`record_id`),
                    INDEX `idx_settlement_customer_period` (`customer_id`, `period_start`, `period_end`),
                    INDEX `idx_settlement_customer_status` (`customer_id`, `status`),
                    FOREIGN KEY (`customer_id`) REFERENCES `customers`(`id`) ON DELETE CASCADE,
                    FOREIGN KEY (`config_id`) REFERENCES `price_configs`(`id`) ON DELETE CASCADE
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """))
            
            conn.commit()
            print("✅ All tables created successfully")
    except Exception as e:
        print(f"❌ Failed to create tables: {str(e)}")
        raise


def insert_sample_data(engine, db_name):
    """Insert sample data for testing"""
    try:
        with engine.connect() as conn:
            conn.execute(text(f"USE `{db_name}`"))
            
            # Check if sample data already exists
            result = conn.execute(text("SELECT COUNT(*) FROM `customers`")).scalar()
            if result > 0:
                print("⚠️  Sample data already exists, skipping")
                return
            
            # Insert sample customers
            conn.execute(text("""
                INSERT INTO `customers` (
                    `customer_id`, `name`, `contact_type`, `contact_name`, 
                    `phone`, `email`, `address`, `status`
                ) VALUES 
                    ('550e8400-e29b-41d4-a716-446655440001', 'Test Customer 1', 'individual', 'John Doe', 
                     '+86-13800138000', 'john@example.com', 'Beijing, China', 'active'),
                    ('550e8400-e29b-41d4-a716-446655440002', 'Test Customer 2', 'corporate', 'Jane Smith', 
                     '+86-13900139000', 'jane@example.com', 'Shanghai, China', 'active')
            """))
            
            # Insert sample price configs
            conn.execute(text("""
                INSERT INTO `price_configs` (
                    `config_id`, `customer_id`, `name`, `description`, 
                    `price_model`, `currency`, `min_quantity`, `max_quantity`, `unit_price`,
                    `is_active`
                ) VALUES 
                    ('650e8400-e29b-41d4-a716-446655440001', 1, 'Basic Tier', 'Basic pricing tier',
                     'tiered', 'CNY', '0', '100', '0.10', 1),
                    ('650e8400-e29b-41d4-a716-446655440002', 2, 'Volume Pricing', 'Volume-based pricing',
                     'volume', 'CNY', NULL, NULL, NULL, 1)
            """))
            
            conn.commit()
            print("✅ Sample data inserted successfully")
    except Exception as e:
        print(f"❌ Failed to insert sample data: {str(e)}")
        raise


def main():
    """Main initialization function"""
    print("=" * 60)
    print("OP_CMS Database Initialization Script")
    print("=" * 60)
    print()
    
    # Load configuration
    config = load_config()
    print(f"🔧 Configuration:")
    print(f"   Host: {config['DB_HOST']}:{config['DB_PORT']}")
    print(f"   Database: {config['DB_NAME']}")
    print(f"   User: {config['DB_USER']}")
    print()
    
    # Create connection (without database first)
    connection_string = create_connection_string(config)
    engine = create_engine(connection_string)
    
    try:
        # Step 1: Create database
        print("Step 1/3: Creating database...")
        create_database(engine, config['DB_NAME'])
        print()
        
        # Step 2: Create tables
        print("Step 2/3: Creating tables...")
        db_connection_string = f"{connection_string}/{config['DB_NAME']}"
        db_engine = create_engine(db_connection_string)
        create_tables(db_engine, config['DB_NAME'])
        print()
        
        # Step 3: Insert sample data
        print("Step 3/3: Inserting sample data...")
        insert_sample_data(db_engine, config['DB_NAME'])
        print()
        
        print("=" * 60)
        print("✅ Database initialization completed successfully!")
        print("=" * 60)
        print()
        print("Next steps:")
        print("1. Update your .env file with the database credentials")
        print("2. Run the application: python -m backend.app.main")
        print("3. Access the API documentation at http://localhost:8000/docs")
        print()
        
    except Exception as e:
        print()
        print("=" * 60)
        print("❌ Database initialization failed!")
        print("=" * 60)
        print(f"Error: {str(e)}")
        print()
        print("Troubleshooting:")
        print("1. Check if MySQL server is running")
        print("2. Verify database credentials")
        print("3. Ensure you have necessary permissions")
        print("4. Check MySQL error logs for details")
        print()
        sys.exit(1)


if __name__ == '__main__':
    main()
