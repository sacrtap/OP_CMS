# OP_CMS Example API Adapter
"""Example implementation of API adapter for usage data collection"""

from typing import Dict, Any, Optional
from datetime import datetime
import logging

from backend.api_adapters.base_adapter import BaseAPIAdapter, APIResponse
from backend.utils.http_client import HTTPClient
from backend.utils.retry_handler import with_retry, CircuitBreaker

logger = logging.getLogger(__name__)


class ExampleUsageAPIAdapter(BaseAPIAdapter):
    """
    Example API adapter for fetching usage data
    
    This adapter demonstrates how to implement an API adapter for
    external usage data collection systems.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize example API adapter
        
        Args:
            config: API configuration
        """
        super().__init__(config)
        self.http_client = HTTPClient(
            timeout=self.timeout,
            retry_count=self.retry_count,
            retry_delay=self.retry_delay,
            verify_ssl=config.get('verify_ssl', True)
        )
        self._authenticated = False
        self._circuit_breaker = CircuitBreaker()
    
    def authenticate(self) -> bool:
        """
        Authenticate with the API service
        
        Returns:
            bool: True if authentication successful
        """
        try:
            api_key = self.config.get('api_key')
            api_secret = self.config.get('api_secret')
            
            if not api_key:
                logger.warning("No API key provided")
                return False
            
            # Example: Authenticate and get access token
            auth_url = f"{self.base_url}/auth/token"
            headers = {
                'Content-Type': 'application/json',
                'X-API-Key': api_key
            }
            
            if api_secret:
                headers['X-API-Secret'] = api_secret
            
            response = self.http_client.post(auth_url, headers=headers, json={})
            
            if response.status_code == 200:
                self._authenticated = True
                logger.info("Authentication successful")
                return True
            else:
                logger.error(f"Authentication failed: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            return False
    
    @with_retry(
        max_retries=3,
        delay=1.0,
        backoff=2.0,
        circuit_breaker=None  # Will be set by instance
    )
    def get_usage_data(
        self,
        customer_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> APIResponse:
        """
        Fetch usage data for a customer within date range
        
        Args:
            customer_id: Customer identifier
            start_date: Start date of usage period
            end_date: End date of usage period
            
        Returns:
            APIResponse: Standardized response with usage data
        """
        try:
            # Check authentication
            if not self._authenticated:
                if not self.authenticate():
                    return APIResponse(
                        success=False,
                        error="Authentication required",
                        status_code=401
                    )
            
            # Build request
            url = f"{self.base_url}/usage-data"
            headers = self._get_headers()
            params = {
                'customer_id': customer_id,
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat()
            }
            
            self._log_request('GET', url, params)
            
            # Make request
            response = self.http_client.get(url, headers=headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                self._log_response(APIResponse(success=True, data=data))
                return APIResponse(
                    success=True,
                    data=data,
                    status_code=200,
                    headers=dict(response.headers)
                )
            else:
                error_msg = f"API returned status {response.status_code}"
                try:
                    error_data = response.json()
                    error_msg = error_data.get('error', error_msg)
                except:
                    pass
                
                return APIResponse(
                    success=False,
                    error=error_msg,
                    status_code=response.status_code
                )
                
        except Exception as e:
            logger.error(f"Failed to fetch usage data: {str(e)}")
            return APIResponse(
                success=False,
                error=str(e),
                status_code=500
            )
    
    def validate_connection(self) -> bool:
        """
        Validate API connection and configuration
        
        Returns:
            bool: True if connection is valid
        """
        try:
            # Simple health check endpoint
            health_url = f"{self.base_url}/health"
            response = self.http_client.get(health_url, timeout=5)
            
            if response.status_code == 200:
                logger.info("API connection validated")
                return True
            else:
                logger.warning(f"API health check failed: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"API connection validation failed: {str(e)}")
            return False
    
    def _get_headers(self) -> Dict[str, str]:
        """Get request headers including authentication"""
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        api_key = self.config.get('api_key')
        if api_key:
            headers['X-API-Key'] = api_key
        
        # Add any custom headers from config
        custom_headers = self.config.get('headers', {})
        headers.update(custom_headers)
        
        return headers
    
    def close(self):
        """Close HTTP client connection"""
        if self.http_client:
            self.http_client.close()
        super().close()


# Factory function
def create_api_adapter(adapter_type: str, config: Dict[str, Any]) -> BaseAPIAdapter:
    """
    Factory function to create API adapter instances
    
    Args:
        adapter_type: Type of adapter ('example', 'custom', etc.)
        config: Adapter configuration
        
    Returns:
        BaseAPIAdapter instance
        
    Raises:
        ValueError: If adapter_type is not recognized
    """
    adapters = {
        'example': ExampleUsageAPIAdapter
    }
    
    if adapter_type not in adapters:
        raise ValueError(
            f"Unknown adapter type: {adapter_type}. "
            f"Available types: {list(adapters.keys())}"
        )
    
    return adapters[adapter_type](config)
