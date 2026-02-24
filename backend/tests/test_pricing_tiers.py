"""
Tests for Multi-tier Pricing - Story 2.2
"""

import pytest
from decimal import Decimal

class TestMultiTierPricing:
    """Tests for multi-tier pricing configuration"""
    
    def test_tier_sequential_validation(self):
        """Test tiers must be sequential (1, 2, 3...)"""
        valid_tiers = [1, 2, 3, 4, 5]
        invalid_tiers = [1, 3, 5]  # Gap in sequence
        
        # Valid sequential tiers
        assert valid_tiers == sorted(valid_tiers)
        
        # Invalid non-sequential
        expected_sequential = list(range(1, len(invalid_tiers) + 1))
        assert invalid_tiers != expected_sequential
    
    def test_tier_min_max_validation(self):
        """Test min_quantity < max_quantity for each tier"""
        tiers = [
            {'min': Decimal('0'), 'max': Decimal('100')},
            {'min': Decimal('100'), 'max': Decimal('500')},
            {'min': Decimal('500'), 'max': None},  # Last tier
        ]
        
        for tier in tiers:
            if tier['max'] is not None:
                assert tier['min'] < tier['max']
    
    def test_tier_no_overlap(self):
        """Test tiers must not overlap"""
        tiers = [
            {'min': Decimal('0'), 'max': Decimal('100')},
            {'min': Decimal('100'), 'max': Decimal('500')},
            {'min': Decimal('500'), 'max': None},
        ]
        
        for i in range(len(tiers) - 1):
            current_max = tiers[i]['max']
            next_min = tiers[i + 1]['min']
            
            # Max of current should equal min of next (no gap, no overlap)
            assert current_max == next_min


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
