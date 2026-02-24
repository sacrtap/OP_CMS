"""
Tests for API Adapters
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any

from backend.api_adapters.base_adapter import BaseAPIAdapter, APIResponse
from backend.api_adapters.example_adapter import ExampleUsageAPIAdapter, create_api_adapter
from backend.utils.http_client import HTTPClient
from backend.utils.retry_handler import (
    RetryError,
    CircuitBreaker,
    with_retry,
    FailoverHandler
)
from backend.config.api_config import APIConfig, APIConfigManager, get_api_config_from_env


# ==================== APIResponse Tests ====================

class TestAPIResponse:
    """Tests for APIResponse class"""
    
    def test_successful_response(self):
        """Test successful API response"""
        response = APIResponse(
            success=True,
            data={'usage': 100},
            status_code=200
        )
        
        assert response.success is True
        assert response.data == {'usage': 100}
        assert response.error is None
        assert response.status_code == 200
    
    def test_failed_response(self):
        """Test failed API response"""
        response = APIResponse(
            success=False,
            error="Connection timeout",
            status_code=500
        )
        
        assert response.success is False
        assert response.error == "Connection timeout"
        assert response.status_code == 500
    
    def test_to_dict(self):
        """Test response to_dict conversion"""
        response = APIResponse(
            success=True,
            data={'key': 'value'},
            status_code=200
        )
        
        result = response.to_dict()
        
        assert result['success'] is True
        assert result['data'] == {'key': 'value'}
        assert 'timestamp' in result


# ==================== HTTPClient Tests ====================

class TestHTTPClient:
    """Tests for HTTPClient class"""
    
    def test_client_initialization(self):
        """Test HTTP client initialization"""
        client = HTTPClient(
            timeout=60,
            retry_count=5,
            retry_delay=2.0
        )
        
        assert client.timeout == 60
        assert client.retry_count == 5
        assert client.retry_delay == 2.0
    
    @patch('requests.Session')
    def test_get_request(self, mock_session_class):
        """Test GET request"""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'data': 'test'}
        mock_session.request.return_value = mock_response
        
        client = HTTPClient()
        response = client.get('http://test.com/api')
        
        assert response.status_code == 200
        assert response.json() == {'data': 'test'}


# ==================== CircuitBreaker Tests ====================

class TestCircuitBreaker:
    """Tests for CircuitBreaker class"""
    
    def test_initial_state(self):
        """Test circuit breaker initial state"""
        cb = CircuitBreaker()
        
        assert cb.state == 'closed'
        assert cb.can_execute() is True
    
    def test_opens_after_failures(self):
        """Test circuit breaker opens after threshold failures"""
        cb = CircuitBreaker(failure_threshold=3)
        
        # Record failures
        for _ in range(3):
            cb.record_failure()
        
        assert cb.state == 'open'
        assert cb.can_execute() is False
    
    def test_half_open_after_timeout(self):
        """Test circuit breaker goes half-open after recovery timeout"""
        import time
        
        cb = CircuitBreaker(failure_threshold=2, recovery_timeout=1)
        
        # Open the circuit
        for _ in range(2):
            cb.record_failure()
        
        assert cb.state == 'open'
        
        # Wait for recovery timeout
        time.sleep(1.1)
        
        assert cb.state == 'half-open'
        assert cb.can_execute() is True
    
    def test_closes_after_successful_half_open(self):
        """Test circuit breaker closes after successful requests in half-open"""
        cb = CircuitBreaker(
            failure_threshold=2,
            recovery_timeout=1,
            half_open_requests=2
        )
        
        # Open the circuit
        for _ in range(2):
            cb.record_failure()
        
        # Simulate recovery timeout
        cb._last_failure_time = time.time() - 2
        assert cb.state == 'half-open'
        
        # Record successful requests
        cb.record_success()
        cb.record_success()
        
        assert cb.state == 'closed'


# ==================== Retry Handler Tests ====================

class TestRetryHandler:
    """Tests for retry handler"""
    
    def test_retry_decorator_success(self):
        """Test retry decorator with successful execution"""
        @with_retry(max_retries=3)
        def successful_func():
            return "success"
        
        result = successful_func()
        assert result == "success"
    
    def test_retry_decorator_failure(self):
        """Test retry decorator with all attempts failing"""
        attempt_count = 0
        
        @with_retry(max_retries=2, delay=0.01)
        def failing_func():
            nonlocal attempt_count
            attempt_count += 1
            raise ValueError("Always fails")
        
        with pytest.raises(RetryError):
            failing_func()
        
        # Should have tried 3 times (1 initial + 2 retries)
        assert attempt_count == 3


# ==================== FailoverHandler Tests ====================

class TestFailoverHandler:
    """Tests for FailoverHandler class"""
    
    def test_get_available_endpoint(self):
        """Test getting available endpoint"""
        endpoints = [
            {'name': 'primary', 'url': 'http://primary.com', 'priority': 1},
            {'name': 'secondary', 'url': 'http://secondary.com', 'priority': 2}
        ]
        
        handler = FailoverHandler(endpoints)
        endpoint = handler.get_available_endpoint()
        
        assert endpoint['name'] == 'primary'
    
    def test_failover_to_secondary(self):
        """Test failover to secondary when primary fails"""
        endpoints = [
            {'name': 'primary', 'url': 'http://primary.com', 'priority': 1},
            {'name': 'secondary', 'url': 'http://secondary.com', 'priority': 2}
        ]
        
        handler = FailoverHandler(endpoints)
        
        # Open primary circuit
        handler._circuit_breakers['primary'].record_failure()
        handler._circuit_breakers['primary'].record_failure()
        handler._circuit_breakers['primary'].record_failure()
        
        # Should return secondary
        endpoint = handler.get_available_endpoint()
        assert endpoint['name'] == 'secondary'


# ==================== APIConfig Tests ====================

class TestAPIConfig:
    """Tests for APIConfig class"""
    
    def test_config_creation(self):
        """Test API config creation"""
        config = APIConfig(
            name='Test API',
            base_url='http://test.com',
            api_key='test-key',
            timeout=60
        )
        
        assert config.name == 'Test API'
        assert config.base_url == 'http://test.com'
        assert config.api_key == 'test-key'
        assert config.timeout == 60
    
    def test_to_dict(self):
        """Test config to_dict conversion"""
        config = APIConfig(
            name='Test API',
            base_url='http://test.com'
        )
        
        result = config.to_dict()
        
        assert result['name'] == 'Test API'
        assert result['base_url'] == 'http://test.com'
        assert result['timeout'] == 30  # default


# ==================== ExampleAdapter Tests ====================

class TestExampleUsageAPIAdapter:
    """Tests for ExampleUsageAPIAdapter class"""
    
    def test_adapter_creation(self):
        """Test adapter creation with config"""
        config = {
            'base_url': 'http://api.example.com',
            'api_key': 'test-key',
            'timeout': 30
        }
        
        adapter = ExampleUsageAPIAdapter(config)
        
        assert adapter.base_url == 'http://api.example.com'
        assert adapter.timeout == 30
    
    def test_get_headers(self):
        """Test header generation"""
        config = {
            'base_url': 'http://api.example.com',
            'api_key': 'test-key',
            'headers': {'X-Custom': 'value'}
        }
        
        adapter = ExampleUsageAPIAdapter(config)
        headers = adapter._get_headers()
        
        assert headers['Content-Type'] == 'application/json'
        assert headers['X-API-Key'] == 'test-key'
        assert headers['X-Custom'] == 'value'
    
    @patch.object(HTTPClient, 'get')
    def test_get_usage_data_success(self, mock_get):
        """Test successful usage data fetch"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'usage': 1000}
        mock_response.headers = {}
        mock_get.return_value = mock_response
        
        config = {
            'base_url': 'http://api.example.com',
            'api_key': 'test-key'
        }
        
        adapter = ExampleUsageAPIAdapter(config)
        adapter._authenticated = True
        
        response = adapter.get_usage_data(
            customer_id='C001',
            start_date=datetime.now() - timedelta(days=30),
            end_date=datetime.now()
        )
        
        assert response.success is True
        assert response.data == {'usage': 1000}
        assert response.status_code == 200
    
    def test_factory_function(self):
        """Test adapter factory function"""
        config = {
            'base_url': 'http://api.example.com',
            'api_key': 'test-key'
        }
        
        adapter = create_api_adapter('example', config)
        
        assert isinstance(adapter, ExampleUsageAPIAdapter)
    
    def test_factory_function_invalid_type(self):
        """Test factory function with invalid adapter type"""
        config = {'base_url': 'http://api.example.com'}
        
        with pytest.raises(ValueError) as exc_info:
            create_api_adapter('invalid', config)
        
        assert 'Unknown adapter type' in str(exc_info.value)


# ==================== Integration Tests ====================

class TestAdapterIntegration:
    """Integration tests for API adapters"""
    
    def test_full_workflow(self):
        """Test complete adapter workflow"""
        config = {
            'base_url': 'http://api.example.com',
            'api_key': 'test-key',
            'timeout': 30,
            'retry_count': 3
        }
        
        adapter = ExampleUsageAPIAdapter(config)
        
        # Test connection validation (will fail without real server)
        # This tests the error handling
        result = adapter.validate_connection()
        assert isinstance(result, bool)
        
        # Cleanup
        adapter.close()
