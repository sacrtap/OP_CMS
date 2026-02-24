"""
OP_CMS Backend Test Configuration - Simplified
For unit tests without database dependencies
"""

import pytest
import sys
import os

# Add backend directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


# Simple fixture for mock session
@pytest.fixture
def mock_session():
    """Mock database session for unit tests"""
    from unittest.mock import Mock
    return Mock()
