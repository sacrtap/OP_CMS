"""
Tests for Customer API Endpoints - Story 1.1
"""

import pytest
from decimal import Decimal
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock

from backend.models.database_models import (
    Customer, CustomerCreate, CustomerUpdate, CustomerResponse
)


# ==================== Customer Model Tests ====================

class TestCustomerModel:
    """Tests for Customer SQLAlchemy model"""
    
    def test_customer_creation(self):
        """Test creating a customer with required fields"""
        customer = Customer(
            customer_id='test-uuid-123',
            company_name='Test Company',
            contact_name='John Doe',
            contact_phone='13800138000'
        )
        
        assert customer.company_name == 'Test Company'
        assert customer.contact_name == 'John Doe'
        assert customer.contact_phone == '13800138000'
        assert customer.customer_type == 'enterprise'
        assert customer.status == 'active'
        assert customer.level == 'standard'
        assert customer.source == 'direct'
    
    def test_customer_optional_fields(self):
        """Test creating a customer with all fields"""
        customer = Customer(
            customer_id='test-uuid-456',
            company_name='Test Company 2',
            contact_name='Jane Smith',
            contact_phone='13900139000',
            credit_code='91310000MA1K3YJ12X',
            customer_type='enterprise',
            province='Shanghai',
            city='Shanghai',
            address='No. 123 Test Road',
            email='test@example.com',
            website='https://test.com',
            industry='Technology',
            erp_system='SAP',
            erp_customer_code='C001',
            status='active',
            level='vip',
            source='direct',
            remarks='Test customer'
        )
        
        assert customer.credit_code == '91310000MA1K3YJ12X'
        assert customer.province == 'Shanghai'
        assert customer.email == 'test@example.com'
        assert customer.level == 'vip'


# ==================== Pydantic Schema Tests ====================

class TestCustomerCreateSchema:
    """Tests for CustomerCreate Pydantic schema"""
    
    def test_create_with_required_fields(self):
        """Test creating CustomerCreate with only required fields"""
        data = {
            'company_name': 'Test Company',
            'contact_name': 'John Doe',
            'contact_phone': '13800138000'
        }
        
        customer = CustomerCreate(**data)
        
        assert customer.company_name == 'Test Company'
        assert customer.contact_name == 'John Doe'
        assert customer.contact_phone == '13800138000'
        assert customer.customer_type == 'enterprise'
        assert customer.status == 'active'
    
    def test_create_with_all_fields(self):
        """Test creating CustomerCreate with all fields"""
        data = {
            'company_name': 'Test Company',
            'contact_name': 'John Doe',
            'contact_phone': '13800138000',
            'credit_code': '91310000MA1K3YJ12X',
            'customer_type': 'enterprise',
            'province': 'Shanghai',
            'city': 'Shanghai',
            'address': 'No. 123 Test Road',
            'email': 'test@example.com',
            'website': 'https://test.com',
            'industry': 'Technology',
            'erp_system': 'SAP',
            'erp_customer_code': 'C001',
            'status': 'active',
            'level': 'vip',
            'source': 'direct',
            'remarks': 'Test customer'
        }
        
        customer = CustomerCreate(**data)
        
        assert customer.credit_code == '91310000MA1K3YJ12X'
        assert customer.province == 'Shanghai'
        assert customer.email == 'test@example.com'
    
    def test_validate_phone_valid(self):
        """Test phone validation with valid numbers"""
        valid_phones = [
            '13800138000',
            '+86-13800138000',
            '138-0013-8000',
            '+86 138 0013 8000',
            '(010) 12345678'
        ]
        
        for phone in valid_phones:
            data = {
                'company_name': 'Test',
                'contact_name': 'John',
                'contact_phone': phone
            }
            customer = CustomerCreate(**data)
            assert customer.contact_phone == phone
    
    def test_validate_phone_invalid(self):
        """Test phone validation with invalid numbers"""
        invalid_phones = [
            'abc123',
            '123',  # Too short
            '12345678901234567890'  # Too long
        ]
        
        for phone in invalid_phones:
            data = {
                'company_name': 'Test',
                'contact_name': 'John',
                'contact_phone': phone
            }
            with pytest.raises(ValueError, match='Phone number'):
                CustomerCreate(**data)
    
    def test_validate_email_valid(self):
        """Test email validation with valid emails"""
        valid_emails = [
            'test@example.com',
            'john.doe@company.cn',
            'admin@test-site.org'
        ]
        
        for email in valid_emails:
            data = {
                'company_name': 'Test',
                'contact_name': 'John',
                'contact_phone': '13800138000',
                'email': email
            }
            customer = CustomerCreate(**data)
            assert customer.email == email
    
    def test_validate_email_invalid(self):
        """Test email validation with invalid emails"""
        invalid_emails = [
            'notanemail',
            'test@',
            '@example.com',
            'test @example.com'
        ]
        
        for email in invalid_emails:
            data = {
                'company_name': 'Test',
                'contact_name': 'John',
                'contact_phone': '13800138000',
                'email': email
            }
            with pytest.raises(ValueError, match='Invalid email'):
                CustomerCreate(**data)
    
    def test_validate_credit_code_valid(self):
        """Test credit code validation with valid codes"""
        valid_codes = [
            '91310000MA1K3YJ12X',
            'ABC123456789012345',
            '123456789012345678'
        ]
        
        for code in valid_codes:
            data = {
                'company_name': 'Test',
                'contact_name': 'John',
                'contact_phone': '13800138000',
                'credit_code': code
            }
            customer = CustomerCreate(**data)
            assert customer.credit_code == code
    
    def test_validate_credit_code_invalid_length(self):
        """Test credit code validation with invalid length"""
        invalid_codes = [
            'ABC123',  # Too short
            'ABC12345678901234567890'  # Too long
        ]
        
        for code in invalid_codes:
            data = {
                'company_name': 'Test',
                'contact_name': 'John',
                'contact_phone': '13800138000',
                'credit_code': code
            }
            with pytest.raises(ValueError, match='18 characters'):
                CustomerCreate(**data)
    
    def test_validate_credit_code_invalid_chars(self):
        """Test credit code validation with invalid characters"""
        data = {
            'company_name': 'Test',
            'contact_name': 'John',
            'contact_phone': '13800138000',
            'credit_code': '91310000MA1K3YJ12X@'  # Contains special char
        }
        with pytest.raises(ValueError, match='alphanumeric'):
            CustomerCreate(**data)
    
    def test_validate_enums(self):
        """Test enum field validation"""
        # Valid values
        valid_data = {
            'company_name': 'Test',
            'contact_name': 'John',
            'contact_phone': '13800138000',
            'customer_type': 'individual',
            'status': 'potential',
            'level': 'economy',
            'source': 'referral'
        }
        customer = CustomerCreate(**valid_data)
        assert customer.customer_type == 'individual'
        assert customer.status == 'potential'
        assert customer.level == 'economy'
        assert customer.source == 'referral'
        
        # Invalid values
        invalid_data = {
            'company_name': 'Test',
            'contact_name': 'John',
            'contact_phone': '13800138000',
            'customer_type': 'invalid'
        }
        with pytest.raises(ValueError, match='pattern'):
            CustomerCreate(**invalid_data)


