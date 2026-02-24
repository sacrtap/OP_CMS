# OP_CMS Settlement Validation Service
# Story 3.3: Settlement Validation and Sending

from decimal import Decimal
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import logging

from backend.models.database_models import SettlementRecord, PriceConfig

logger = logging.getLogger(__name__)


class SettlementValidationError(Exception):
    """Custom exception for settlement validation errors"""
    pass


class SettlementValidationService:
    """Service for validating settlement data"""
    
    def __init__(self):
        self.validation_rules = [
            self._check_usage_spike,
            self._check_unit_price_consistency,
            self._check_total_amount_calculation,
            self._check_negative_values
        ]
    
    def validate_settlement(
        self,
        settlement: SettlementRecord,
        session
    ) -> Dict[str, Any]:
        """
        Validate settlement data for accuracy
        
        Args:
            settlement: Settlement record to validate
            session: Database session
            
        Returns:
            Dictionary with validation results:
            - is_valid: bool
            - errors: List of validation errors
            - warnings: List of warnings
            - validation_details: Detailed validation info
        """
        errors = []
        warnings = []
        validation_details = []
        
        # Run all validation rules
        for rule in self.validation_rules:
            try:
                result = rule(settlement, session)
                if result and not result.get('is_valid', True):
                    if result.get('is_error', True):
                        errors.extend(result.get('errors', []))
                    else:
                        warnings.extend(result.get('warnings', []))
                
                if result and 'details' in result:
                    validation_details.append(result['details'])
                    
            except Exception as e:
                logger.error(f"Validation rule failed: {str(e)}")
                errors.append(f"Validation error: {str(e)}")
        
        return {
            'is_valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings,
            'validation_details': validation_details
        }
    
    def _check_usage_spike(
        self,
        settlement: SettlementRecord,
        session
    ) -> Dict[str, Any]:
        """
        Check for usage quantity spike (>50% increase from previous period)
        
        Args:
            settlement: Current settlement
            session: Database session
            
        Returns:
            Validation result with warnings for usage spikes
        """
        warnings = []
        details = {}
        
        try:
            # Get previous settlement for same customer
            previous_settlement = session.query(SettlementRecord).filter(
                SettlementRecord.customer_id == settlement.customer_id,
                SettlementRecord.id != settlement.id,
                SettlementRecord.status != 'draft'
            ).order_by(
                SettlementRecord.period_end.desc()
            ).first()
            
            if previous_settlement and previous_settlement.usage_quantity:
                current_usage = settlement.usage_quantity
                previous_usage = previous_settlement.usage_quantity
                
                if previous_usage > 0:
                    usage_change = (current_usage - previous_usage) / previous_usage * 100
                    
                    details['usage_comparison'] = {
                        'current_usage': float(current_usage),
                        'previous_usage': float(previous_usage),
                        'change_percentage': float(usage_change)
                    }
                    
                    if usage_change > 50:
                        warnings.append(
                            f"用量突增警告：当前用量 {float(current_usage)} 比上期用量 {float(previous_usage)} 增长了 {usage_change:.2f}%"
                        )
                    elif usage_change < -50:
                        warnings.append(
                            f"用量骤降警告：当前用量 {float(current_usage)} 比上期用量 {float(previous_usage)} 下降了 {abs(usage_change):.2f}%"
                        )
        
        except Exception as e:
            logger.error(f"Usage spike check failed: {str(e)}")
        
        return {
            'is_valid': True,  # Usage spike is a warning, not an error
            'is_error': False,
            'warnings': warnings,
            'details': {
                'check': 'usage_spike',
                'data': details
            }
        }
    
    def _check_unit_price_consistency(
        self,
        settlement: SettlementRecord,
        session
    ) -> Dict[str, Any]:
        """
        Check unit price consistency with price config
        
        Args:
            settlement: Settlement to check
            session: Database session
            
        Returns:
            Validation result with errors for price inconsistencies
        """
        errors = []
        details = {}
        
        try:
            # Get price config
            config = session.query(PriceConfig).filter(
                PriceConfig.id == settlement.config_id
            ).first()
            
            if config:
                expected_price = config.unit_price
                actual_price = settlement.unit_price
                
                details['price_comparison'] = {
                    'expected_price': float(expected_price) if expected_price else None,
                    'actual_price': float(actual_price) if actual_price else None
                }
                
                if expected_price and actual_price:
                    price_diff = abs(float(expected_price) - float(actual_price))
                    
                    # Allow 1% tolerance
                    if price_diff > float(expected_price) * 0.01:
                        errors.append(
                            f"单价不一致：期望单价 ¥{float(expected_price)}，实际单价 ¥{float(actual_price)}，差异 {price_diff:.4f}"
                        )
        
        except Exception as e:
            logger.error(f"Price consistency check failed: {str(e)}")
        
        return {
            'is_valid': len(errors) == 0,
            'is_error': True,
            'errors': errors,
            'details': {
                'check': 'unit_price_consistency',
                'data': details
            }
        }
    
    def _check_total_amount_calculation(
        self,
        settlement: SettlementRecord,
        session
    ) -> Dict[str, Any]:
        """
        Check total amount calculation accuracy
        
        Args:
            settlement: Settlement to check
            session: Database session
            
        Returns:
            Validation result with errors for calculation errors
        """
        errors = []
        details = {}
        
        try:
            if settlement.usage_quantity and settlement.unit_price:
                expected_total = settlement.usage_quantity * settlement.unit_price
                actual_total = settlement.total_amount
                
                details['amount_calculation'] = {
                    'expected_total': float(expected_total),
                    'actual_total': float(actual_total),
                    'difference': float(abs(expected_total - actual_total))
                }
                
                # Allow small floating point differences
                if abs(float(expected_total) - float(actual_total)) > 0.01:
                    errors.append(
                        f"总金额计算错误：期望总额 ¥{float(expected_total):.2f}，实际总额 ¥{float(actual_total):.2f}，差异 ¥{abs(float(expected_total) - float(actual_total)):.2f}"
                    )
        
        except Exception as e:
            logger.error(f"Amount calculation check failed: {str(e)}")
        
        return {
            'is_valid': len(errors) == 0,
            'is_error': True,
            'errors': errors,
            'details': {
                'check': 'total_amount_calculation',
                'data': details
            }
        }
    
    def _check_negative_values(
        self,
        settlement: SettlementRecord,
        session
    ) -> Dict[str, Any]:
        """
        Check for negative values in settlement data
        
        Args:
            settlement: Settlement to check
            session: Database session
            
        Returns:
            Validation result with errors for negative values
        """
        errors = []
        
        try:
            if settlement.usage_quantity and settlement.usage_quantity < 0:
                errors.append(f"用量不能为负数：{float(settlement.usage_quantity)}")
            
            if settlement.unit_price and settlement.unit_price < 0:
                errors.append(f"单价不能为负数：¥{float(settlement.unit_price)}")
            
            if settlement.total_amount and settlement.total_amount < 0:
                errors.append(f"总金额不能为负数：¥{float(settlement.total_amount)}")
        
        except Exception as e:
            logger.error(f"Negative value check failed: {str(e)}")
        
        return {
            'is_valid': len(errors) == 0,
            'is_error': True,
            'errors': errors,
            'details': {
                'check': 'negative_values'
            }
        }
    
    def mark_as_validated(
        self,
        settlement: SettlementRecord,
        session,
        validated_by: int,
        validation_result: Dict[str, Any]
    ):
        """
        Mark settlement as validated
        
        Args:
            settlement: Settlement to mark
            session: Database session
            validated_by: User ID who validated
            validation_result: Result from validate_settlement
        """
        settlement.validation_status = 'validated' if validation_result['is_valid'] else 'invalid'
        settlement.validation_errors = validation_result['errors']
        settlement.validation_warnings = validation_result['warnings']
        settlement.validated_at = datetime.utcnow()
        settlement.validated_by = validated_by
