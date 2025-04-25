"""
Configuration module for the AWS DevOps Agent.
This module handles loading and managing configuration settings.
"""

import os
import logging
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

class AgentConfig:
    """
    Manages configuration settings for the AWS DevOps Agent.
    """
    
    def __init__(self, config_override: Optional[Dict[str, Any]] = None):
        """
        Initialize the configuration manager.
        
        Args:
            config_override: Optional dictionary to override default settings
        """
        # Load environment variables
        load_dotenv()
        
        # Default configuration
        self.config = {
            # AWS Configuration
            "aws_access_key_id": os.getenv("AWS_ACCESS_KEY_ID"),
            "aws_secret_access_key": os.getenv("AWS_SECRET_ACCESS_KEY"),
            "aws_default_region": os.getenv("AWS_DEFAULT_REGION", "us-east-1"),
            
            # LLM Configuration
            "openai_api_key": os.getenv("OPENAI_API_KEY"),
            "model": os.getenv("DEFAULT_MODEL", "gpt-4-turbo"),
            "temperature": float(os.getenv("TEMPERATURE", "0")),
            "verbose": os.getenv("VERBOSE", "True").lower() == "true",
            
            # Agent Configuration
            "confirmation_required": os.getenv("CONFIRMATION_REQUIRED", "True").lower() == "true",
            "max_retries": int(os.getenv("MAX_RETRIES", "3")),
            "timeout": int(os.getenv("TIMEOUT", "60")),
            
            # Paths
            "schema_dir": os.path.join(os.path.dirname(os.path.dirname(__file__)), "schemas"),
        }
        
        # Override with provided configuration
        if config_override:
            self.config.update(config_override)
        
        # Validate configuration
        self._validate_config()
        
        logger.info("Configuration loaded")
    
    def _validate_config(self):
        """
        Validate the configuration settings.
        """
        # Check for required AWS credentials in non-development mode
        if not os.getenv("DEVELOPMENT_MODE", "False").lower() == "true":
            if not self.config.get("aws_access_key_id") or not self.config.get("aws_secret_access_key"):
                logger.warning("AWS credentials not found. Some operations may fail.")
        
        # Check for OpenAI API key
        if not self.config.get("openai_api_key"):
            logger.warning("OpenAI API key not found. LLM operations will fail.")
    
    def get_config(self) -> Dict[str, Any]:
        """
        Get the complete configuration dictionary.
        
        Returns:
            Configuration dictionary
        """
        return self.config
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a specific configuration value.
        
        Args:
            key: Configuration key
            default: Default value if key is not found
            
        Returns:
            Configuration value
        """
        return self.config.get(key, default)
    
    def update(self, key: str, value: Any):
        """
        Update a specific configuration value.
        
        Args:
            key: Configuration key
            value: New value
        """
        self.config[key] = value
        logger.info(f"Configuration updated: {key}")
    
    def update_many(self, updates: Dict[str, Any]):
        """
        Update multiple configuration values.
        
        Args:
            updates: Dictionary of updates
        """
        self.config.update(updates)
        logger.info(f"Configuration updated with {len(updates)} values")
