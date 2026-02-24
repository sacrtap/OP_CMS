"""
Tests for Settlement Service - Story 3.1
Tests for settlement calculation and generation
"""

import pytest
from decimal import Decimal
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock

from backend.services.settlement_service import (
    SettlementService,
    SettlementCalculationError
)


class TestSettlementServiceInit:
    """Tests for SettlementService initialization"""
    
    def test_init_default_values(self):
        """Test initialization with default values"""
        service = SettlementService()
        
        assert 'single' in service.calculation_methods
        assert 'multi' in service.calculation_methods
        assert 'tiered' in service.calculation_methods
    
    def test_init_calculation_methods(self):
        """Test calculation methods are properly mapped"""
        service = SettlementService()
        
        assert callable(service.calculation_methods['single'])
        assert callable(service.calculation_methods['multi'])
        assert callable(service.calculation_methods['tiered'])


class TestCalculateSingleTierSettlement:
    """Tests for single-tier pricing calculation"""
    
    def test_calculate_single_tier_basic(self):
        """Test basic single-tier calculation"""
        service = SettlementService()
        
        # Mock config
        config = Mock()
        config.price_model = 'single'
        config.unit_price = Decimal('0.10')
        config.currency = 'CNY'
        
        usage = Decimal('100')
        period_start = datetime(2026, 1, 1)
        period_end = datetime(2026, 1, 31)
        
        result = service.calculate_settlement(
            customer_id=1,
            config=config,
            usage_quantity=usage,
            period_start=period_start,
            period_end=period_end
        )
        
        assert result['total_amount'] == 10.0  # 100 * 0.10
        assert result['unit_price'] == 0.1
        assert result['usage_quantity'] == 100.0
        assert result['pricing_model'] == 'single'
        assert result['currency'] == 'CNY'
    
    def test_calculate_single_tier_large_amount(self):
        """Test single-tier with large amounts"""
        service = SettlementService()
        
        config = Mock()
        config.price_model = 'single'
        config.unit_price = Decimal('125.50')
        config.currency = 'USD'
        
        usage = Decimal('10000')
        
        result = service.calculate_settlement(
            customer_id=1,
            config=config,
            usage_quantity=usage,
            period_start=datetime(2026, 1, 1),
            period_end=datetime(2026, 1, 31)
        )
        
        assert result['total_amount'] == 1255000.0  # 10000 * 125.50
        assert result['currency'] == 'USD'
    
    def test_calculate_single_tier_zero_usage(self):
        """Test single-tier with zero usage"""
        service = SettlementService()
        
        config = Mock()
        config.price_model = 'single'
        config.unit_price = Decimal('0.10')
        config.currency = 'CNY'
        
        usage = Decimal('0')
        
        result = service.calculate_settlement(
            customer_id=1,
            config=config,
            usage_quantity=usage,
            period_start=datetime(2026, 1, 1),
            period_end=datetime(2026, 1, 31)
        )
        
        assert result['total_amount'] == 0.0
        assert result['usage_quantity'] == 0.0
    
    def test_calculate_single_tier_decimal_precision(self):
        """Test single-tier maintains decimal precision"""
        service = SettlementService()
        
        config = Mock()
        config.price_model = 'single'
        config.unit_price = Decimal('0.123456')
        config.currency = 'CNY'
        
        usage = Decimal('1234.567')
        
        result = service.calculate_settlement(
            customer_id=1,
            config=config,
            usage_quantity=usage,
            period_start=datetime(2026, 1, 1),
            period_end=datetime(2026, 1, 31)
        )
        
        # Check calculation is precise
        expected = float(Decimal('1234.567') * Decimal('0.123456'))
        assert abs(result['total_amount'] - expected) < 0.0001


class TestCalculateMultiTierSettlement:
    """Tests for multi-tier pricing calculation"""
    
    def test_calculate_multi_tier_basic(self):
        """Test basic multi-tier calculation"""
        service = SettlementService()
        
        config = Mock()
        config.price_model = 'multi'
        config.unit_price = Decimal('0.08')
        config.currency = 'CNY'
        
        usage = Decimal('500')
        
        result = service.calculate_settlement(
            customer_id=1,
            config=config,
            usage_quantity=usage,
            period_start=datetime(2026, 1, 1),
            period_end=datetime(2026, 1, 31)
        )
        
        assert result['total_amount'] == 40.0  # 500 * 0.08
        assert result['pricing_model'] == 'multi'
    
    def test_calculate_multi_tier_default_tier(self):
        """Test multi-tier uses default tier when no match"""
        service = SettlementService()
        
        config = Mock()
        config.price_model = 'multi'
        config.unit_price = Decimal('0.15')
        config.currency = 'CNY'
        
        usage = Decimal('1000')
        
        result = service.calculate_settlement(
            customer_id=1,
            config=config,
            usage_quantity=usage,
            period_start=datetime(2026, 1, 1),
            period_end=datetime(2026, 1, 31)
        )
        
        # Should use default tier price
        assert result['total_amount'] == 150.0
        assert 'default_tier' in str(result.get('calculation_breakdown', {}))


