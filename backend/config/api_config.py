# OP_CMS API Configuration
"""Configuration management for external API adapters"""

import os
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
import yaml


@dataclass
class APIConfig:
    """API configuration data class"""
    name: str
    base_url: str
    api_key: Optional[str] = None
    api_secret: Optional[str] = None
    timeout: int = 30
    retry_count: int = 3
    retry_delay: float = 1.0
    verify_ssl: bool = True
    headers: Dict[str, str] = field(default_factory=dict)
    auth_type: str = 'api_key'  # api_key, oauth2, basic, none
    rate_limit: Optional[int] = None  # requests per minute
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'name': self.name,
            'base_url': self.base_url,
            'api_key': self.api_key,
            'api_secret': self.api_secret,
            'timeout': self.timeout,
            'retry_count': self.retry_count,
            'retry_delay': self.retry_delay,
            'verify_ssl': self.verify_ssl,
            'headers': self.headers,
            'auth_type': self.auth_type,
            'rate_limit': self.rate_limit
        }


class APIConfigManager:
    """Manager for API configurations"""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize API configuration manager
        
        Args:
            config_path: Path to API configuration file (optional)
        """
        self.config_path = config_path or os.environ.get('API_CONFIG_PATH')
        self._configs: Dict[str, APIConfig] = {}
        
        if self.config_path and os.path.exists(self.config_path):
            self._load_configs()
    
    def _load_configs(self):
        """Load API configurations from file"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                configs_data = yaml.safe_load(f)
            
            if configs_data and 'apis' in configs_data:
                for api_name, api_config in configs_data['apis'].items():
                    self._configs[api_name] = APIConfig(
                        name=api_config.get('name', api_name),
                        base_url=api_config.get('base_url', ''),
                        api_key=api_config.get('api_key'),
                        api_secret=api_config.get('api_secret'),
                        timeout=api_config.get('timeout', 30),
                        retry_count=api_config.get('retry_count', 3),
                        retry_delay=api_config.get('retry_delay', 1.0),
                        verify_ssl=api_config.get('verify_ssl', True),
                        headers=api_config.get('headers', {}),
                        auth_type=api_config.get('auth_type', 'api_key'),
                        rate_limit=api_config.get('rate_limit')
                    )
        except Exception as e:
            raise RuntimeError(f"Failed to load API configs: {str(e)}")
    
    def get_config(self, api_name: str) -> Optional[APIConfig]:
        """
        Get API configuration by name
        
        Args:
            api_name: Name of the API configuration
            
        Returns:
            APIConfig or None if not found
        """
        return self._configs.get(api_name)
    
    def get_all_configs(self) -> Dict[str, APIConfig]:
        """Get all API configurations"""
        return self._configs.copy()
    
    def add_config(self, config: APIConfig):
        """
        Add or update API configuration
        
        Args:
            config: API configuration to add
        """
        self._configs[config.name] = config
    
    def remove_config(self, api_name: str):
        """
        Remove API configuration
        
        Args:
            api_name: Name of the API to remove
        """
        if api_name in self._configs:
            del self._configs[api_name]
    
    def save_configs(self, path: Optional[str] = None):
        """
        Save configurations to file
        
        Args:
            path: File path (uses default if None)
        """
        save_path = path or self.config_path
        if not save_path:
            raise ValueError("No configuration path specified")
        
        configs_data = {
            'apis': {
                name: config.to_dict()
                for name, config in self._configs.items()
            }
        }
        
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        with open(save_path, 'w', encoding='utf-8') as f:
            yaml.safe_dump(configs_data, f, default_flow_style=False, allow_unicode=True)


# Environment variable helpers
def get_api_config_from_env(api_name: str) -> APIConfig:
    """
    Create API configuration from environment variables
    
    Args:
        api_name: Name of the API (used as prefix for env vars)
        
    Returns:
        APIConfig object
        
    Environment Variables:
        {API_NAME}_BASE_URL
        {API_NAME}_API_KEY
        {API_NAME}_API_SECRET
        {API_NAME}_TIMEOUT
        {API_NAME}_RETRY_COUNT
    """
    prefix = api_name.upper().replace(' ', '_').replace('-', '_')
    
    return APIConfig(
        name=api_name,
        base_url=os.environ.get(f'{prefix}_BASE_URL', ''),
        api_key=os.environ.get(f'{prefix}_API_KEY'),
        api_secret=os.environ.get(f'{prefix}_API_SECRET'),
        timeout=int(os.environ.get(f'{prefix}_TIMEOUT', '30')),
        retry_count=int(os.environ.get(f'{prefix}_RETRY_COUNT', '3')),
        retry_delay=float(os.environ.get(f'{prefix}_RETRY_DELAY', '1.0')),
        verify_ssl=os.environ.get(f'{prefix}_VERIFY_SSL', 'true').lower() == 'true'
    )
