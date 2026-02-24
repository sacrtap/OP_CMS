# OP_CMS Data Validation Service
# Story 6.1: Data Quality Validation & Duplicate Detection

from datetime import datetime
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
    
    def __init__(self, batch_size: int = 1000, max_errors: int = 100):
        """Initialize DataValidationService
        
        Args:
            batch_size: Number of records to process in one batch
            max_errors: Maximum number of errors to collect before stopping
        """
        self.batch_size = batch_size
        self.max_errors = max_errors
    
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
    
    def validate_customer_data(self, customer_data: dict) -> tuple[bool, list]:
        """
        Validate customer data
        
        Args:
            customer_data: Dictionary containing customer data
            
        Returns:
            Tuple of (is_valid, errors)
            - is_valid: True if data is valid, False otherwise
            - errors: List of error messages
        """
        errors = []
        
        # Check required fields
        for field in self.REQUIRED_FIELDS:
            value = customer_data.get(field)
            if not value or (isinstance(value, str) and not value.strip()):
                errors.append(f'{field} 为必填字段')
        
        # Validate phone format
        phone = customer_data.get('contact_phone')
        if phone:
            is_phone_valid, phone_error = self.validate_phone(str(phone))
            if not is_phone_valid:
                errors.append(f'contact_phone: {phone_error}')
        
        # Validate email format
        email = customer_data.get('email')
        if email:
            is_email_valid, email_error = self.validate_email(str(email))
            if not is_email_valid:
                errors.append(f'email: {email_error}')
        
        # Validate credit code
        credit_code = customer_data.get('credit_code')
        if credit_code:
            is_credit_valid, credit_error = self.validate_credit_code(str(credit_code))
            if not is_credit_valid:
                errors.append(f'credit_code: {credit_error}')
        
        # Validate enum values
        customer_type = customer_data.get('customer_type')
        if customer_type and customer_type not in ['enterprise', 'individual']:
            errors.append('customer_type 必须为 enterprise 或 individual')
        
        level = customer_data.get('level')
        if level and level not in ['vip', 'standard', 'economy']:
            errors.append('level 必须为 vip, standard 或 economy')
        
        status = customer_data.get('status')
        if status and status not in ['active', 'inactive', 'potential']:
            errors.append('status 必须为 active, inactive 或 potential')
        
        return (len(errors) == 0, errors)
    
    def validate_phone(self, phone: str) -> tuple[bool, str]:
        """
        Validate phone number
        
        Args:
            phone: Phone number string
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not phone:
            return (False, '联系电话不能为空')
        
        # Remove whitespace
        phone = phone.strip()
        
        # Check length (8-15 digits)
        if len(phone) < 8 or len(phone) > 15:
            return (False, '联系电话长度必须为 8-15 位')
        
        # Check format (only digits, spaces, dashes, plus, parentheses)
        if not re.match(r'^[\d\s\-\+\(\)]+$', phone):
            return (False, '联系电话格式不正确（只能包含数字、空格、破折号、加号和括号）')
        
        return (True, '')
    
    def validate_email(self, email: str) -> tuple[bool, str]:
        """
        Validate email address
        
        Args:
            email: Email address string
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not email:
            return (True, '')  # Email is optional
        
        email = email.strip()
        
        # Basic email pattern
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        if not re.match(pattern, email):
            return (False, '邮箱格式不正确')
        
        return (True, '')
    
    def validate_credit_code(self, code: str) -> tuple[bool, str]:
        """
        Validate unified social credit code
        
        Args:
            code: Credit code string
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not code or not code.strip():
            return (False, '统一社会信用代码不能为空')
        
        code = code.strip().upper()
        
        # Check length
        if len(code) != 18:
            return (False, '统一社会信用代码必须为 18 位')
        
        # Check characters (only uppercase letters and digits)
        if not re.match(r'^[A-Z0-9]+$', code):
            return (False, '统一社会信用代码只能包含字母和数字（alphanumeric characters）')
        
        return (True, '')
    
    def validate_data_batch(self, batch_data: list[dict]) -> dict:
        """
        Validate batch data
        
        Args:
            batch_data: List of customer data dictionaries
            
        Returns:
            Dictionary with validation results
        """
        results = {
            'total': len(batch_data),
            'valid': 0,
            'invalid': 0,
            'errors': [],
            'details': []
        }
        
        errors_collected = 0
        
        for idx, data in enumerate(batch_data, 1):
            # Stop if max_errors reached
            if errors_collected >= self.max_errors:
                break
            
            is_valid, errors = self.validate_customer_data(data)
            
            if is_valid:
                results['valid'] += 1
            else:
                results['invalid'] += 1
                errors_collected += len(errors)
                results['errors'].append({
                    'row': idx,
                    'errors': errors
                })
            
            results['details'].append({
                'row': idx,
                'is_valid': is_valid,
                'errors': errors
            })
        
        results['validation_rate'] = results['valid'] / results['total'] if results['total'] > 0 else 0
        
        return results
    
    def generate_quality_report(self, validation_results: dict) -> dict:
        """
        Generate data quality report
        
        Args:
            validation_results: Dictionary with validation results
                {
                    'total': int,
                    'valid': int,
                    'invalid': int,
                    'errors': list
                }
            
        Returns:
            Quality report dictionary
        """
        total = validation_results.get('total', 0)
        valid = validation_results.get('valid', 0)
        invalid = validation_results.get('invalid', 0)
        
        # Calculate score (0-100)
        score = (valid / total * 100) if total > 0 else 0
        
        # Determine quality level
        if score >= 95:
            quality_level = '优秀 (Excellent)'
        elif score >= 90:
            quality_level = '良好 (Good)'
        elif score >= 80:
            quality_level = '中等 (Fair)'
        else:
            quality_level = '需改进 (Needs Improvement)'
        
        # Collect error summary
        errors = validation_results.get('errors', [])
        error_summary = {}
        for error in errors:
            field = error.get('field', 'unknown')
            error_msg = error.get('error', 'Unknown error')
            key = f"{field}: {error_msg}"
            error_summary[key] = error_summary.get(key, 0) + 1
        
        # Sort errors by frequency
        sorted_errors = sorted(
            error_summary.items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]  # Top 10 errors
        
        return {
            'total_records': total,
            'valid_records': valid,
            'invalid_records': invalid,
            'quality_score': round(score, 2),
            'quality_level': quality_level,
            'error_summary': [
                {'error': error, 'count': count}
                for error, count in sorted_errors
            ],
            'generated_at': datetime.utcnow().isoformat()
        }
    
    def _find_by_company_name(self, session, company_name: str) -> list:
        """Find customers by company name"""
        try:
            from backend.models.database_models import Customer
            results = session.query(Customer).filter(
                Customer.company_name == company_name
            ).limit(10).all()
            return results
        except Exception as e:
            logger.error(f"Error finding by company name: {e}")
            return []
    
    def _find_by_credit_code(self, session, credit_code: str) -> list:
        """Find customers by credit code"""
        try:
            from backend.models.database_models import Customer
            results = session.query(Customer).filter(
                Customer.credit_code == credit_code
            ).limit(10).all()
            return results
        except Exception as e:
            logger.error(f"Error finding by credit code: {e}")
            return []
    
    def validate_data_batch(self, batch_data: list[dict]) -> dict:
        """
        Validate batch data
        
        Args:
            batch_data: List of customer data dictionaries
            
        Returns:
            Dictionary with validation results
        """
        results = {
            'total': len(batch_data),
            'valid': 0,
            'invalid': 0,
            'errors': [],
            'details': []
        }
        
        for idx, data in enumerate(batch_data, 1):
            is_valid, errors = self.validate_customer_data(data)
            
            if is_valid:
                results['valid'] += 1
            else:
                results['invalid'] += 1
                results['errors'].append({
                    'row': idx,
                    'errors': errors
                })
            
            results['details'].append({
                'row': idx,
                'is_valid': is_valid,
                'errors': errors
            })
        
        results['validation_rate'] = results['valid'] / results['total'] if results['total'] > 0 else 0
        
        return results
    
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
