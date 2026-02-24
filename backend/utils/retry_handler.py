# OP_CMS API Retry Handler
"""Retry and failover mechanisms for API calls"""

import time
import random
from typing import Callable, Any, Optional, List, Dict
from functools import wraps
import logging

logger = logging.getLogger(__name__)


class RetryError(Exception):
    """Exception raised when all retry attempts fail"""
    
    def __init__(self, message: str, last_exception: Optional[Exception] = None):
        super().__init__(message)
        self.last_exception = last_exception


class CircuitBreaker:
    """Circuit breaker pattern implementation"""
    
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        half_open_requests: int = 1
    ):
        """
        Initialize circuit breaker
        
        Args:
            failure_threshold: Number of failures before opening circuit
            recovery_timeout: Seconds to wait before trying again
            half_open_requests: Number of test requests in half-open state
        """
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.half_open_requests = half_open_requests
        
        self._failure_count = 0
        self._last_failure_time: Optional[float] = None
        self._state = 'closed'  # closed, open, half-open
        self._half_open_successes = 0
    
    @property
    def state(self) -> str:
        """Get current circuit state"""
        if self._state == 'open':
            if time.time() - self._last_failure_time >= self.recovery_timeout:
                self._state = 'half-open'
                self._half_open_successes = 0
        return self._state
    
    def record_success(self):
        """Record successful request"""
        self._failure_count = 0
        if self._state == 'half-open':
            self._half_open_successes += 1
            if self._half_open_successes >= self.half_open_requests:
                self._state = 'closed'
        elif self._state == 'closed':
            pass  # Already closed
    
    def record_failure(self):
        """Record failed request"""
        self._failure_count += 1
        self._last_failure_time = time.time()
        
        if self._failure_count >= self.failure_threshold:
            self._state = 'open'
            logger.warning(f"Circuit breaker opened after {self._failure_count} failures")
    
    def can_execute(self) -> bool:
        """Check if request can be executed"""
        current_state = self.state
        if current_state == 'closed':
            return True
        elif current_state == 'half-open':
            return True
        else:  # open
            return False


def with_retry(
    max_retries: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    jitter: bool = True,
    exceptions: tuple = (Exception,),
    circuit_breaker: Optional[CircuitBreaker] = None
):
    """
    Decorator for adding retry logic to functions
    
    Args:
        max_retries: Maximum number of retry attempts
        delay: Initial delay between retries in seconds
        backoff: Backoff multiplier
        jitter: Add random jitter to delay
        exceptions: Tuple of exceptions to catch and retry
        circuit_breaker: Optional circuit breaker instance
        
    Returns:
        Decorated function with retry logic
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_exception = None
            current_delay = delay
            
            for attempt in range(max_retries + 1):
                try:
                    # Check circuit breaker
                    if circuit_breaker and not circuit_breaker.can_execute():
                        raise RetryError(
                            f"Circuit breaker is open for {func.__name__}"
                        )
                    
                    # Execute function
                    result = func(*args, **kwargs)
                    
                    # Record success
                    if circuit_breaker:
                        circuit_breaker.record_success()
                    
                    return result
                    
                except exceptions as e:
                    last_exception = e
                    
                    # Record failure
                    if circuit_breaker:
                        circuit_breaker.record_failure()
                    
                    # Check if we should retry
                    if attempt < max_retries:
                        # Calculate delay with jitter
                        calculated_delay = current_delay
                        if jitter:
                            calculated_delay += random.uniform(0, current_delay * 0.5)
                        
                        logger.warning(
                            f"Attempt {attempt + 1}/{max_retries + 1} failed for {func.__name__}: "
                            f"{str(e)}. Retrying in {calculated_delay:.2f}s..."
                        )
                        
                        time.sleep(calculated_delay)
                        current_delay *= backoff
                    else:
                        logger.error(
                            f"All {max_retries + 1} attempts failed for {func.__name__}"
                        )
            
            # All retries exhausted
            raise RetryError(
                f"All {max_retries + 1} attempts failed for {func.__name__}",
                last_exception=last_exception
            )
        
        return wrapper
    return decorator


class FailoverHandler:
    """Handle failover between multiple API endpoints"""
    
    def __init__(self, endpoints: List[Dict[str, Any]]):
        """
        Initialize failover handler
        
        Args:
            endpoints: List of endpoint configurations in priority order
                Each config should contain:
                - name: Endpoint name
                - url: Base URL
                - priority: Priority (lower = higher priority)
                - config: Endpoint-specific configuration
        """
        self.endpoints = sorted(
            endpoints,
            key=lambda x: x.get('priority', 999)
        )
        self._circuit_breakers: Dict[str, CircuitBreaker] = {}
        
        # Create circuit breaker for each endpoint
        for endpoint in self.endpoints:
            name = endpoint.get('name', endpoint.get('url'))
            self._circuit_breakers[name] = CircuitBreaker()
    
    def get_available_endpoint(self) -> Optional[Dict[str, Any]]:
        """
        Get first available endpoint based on circuit breaker state
        
        Returns:
            Endpoint configuration or None if all unavailable
        """
        for endpoint in self.endpoints:
            name = endpoint.get('name', endpoint.get('url'))
            cb = self._circuit_breakers[name]
            
            if cb.can_execute():
                return endpoint
        
        return None
    
    def execute_with_failover(
        self,
        func: Callable,
        *args,
        **kwargs
    ) -> Any:
        """
        Execute function with automatic failover
        
        Args:
            func: Function to execute (should accept endpoint config as first arg)
            *args: Function arguments
            **kwargs: Function keyword arguments
            
        Returns:
            Function result
            
        Raises:
            RetryError: If all endpoints fail
        """
        last_exception = None
        
        for endpoint in self.endpoints:
            name = endpoint.get('name', endpoint.get('url'))
            cb = self._circuit_breakers[name]
            
            if not cb.can_execute():
                logger.warning(f"Skipping endpoint {name}: circuit breaker open")
                continue
            
            try:
                logger.info(f"Attempting to execute with endpoint: {name}")
                result = func(endpoint, *args, **kwargs)
                cb.record_success()
                return result
                
            except Exception as e:
                last_exception = e
                cb.record_failure()
                logger.error(f"Endpoint {name} failed: {str(e)}")
                continue
        
        # All endpoints failed
        raise RetryError(
            f"All {len(self.endpoints)} endpoints failed",
            last_exception=last_exception
        )
