# OP_CMS HTTP Client
"""HTTP request utilities for API adapters"""

import requests
from typing import Dict, Any, Optional, List
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import logging

logger = logging.getLogger(__name__)


class HTTPClient:
    """HTTP client with retry and timeout support"""
    
    def __init__(
        self,
        timeout: int = 30,
        retry_count: int = 3,
        retry_delay: float = 1.0,
        verify_ssl: bool = True
    ):
        """
        Initialize HTTP client
        
        Args:
            timeout: Request timeout in seconds
            retry_count: Number of retry attempts
            retry_delay: Delay between retries in seconds
            verify_ssl: Whether to verify SSL certificates
        """
        self.timeout = timeout
        self.retry_count = retry_count
        self.retry_delay = retry_delay
        self.verify_ssl = verify_ssl
        self._session = self._create_session()
    
    def _create_session(self) -> requests.Session:
        """Create requests session with retry strategy"""
        session = requests.Session()
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=self.retry_count,
            backoff_factor=self.retry_delay,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS", "POST"]
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        return session
    
    def request(
        self,
        method: str,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        timeout: Optional[int] = None
    ) -> requests.Response:
        """
        Make HTTP request with retry support
        
        Args:
            method: HTTP method (GET, POST, etc.)
            url: Request URL
            headers: Request headers
            params: URL query parameters
            data: Form data
            json: JSON data
            timeout: Request timeout (overrides default)
            
        Returns:
            requests.Response: HTTP response
            
        Raises:
            requests.RequestException: If request fails after retries
        """
        request_timeout = timeout or self.timeout
        
        try:
            response = self._session.request(
                method=method,
                url=url,
                headers=headers,
                params=params,
                data=data,
                json=json,
                timeout=request_timeout,
                verify=self.verify_ssl
            )
            
            logger.debug(f"HTTP {method} {url} - Status: {response.status_code}")
            return response
            
        except requests.exceptions.Timeout as e:
            logger.error(f"Request timeout: {url} - {str(e)}")
            raise
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Connection error: {url} - {str(e)}")
            raise
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {url} - {str(e)}")
            raise
    
    def get(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> requests.Response:
        """Make GET request"""
        return self.request('GET', url, headers=headers, params=params, **kwargs)
    
    def post(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        json: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> requests.Response:
        """Make POST request"""
        return self.request('POST', url, headers=headers, json=json, data=data, **kwargs)
    
    def close(self):
        """Close the session"""
        if self._session:
            self._session.close()
