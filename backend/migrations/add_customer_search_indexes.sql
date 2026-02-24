-- Database Indexes for Customer Search Optimization - Story 1.2
-- Run these indexes to improve search performance

-- Composite index for multi-field search
CREATE INDEX IF NOT EXISTS idx_customer_search_combined 
ON customers(company_name, contact_name, credit_code);

-- Index for common filter combinations
CREATE INDEX IF NOT EXISTS idx_customer_filters 
ON customers(status, level, customer_type, province, city, source);

-- Index for date range queries
CREATE INDEX IF NOT EXISTS idx_customer_created_at 
ON customers(created_at);

-- Index for company name exact match
CREATE INDEX IF NOT EXISTS idx_customer_company_name 
ON customers(company_name);

-- Index for contact name search
CREATE INDEX IF NOT EXISTS idx_customer_contact_name 
ON customers(contact_name);

-- Composite index for status + level filtering
CREATE INDEX IF NOT EXISTS idx_customer_status_level 
ON customers(status, level);

-- Composite index for geographic filtering
CREATE INDEX IF NOT EXISTS idx_customer_location 
ON customers(province, city);

-- Composite index for time-based queries
CREATE INDEX IF NOT EXISTS idx_customer_created_status 
ON customers(created_at, status);

-- Composite index for sorting optimization
CREATE INDEX IF NOT EXISTS idx_customer_created_desc 
ON customers(created_at DESC);

-- Composite index for multi-column sorting
CREATE INDEX IF NOT EXISTS idx_customer_company_created 
ON customers(company_name, created_at DESC);