class TestCalculateTieredProgressiveSettlement:
    """Tests for tiered progressive settlement calculation"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.service = SettlementService()
    
    def test_calculate_tiered_progressive_basic(self):
        """Test basic tiered progressive calculation"""
        usage = Decimal('250')
        price_model = 'tiered_progressive'
        
        tiers = [
            {'threshold': Decimal('100'), 'unit_price': Decimal('0.1')},
            {'threshold': Decimal('200'), 'unit_price': Decimal('0.08')},
            {'threshold': Decimal('500'), 'unit_price': Decimal('0.06')}
        ]
        
        result = self.service.calculate_tiered_progressive_settlement(usage, price_model, tiers, 'CNY')
        
        # 100 * 0.1 + 100 * 0.08 + 50 * 0.06 = 10 + 8 + 3 = 21
        assert result['total_settlement'] == Decimal('21.00')
        assert result['currency'] == 'CNY'
        assert result['pricing_model'] == 'tiered_progressive'
    
    def test_calculate_tiered_progressive_single_tier(self):
        """Test tiered progressive within first tier"""
        service = SettlementService()
        
        config = Mock()
        config.price_model = 'tiered'
        config.unit_price = Decimal('0.10')
        config.currency = 'CNY'
        
        usage = Decimal('50')
        
        result = service.calculate_settlement(
            customer_id=1,
            config=config,
            usage_quantity=usage,
            period_start=datetime(2026, 1, 1),
            period_end=datetime(2026, 1, 31)
        )
        
        # Expected: 50 * 0.10 = 5
        assert result['total_amount'] == 5.0
    
    def test_calculate_tiered_progressive_exact_tier_boundary(self):
        """Test tiered progressive at exact tier boundary"""
        service = SettlementService()
        
        config = Mock()
        config.price_model = 'tiered'
        config.unit_price = Decimal('0.10')
        config.currency = 'CNY'
        
        usage = Decimal('100')
        
        result = service.calculate_settlement(
            customer_id=1,
            config=config,
            usage_quantity=usage,
            period_start=datetime(2026, 1, 1),
            period_end=datetime(2026, 1, 31)
        )
        
        # Expected: 100 * 0.10 = 10 (exactly at first tier boundary)
        assert result['total_amount'] == 10.0
    
    def test_calculate_tiered_progressive_large_usage(self):
        """Test tiered progressive with very large usage"""
        service = SettlementService()
        
        config = Mock()
        config.price_model = 'tiered'
        config.unit_price = Decimal('0.10')
        config.currency = 'CNY'
        
        usage = Decimal('10000')
        
        result = service.calculate_settlement(
            customer_id=1,
            config=config,
            usage_quantity=usage,
            period_start=datetime(2026, 1, 1),
            period_end=datetime(2026, 1, 31)
        )
        
        # Expected: (100 * 0.10) + (400 * 0.08) + (9500 * 0.05) = 10 + 32 + 475 = 517
        assert result['total_amount'] == 517.0
    
    def test_calculate_tiered_progressive_breakdown(self):
        """Test tiered progressive calculation breakdown"""
        service = SettlementService()
        
        config = Mock()
        config.price_model = 'tiered'
        config.unit_price = Decimal('0.10')
        config.currency = 'CNY'
        
        usage = Decimal('600')
        
        result = service.calculate_settlement(
            customer_id=1,
            config=config,
            usage_quantity=usage,
            period_start=datetime(2026, 1, 1),
            period_end=datetime(2026, 1, 31)
        )
        
        breakdown = result['calculation_breakdown']
        
        assert breakdown['formula'] == 'Σ(tier_quantity × tier_unit_price)'
        assert breakdown['pricing_model'] == 'tiered_progressive'
        assert 'tiers' in breakdown
        assert 'steps' in breakdown
        assert len(breakdown['tiers']) == 3  # All three tiers used


class TestCreateSettlementRecord:
    """Tests for creating settlement records in database"""
    
    @patch('backend.services.settlement_service.SettlementRecord')
    @patch('backend.services.settlement_service.uuid.uuid4')
    def test_create_settlement_record_optional_fields(self, mock_uuid):
        """Test settlement record with optional fields"""
        service = SettlementService()
        
        mock_uuid_module.uuid4.return_value = 'test-uuid-456'
        mock_session = Mock()
        
        calculation_result = {
            'customer_id': 1,
            'period_start': datetime(2026, 1, 1),
            'period_end': datetime(2026, 1, 31),
            'usage_quantity': 100.0,
            'pricing_model': 'single',
            'currency': 'CNY',
            'total_amount': 10.0,
            'calculation_breakdown': {'formula': 'test'}
        }
        
        # Mock the record instance
        mock_record_instance = Mock()
        mock_record_instance.generated_by = None
        mock_record_class.return_value = mock_record_instance
        
        result = service.create_settlement_record(
            session=mock_session,
            calculation_result=calculation_result,
            config_id=1
            # generated_by is optional
        )
        
        # Should create record without generated_by
        assert mock_session.add.call_args[0][0].generated_by is None


class TestSettlementServiceErrorHandling:
    """Tests for error handling in SettlementService"""
    
    def test_calculate_settlement_unsupported_pricing_model(self):
        """Test calculation with unsupported pricing model"""
        service = SettlementService()
        
        config = Mock()
        config.price_model = 'unsupported_model'
        config.unit_price = Decimal('0.10')
        config.currency = 'CNY'
        
        with pytest.raises(SettlementCalculationError, match="Unsupported pricing model"):
            service.calculate_settlement(
                customer_id=1,
                config=config,
                usage_quantity=Decimal('100'),
                period_start=datetime(2026, 1, 1),
                period_end=datetime(2026, 1, 31)
            )
    
    @patch.object(SettlementService, '_calculate_single_tier')
    def test_calculate_settlement_calculation_error(self, mock_calc):
        """Test calculation that raises an exception"""
        service = SettlementService()
        
        mock_calc.side_effect = Exception("Calculation failed")
        
        config = Mock()
        config.price_model = 'single'
        config.unit_price = Decimal('0.10')
        config.currency = 'CNY'
        
        with pytest.raises(SettlementCalculationError, match="Failed to calculate"):
            service.calculate_settlement(
                customer_id=1,
                config=config,
                usage_quantity=Decimal('100'),
                period_start=datetime(2026, 1, 1),
                period_end=datetime(2026, 1, 31)
            )


class TestSettlementServiceEdgeCases:
    """Tests for edge cases in SettlementService"""
    
    def test_calculate_with_negative_usage(self):
        """Test calculation with negative usage (should still calculate)"""
        service = SettlementService()
        
        config = Mock()
        config.price_model = 'single'
        config.unit_price = Decimal('0.10')
        config.currency = 'CNY'
        
        usage = Decimal('-100')
        
        result = service.calculate_settlement(
            customer_id=1,
            config=config,
            usage_quantity=usage,
            period_start=datetime(2026, 1, 1),
            period_end=datetime(2026, 1, 31)
        )
        
        # Should calculate with negative value
        assert result['total_amount'] == -10.0
    
    def test_calculate_with_very_small_decimal(self):
        """Test calculation with very small decimal values"""
        service = SettlementService()
        
        config = Mock()
        config.price_model = 'single'
        config.unit_price = Decimal('0.000001')
        config.currency = 'CNY'
        
        usage = Decimal('0.001')
        
        result = service.calculate_settlement(
            customer_id=1,
            config=config,
            usage_quantity=usage,
            period_start=datetime(2026, 1, 1),
            period_end=datetime(2026, 1, 31)
        )
        
        # Should handle small decimals
        assert result['total_amount'] == pytest.approx(0.000000001, rel=1e-9)
    
    def test_calculate_with_none_currency(self):
        """Test calculation with None currency (should default to CNY)"""
        service = SettlementService()
        
        config = Mock()
        config.price_model = 'single'
        config.unit_price = Decimal('0.10')
        config.currency = None
        
        result = service.calculate_settlement(
            customer_id=1,
            config=config,
            usage_quantity=Decimal('100'),
            period_start=datetime(2026, 1, 1),
            period_end=datetime(2026, 1, 31)
        )
        
        assert result['currency'] == 'CNY'


class TestSettlementServiceIntegration:
    """Integration tests for SettlementService"""
    
    @patch('backend.services.settlement_service.uuid.uuid4')
    def test_complete_settlement_workflow(self, mock_uuid):
        """Test complete settlement calculation and record creation"""
        service = SettlementService()
        
        mock_uuid.uuid4.return_value = 'test-uuid'
        mock_session_instance = Mock()
        
        # Step 1: Calculate settlement
        config = Mock()
        config.price_model = 'single'
        config.unit_price = Decimal('0.10')
        config.currency = 'CNY'
        
        calculation_result = service.calculate_settlement(
            customer_id=1,
            config=config,
            usage_quantity=Decimal('100'),
            period_start=datetime(2026, 1, 1),
            period_end=datetime(2026, 1, 31)
        )
        
        assert calculation_result['total_amount'] == 10.0
        
        # Step 2: Create record
        record = service.create_settlement_record(
            session=mock_session_instance,
            calculation_result=calculation_result,
            config_id=1
        )
        
        # Verify both steps completed
        assert calculation_result['total_amount'] == 10.0
        mock_session_instance.add.assert_called_once()
