"""
Tests for Settlement Calculation - Story 3.1
"""

import pytest
from decimal import Decimal
from datetime import datetime

from backend.services.settlement_service import SettlementService, SettlementCalculationError


class TestSettlementCalculation:
    """Tests for settlement calculation logic"""
    
    def test_single_tier_calculation(self):
        """Test single-tier pricing calculation"""
        service = SettlementService()
        
        # Mock config
        config = type('PriceConfig', (), {
            'price_model': 'single',
            'unit_price': Decimal('0.10'),
            'currency': 'CNY'
        })()
        
        result = service.calculate_settlement(
            customer_id=1,
            config=config,
            usage_quantity=Decimal('100'),
            period_start=datetime(2026, 2, 1),
            period_end=datetime(2026, 2, 28)
        )
        
        assert result['total_amount'] == 10.0
        assert result['pricing_model'] == 'single'
        assert result['currency'] == 'CNY'
    
    def test_tiered_progressive_calculation(self):
        """Test tiered progressive pricing calculation"""
        service = SettlementService()
        
        # Mock config
        config = type('PriceConfig', (), {
            'price_model': 'tiered',
            'unit_price': Decimal('0.10'),
            'currency': 'CNY'
        })()
        
        result = service.calculate_settlement(
            customer_id=1,
            config=config,
            usage_quantity=Decimal('600'),
            period_start=datetime(2026, 2, 1),
            period_end=datetime(2026, 2, 28)
        )
        
        # Tier 1: 100 × 0.10 = 10
        # Tier 2: 400 × 0.08 = 32
        # Tier 3: 100 × 0.05 = 5
        # Total: 47
        assert result['total_amount'] == 47.0
        assert result['pricing_model'] == 'tiered'
        assert 'calculation_breakdown' in result
        assert 'tiers' in result['calculation_breakdown']
    
    def test_settlement_service_initialization(self):
        """Test settlement service initialization"""
        service = SettlementService()
        
        assert 'single' in service.calculation_methods
        assert 'multi' in service.calculation_methods
        assert 'tiered' in service.calculation_methods


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
