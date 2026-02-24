# OP_CMS External API Adapters
"""Base adapter interface and implementations for external API integration"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class APIResponse:
    """Standardized API response wrapper"""
    
    def __init__(
        self,
        success: bool,
        data: Optional[Any] = None,
        error: Optional[str] = None,
        status_code: int = 200,
        headers: Optional[Dict[str, str]] = None
    ):
        self.success = success
        self.data = data
        self.error = error
        self.status_code = status_code
        self.headers = headers or {}
        self.timestamp = datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert response to dictionary"""
        return {
            'success': self.success,
            'data': self.data,
            'error': self.error,
            'status_code': self.status_code,
            'timestamp': self.timestamp.isoformat()
        }


class BaseAPIAdapter(ABC):
    """Abstract base class for all API adapters"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize API adapter with configuration
        
        Args:
            config: API configuration containing base_url, auth, timeouts, etc.
        """
        self.config = config
        self.base_url = config.get('base_url', '')
        self.timeout = config.get('timeout', 30)
        self.retry_count = config.get('retry_count', 3)
        self.retry_delay = config.get('retry_delay', 1.0)
        self._session = None
    
    @abstractmethod
    def authenticate(self) -> bool:
        """
        Authenticate with the API service
        
        Returns:
            bool: True if authentication successful
        """
        pass
    
    @abstractmethod
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
        pass
    
    @abstractmethod
    def validate_connection(self) -> bool:
        """
        Validate API connection and configuration
        
        Returns:
            bool: True if connection is valid
        """
        pass
    
    def _log_request(self, method: str, url: str, params: Dict[str, Any]):
        """Log API request details"""
        logger.debug(f"API Request: {method} {url} - Params: {params}")
    
    def _log_response(self, response: APIResponse):
        """Log API response details"""
        if response.success:
            logger.debug(f"API Response: Success - {response.status_code}")
        else:
            logger.error(f"API Response: Failed - {response.error}")
    
    def close(self):
        """Close any open connections or sessions"""
        if self._session:
            self._session.close()
            self._session = None
