# OP_CMS Data Validation Service
# Story 6.1: Data Quality Validation & Duplicate Detection

from decimal import Decimal
from typing import Dict, List, Any, Optional, Tuple
import re
import logging
from difflib import SequenceMatcher

from backend.models.database_models import Customer

logger = logging.getLogger(__name__)


class ValidationResult:
    """Validation result container"""
    
    def __init__(self):
        self.is_valid = True
        self.errors: List[Dict[str, Any]] = []
        self.warnings: List[Dict[str, Any]] = []
    
    def add_error(self, field: str, message: str, value: Any = None):
        self.is_valid = False
        self.errors.append({
            'field': field,
            'message': message,
            'value': value
        })
    
    def add_warning(self, field: str, message: str, value: Any = None):
        self.warnings.append({
            'field': field,
            'message': message,
            'value': value
        })
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'is_valid': self.is_valid,
            'error_count': len(self.errors),
            'warning_count': len(self.warnings),
            'errors': self.errors,
            'warnings': self.warnings
        }


class DataValidationService:
    """Service for validating imported data"""
    
    # Required fields for customer import
    REQUIRED_FIELDS = ['company_name', 'contact_name', 'contact_phone']
    
    # Optional fields with validation rules
    VALIDATION_RULES = {
        'contact_phone': {
            'pattern': r'^[\d\s\-\+\(\)]{8,15}$',
            'message': '联系电话格式不正确（应为 8-15 位数字）'
        },
        'email': {
            'pattern': r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
            'message': '邮箱格式不正确'
        },
        'credit_code': {
            'pattern': r'^[A-Z0-9]{18}$',
            'message': '统一社会信用代码格式不正确（应为 18 位字母数字）'
        }
    }
    
    # Duplicate detection fields
    DUPLICATE_FIELDS = ['company_name', 'credit_code', 'erp_system', 'erp_customer_code']
    
    def validate_row(self, row_data: Dict[str, Any]) -> ValidationResult:
        """
        Validate a single row of imported data
        
        Args:
            row_data: Dictionary containing row data
            
        Returns:
            ValidationResult with errors and warnings
        """
        result = ValidationResult()
        
        # Check required fields
        for field in self.REQUIRED_FIELDS:
            value = row_data.get(field)
            if not value or (isinstance(value, str) and not value.strip()):
                result.add_error(
                    field=field,
                    message=f'{field} 为必填字段',
                    value=value
                )
        
        # Validate field formats
        for field, rules in self.VALIDATION_RULES.items():
            value = row_data.get(field)
            if value and isinstance(value, str):
                if not re.match(rules['pattern'], value.strip()):
                    result.add_error(
                        field=field,
                        message=rules['message'],
                        value=value
                    )
        
        # Additional business logic validations
        self._validate_business_rules(row_data, result)
        
        return result
    
    def _validate_business_rules(self, row_data: Dict[str, Any], result: ValidationResult):
        """
        Validate business-specific rules
        
        Args:
            row_data: Row data dictionary
            result: ValidationResult to add errors to
        """
        # Check credit code length if provided
        credit_code = row_data.get('credit_code')
        if credit_code and len(str(credit_code).strip()) != 18:
            result.add_error(
                field='credit_code',
                message='统一社会信用代码必须为 18 位',
                value=credit_code
            )
        
        # Check customer type if provided
        customer_type = row_data.get('customer_type')
        if customer_type and customer_type not in ['enterprise', 'individual']:
            result.add_error(
                field='customer_type',
                message='客户类型必须为 enterprise 或 individual',
                value=customer_type
            )
        
        # Check level if provided
        level = row_data.get('level')
        if level and level not in ['vip', 'standard', 'economy']:
            result.add_error(
                field='level',
                message='客户等级必须为 vip, standard 或 economy',
                value=level
            )
        
        # Check status if provided
        status = row_data.get('status')
        if status and status not in ['active', 'inactive', 'potential']:
            result.add_error(
                field='status',
                message='客户状态必须为 active, inactive 或 potential',
                value=status
            )
    
    def check_duplicates(
        self,
        row_data: Dict[str, Any],
        session,
        exclude_customer_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Check for duplicate customers
        
        Args:
            row_data: Row data to check
            session: Database session
            exclude_customer_id: Customer ID to exclude (for updates)
            
        Returns:
            List of matching customers
        """
        duplicates = []
        
        # Build query filters
        filters = []
        
        # Exact match on company name
        company_name = row_data.get('company_name')
        if company_name:
            filters.append(Customer.company_name == company_name.strip())
        
        # Exact match on credit code
        credit_code = row_data.get('credit_code')
        if credit_code:
            filters.append(Customer.credit_code == credit_code.strip())
        
        # Exact match on ERP code
        erp_code = row_data.get('erp_customer_code')
        if erp_code:
            filters.append(Customer.erp_customer_code == erp_code.strip())
        
        if not filters:
            return []
        
        # Query for exact matches
        from sqlalchemy import or_
        query = session.query(Customer).filter(or_(*filters))
        
        if exclude_customer_id:
            query = query.filter(Customer.id != exclude_customer_id)
        
        exact_matches = query.all()
        
        for customer in exact_matches:
            duplicates.append({
                'customer_id': customer.id,
                'company_name': customer.company_name,
                'contact_name': customer.contact_name,
                'match_type': 'exact',
                'match_fields': self._get_match_fields(customer, row_data)
            })
        
        # Fuzzy match on company name (similarity > 0.8)
        if company_name:
            fuzzy_matches = self._fuzzy_match_company_name(session, company_name, exclude_customer_id)
            for customer in fuzzy_matches:
                if customer.id not in [d['customer_id'] for d in duplicates]:
                    duplicates.append({
                        'customer_id': customer.id,
                        'company_name': customer.company_name,
                        'contact_name': customer.contact_name,
                        'match_type': 'fuzzy',
                        'similarity': self._calculate_similarity(customer.company_name, company_name),
                        'match_fields': ['company_name']
                    })
        
        return duplicates
    
    def _get_match_fields(self, customer: Customer, row_data: Dict[str, Any]) -> List[str]:
        """Get fields that matched"""
        match_fields = []
        
        if customer.company_name == row_data.get('company_name', '').strip():
            match_fields.append('company_name')
        
        if customer.credit_code and customer.credit_code == row_data.get('credit_code', '').strip():
            match_fields.append('credit_code')
        
        if customer.erp_customer_code and customer.erp_customer_code == row_data.get('erp_customer_code', '').strip():
            match_fields.append('erp_customer_code')
        
        return match_fields
    
    def _fuzzy_match_company_name(
        self,
        session,
        company_name: str,
        exclude_customer_id: Optional[int] = None
    ) -> List[Customer]:
        """
        Fuzzy match company name using SQL LIKE
        
        Args:
            session: Database session
            company_name: Company name to match
            exclude_customer_id: Customer ID to exclude
            
        Returns:
            List of potential fuzzy matches
        """
        # Use LIKE for basic fuzzy matching
        # In production, consider using full-text search or trigram similarity
        query = session.query(Customer).filter(
            Customer.company_name.like(f'%{company_name}%')
        )
        
        if exclude_customer_id:
            query = query.filter(Customer.id != exclude_customer_id)
        
        return query.limit(10).all()
    
    def _calculate_similarity(self, str1: str, str2: str) -> float:
        """Calculate string similarity using SequenceMatcher"""
        return SequenceMatcher(None, str1, str2).ratio()
    
    def validate_batch(
        self,
        rows: List[Dict[str, Any]],
        session
    ) -> Dict[str, Any]:
        """
        Validate a batch of rows
        
        Args:
            rows: List of row data dictionaries
            session: Database session
            
        Returns:
            Batch validation report
        """
        total_rows = len(rows)
        valid_rows = 0
        invalid_rows = 0
        duplicate_rows = 0
        
        validation_results = []
        
        for idx, row_data in enumerate(rows, 1):
            # Validate row
            validation = self.validate_row(row_data)
            
            # Check duplicates
            duplicates = self.check_duplicates(row_data, session)
            
            row_result = {
                'row_number': idx,
                'validation': validation.to_dict(),
                'duplicates': duplicates,
                'is_importable': validation.is_valid and len(duplicates) == 0
            }
            
            validation_results.append(row_result)
            
            if row_result['is_importable']:
                valid_rows += 1
            else:
                invalid_rows += 1
                if duplicates:
                    duplicate_rows += 1
        
        return {
            'total_rows': total_rows,
            'valid_rows': valid_rows,
            'invalid_rows': invalid_rows,
            'duplicate_rows': duplicate_rows,
            'validation_rate': valid_rows / total_rows if total_rows > 0 else 0,
            'results': validation_results
        }