class TestCustomerUpdateSchema:
    """Tests for CustomerUpdate Pydantic schema"""
    
    def test_update_partial(self):
        """Test partial update (only some fields)"""
        data = {
            'company_name': 'Updated Company'
        }
        
        update = CustomerUpdate(**data)
        
        assert update.company_name == 'Updated Company'
        assert update.contact_name is None
        assert update.contact_phone is None
    
    def test_update_full(self):
        """Test full update (all fields)"""
        data = {
            'company_name': 'Updated Company',
            'contact_name': 'Updated Name',
            'contact_phone': '13900139000',
            'email': 'updated@example.com',
            'status': 'inactive'
        }
        
        update = CustomerUpdate(**data)
        
        assert update.company_name == 'Updated Company'
        assert update.contact_name == 'Updated Name'
        assert update.email == 'updated@example.com'
        assert update.status == 'inactive'
    
    def test_update_validates_fields(self):
        """Test that update also validates fields"""
        data = {
            'contact_phone': 'invalid-phone'
        }
        
        with pytest.raises(ValueError, match='Phone number'):
            CustomerUpdate(**data)


# ==================== Response Schema Tests ====================

class TestCustomerResponseSchema:
    """Tests for CustomerResponse schema"""
    
    def test_response_from_model(self):
        """Test creating response from Customer model"""
        customer = Customer(
            id=1,
            customer_id='test-uuid',
            company_name='Test Company',
            contact_name='John Doe',
            contact_phone='13800138000',
            created_at=datetime(2026, 2, 24, 10, 0, 0),
            updated_at=datetime(2026, 2, 24, 12, 0, 0)
        )
        
        response = CustomerResponse.model_validate(customer)
        
        assert response.id == 1
        assert response.customer_id == 'test-uuid'
        assert response.company_name == 'Test Company'
        assert response.contact_name == 'John Doe'
    
    def test_response_with_optional_fields(self):
        """Test response includes all optional fields"""
        customer = Customer(
            id=1,
            customer_id='test-uuid',
            company_name='Test Company',
            contact_name='John Doe',
            contact_phone='13800138000',
            credit_code='91310000MA1K3YJ12X',
            email='test@example.com',
            province='Shanghai',
            city='Shanghai',
            level='vip',
            status='active',
            created_at=datetime(2026, 2, 24, 10, 0, 0),
            updated_at=datetime(2026, 2, 24, 12, 0, 0)
        )
        
        response = CustomerResponse.model_validate(customer)
        
        assert response.credit_code == '91310000MA1K3YJ12X'
        assert response.email == 'test@example.com'
        assert response.province == 'Shanghai'
        assert response.level == 'vip'


# ==================== Integration Tests ====================

class TestCustomerWorkflow:
    """Integration tests for complete customer workflow"""
    
    def test_create_validate_workflow(self):
        """Test complete create and validate workflow"""
        # Step 1: Create
        create_data = {
            'company_name': 'Integration Test Corp',
            'contact_name': 'Test Manager',
            'contact_phone': '13800138000',
            'credit_code': '91310000MA1K3YJ12X',
            'email': 'contact@testcorp.com',
            'province': 'Shanghai',
            'level': 'vip'
        }
        
        customer = CustomerCreate(**create_data)
        assert customer.company_name == 'Integration Test Corp'
        assert customer.credit_code == '91310000MA1K3YJ12X'
        
        # Step 2: Update
        update_data = {
            'level': 'standard',
            'status': 'active',
            'remarks': 'Updated via integration test'
        }
        
        update = CustomerUpdate(**update_data)
        assert update.level == 'standard'
        assert update.remarks == 'Updated via integration test'
        
        # Step 3: Validate defaults
        minimal_data = {
            'company_name': 'Minimal Corp',
            'contact_name': 'Min Contact',
            'contact_phone': '13800138000'
        }
        
        minimal = CustomerCreate(**minimal_data)
        assert minimal.customer_type == 'enterprise'
        assert minimal.status == 'active'
        assert minimal.level == 'standard'
        assert minimal.source == 'direct'
