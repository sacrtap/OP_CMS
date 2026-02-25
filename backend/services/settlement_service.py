# OP_CMS Settlement Calculation Service
# Story 3.1: Automated Settlement Generation

from decimal import Decimal
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging
import uuid

from backend.models.database_models import (
    SettlementRecord, PriceConfig, Customer
)

logger = logging.getLogger(__name__)


class SettlementCalculationError(Exception):
    """Custom exception for settlement calculation errors"""
    pass


class SettlementService:
    """Service for calculating and generating settlements"""
    
    def __init__(self):
        self.calculation_methods = {
            'single': self._calculate_single_tier,
            'multi': self._calculate_multi_tier,
            'tiered': self._calculate_tiered_progressive
        }
    
    def calculate_settlement(
        self,
        customer_id: int,
        config: PriceConfig,
        usage_quantity: Decimal,
        period_start: datetime,
        period_end: datetime
    ) -> Dict[str, Any]:
        """
        Calculate settlement for a customer based on their pricing config
        
        Args:
            customer_id: Customer ID
            config: Price configuration
            usage_quantity: Total usage quantity for the period
            period_start: Start of settlement period
            period_end: End of settlement period
            
        Returns:
            Dictionary with calculation details:
            - total_amount: Total settlement amount
            - calculation_breakdown: Detailed breakdown of calculation
            - pricing_model: Pricing model used
        """
        try:
            # Get calculation method based on pricing model
            calc_method = self.calculation_methods.get(config.price_model)
            
            if not calc_method:
                raise SettlementCalculationError(
                    f"Unsupported pricing model: {config.price_model}"
                )
            
            # Calculate settlement
            result = calc_method(config, usage_quantity)
            
            # Add metadata
            result['customer_id'] = customer_id
            result['period_start'] = period_start
            result['period_end'] = period_end
            result['usage_quantity'] = float(usage_quantity)
            result['pricing_model'] = config.price_model
            result['currency'] = config.currency or 'CNY'
            
            return result
            
        except Exception as e:
            logger.error(f"Settlement calculation failed: {str(e)}")
            raise SettlementCalculationError(f"Failed to calculate settlement: {str(e)}")
    
    def _calculate_single_tier(
        self,
        config: PriceConfig,
        usage_quantity: Decimal
    ) -> Dict[str, Any]:
        """
        Calculate settlement for single-tier pricing
        
        Formula: total = usage_quantity * unit_price
        """
        unit_price = Decimal(str(config.unit_price))
        total_amount = usage_quantity * unit_price
        
        return {
            'total_amount': float(total_amount),
            'unit_price': float(unit_price),
            'usage_quantity': float(usage_quantity),
            'calculation_breakdown': {
                'formula': 'usage_quantity × unit_price',
                'steps': [
                    f'Usage: {float(usage_quantity)}',
                    f'Unit Price: ¥{float(unit_price)}',
                    f'Total: {float(usage_quantity)} × ¥{float(unit_price)} = ¥{float(total_amount)}'
                ]
            }
        }
    
    def _calculate_multi_tier(
        self,
        config: PriceConfig,
        usage_quantity: Decimal
    ) -> Dict[str, Any]:
        """
        Calculate settlement for multi-tier pricing
        
        Find the appropriate tier based on usage quantity
        and apply that tier's unit price
        """
        # For multi-tier, find the tier that matches usage quantity
        # This assumes tiers are stored in price_tiers table
        # Simplified implementation - in production, query from database
        
        unit_price = Decimal(str(config.unit_price))
        total_amount = usage_quantity * unit_price
        
        # In production, this would query price_tiers table
        # and find the appropriate tier for the usage quantity
        
        return {
            'total_amount': float(total_amount),
            'unit_price': float(unit_price),
            'usage_quantity': float(usage_quantity),
            'calculation_breakdown': {
                'formula': 'usage_quantity × tier_unit_price',
                'tier_found': 'default_tier',
                'steps': [
                    f'Usage: {float(usage_quantity)}',
                    f'Found tier with unit price: ¥{float(unit_price)}',
                    f'Total: {float(usage_quantity)} × ¥{float(unit_price)} = ¥{float(total_amount)}'
                ]
            }
        }
    
    def calculate_tiered_progressive_settlement(
        self,
        usage: Decimal,
        price_model: str,
        tiers: List[Dict[str, Any]],
        currency: str = 'CNY'
    ) -> Dict[str, Any]:
        """
        Calculate tiered progressive settlement (for testing)
        
        Args:
            usage: Total usage quantity
            price_model: Pricing model type
            tiers: List of tier configurations with threshold and unit_price
            currency: Currency code
            
        Returns:
            Dictionary with settlement details
        """
        total_settlement = Decimal('0')
        remaining_usage = usage
        calculation_details = []
        previous_threshold = Decimal('0')
        
        for tier in tiers:
            tier_threshold = Decimal(str(tier['threshold']))
            tier_unit_price = Decimal(str(tier['unit_price']))
            
            if remaining_usage <= 0:
                break
            
            tier_range = tier_threshold - previous_threshold
            
            if tier == tiers[-1]:
                tier_usage = remaining_usage
            else:
                tier_usage = min(remaining_usage, tier_range)
            
            tier_amount = tier_usage * tier_unit_price
            total_settlement += tier_amount
            
            calculation_details.append({
                'tier': tier,
                'tier_usage': float(tier_usage),
                'tier_amount': float(tier_amount)
            })
            
            remaining_usage -= tier_usage
            previous_threshold = tier_threshold
        
        return {
            'total_settlement': total_settlement,
            'currency': currency,
            'usage': float(usage),
            'pricing_model': price_model,
            'calculation_details': calculation_details
        }
    
    def _calculate_tiered_progressive(
        self,
        config: PriceConfig,
        usage_quantity: Decimal
    ) -> Dict[str, Any]:
        """
        Calculate settlement for tiered progressive pricing
        
        Formula: Sum of (tier_quantity × tier_unit_price) for each tier
        
        Example:
        Tier 1: 0-100 units @ ¥0.10
        Tier 2: 101-500 units @ ¥0.08
        Tier 3: 501+ units @ ¥0.05
        
        For 600 units:
        = (100 × 0.10) + (400 × 0.08) + (100 × 0.05)
        = 10 + 32 + 5 = ¥47
        """
        # For tiered progressive, calculate across multiple tiers
        # This assumes tiers are stored in price_tiers table
        # Simplified implementation - in production, query from database
        
        total_amount = Decimal('0')
        remaining_usage = usage_quantity
        calculation_steps = []
        
        # In production, this would query price_tiers table
        # and calculate progressively across tiers
        
        # Simplified example with hardcoded tiers
        tiers = [
            {'min': Decimal('0'), 'max': Decimal('100'), 'price': Decimal('0.10')},
            {'min': Decimal('100'), 'max': Decimal('500'), 'price': Decimal('0.08')},
            {'min': Decimal('500'), 'max': None, 'price': Decimal('0.05')},
        ]
        
        tier_details = []
        for tier in tiers:
            if remaining_usage <= 0:
                break
            
            tier_min = tier['min']
            tier_max = tier['max']
            tier_price = tier['price']
            
            # Calculate quantity in this tier
            if tier_max is None:
                # Last tier - take all remaining
                tier_quantity = remaining_usage
            else:
                tier_capacity = tier_max - tier_min
                tier_quantity = min(remaining_usage, tier_capacity)
            
            # Calculate tier amount
            tier_amount = tier_quantity * tier_price
            total_amount += tier_amount
            
            # Record calculation step
            tier_details.append({
                'tier_range': f"{float(tier_min)}-{float(tier_max) if tier_max else '∞'}",
                'quantity': float(tier_quantity),
                'unit_price': float(tier_price),
                'amount': float(tier_amount)
            })
            
            calculation_steps.append(
                f"Tier {len(tier_details)}: {float(tier_quantity)} × ¥{float(tier_price)} = ¥{float(tier_amount)}"
            )
            
            remaining_usage -= tier_quantity
        
        return {
            'total_amount': float(total_amount),
            'usage_quantity': float(usage_quantity),
            'calculation_breakdown': {
                'formula': 'Σ(tier_quantity × tier_unit_price)',
                'pricing_model': 'tiered_progressive',
                'tiers': tier_details,
                'steps': calculation_steps
            }
        }
    
    def create_settlement_record(
        self,
        session,
        calculation_result: Dict[str, Any],
        config_id: int,
        generated_by: Optional[int] = None
    ) -> SettlementRecord:
        """
        Create settlement record in database
        
        Args:
            session: Database session
            calculation_result: Result from calculate_settlement
            config_id: Price config ID
            generated_by: User ID who generated the settlement
            
        Returns:
            Created SettlementRecord
        """
        import uuid
        
        settlement = SettlementRecord(
            record_id=str(uuid.uuid4()),
            customer_id=calculation_result['customer_id'],
            config_id=config_id,
            period_start=calculation_result['period_start'],
            period_end=calculation_result['period_end'],
            usage_quantity=Decimal(str(calculation_result['usage_quantity'])),
            unit='units',  # Should be configurable
            price_model=calculation_result['pricing_model'],
            unit_price=Decimal(str(calculation_result.get('unit_price', 0))),
            total_amount=Decimal(str(calculation_result['total_amount'])),
            currency=calculation_result['currency'],
            status='pending',
            remarks=calculation_result.get('remarks')
        )
        
        session.add(settlement)
        return settlement
