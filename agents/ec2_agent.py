"""
EC2 agent module for the AWS DevOps Agent.
This module handles EC2 instance creation operations.
"""

import logging
import json
import boto3
from typing import Dict, Any, List, Optional

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Import utility modules
try:
    from utils.prompt_understanding import PromptUnderstanding
    from utils.configuration_validator import ConfigurationValidator
    from parsers.ec2_parser import EC2Parser
    from tools.ec2_tools import create_ec2_instance
except ImportError:
    logger.error("Required modules not found. Please ensure all dependencies are installed.")

class EC2Agent:
    """
    Handles EC2 instance creation operations.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the EC2 agent.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        
        # Initialize components
        self.prompt_understanding = PromptUnderstanding(config)
        self.configuration_validator = ConfigurationValidator(config)
        self.parser = EC2Parser(config)
        
        # Initialize AWS client
        self.ec2_client = None
        self._initialize_aws_client()
        
        logger.info("EC2 agent initialized")
    
    def _initialize_aws_client(self):
        """
        Initialize the AWS EC2 client.
        """
        try:
            # Initialize boto3 client
            self.ec2_client = boto3.client(
                'ec2',
                aws_access_key_id=self.config.get("aws_access_key_id"),
                aws_secret_access_key=self.config.get("aws_secret_access_key"),
                region_name=self.config.get("aws_default_region")
            )
            logger.info(f"EC2 client initialized for region {self.config.get('aws_default_region')}")
        except Exception as e:
            logger.error(f"Error initializing EC2 client: {str(e)}")
    
    def process_prompt(self, prompt: str, operation_type: str = "create") -> Dict[str, Any]:
        """
        Process a user prompt for EC2 operations.
        
        Args:
            prompt: User's natural language prompt
            operation_type: Operation type (default: "create")
            
        Returns:
            Dictionary containing the response
        """
        logger.info(f"Processing EC2 {operation_type} prompt: {prompt}")
        
        try:
            # Parse the prompt to extract parameters
            parsed_result = self.parser.parse_prompt(prompt, operation_type)
            
            if parsed_result.get("status") != "success":
                return parsed_result
            
            parameters = parsed_result.get("parameters", {})
            
            # Validate the configuration
            validation_result = self.configuration_validator.validate_configuration("ec2", operation_type, parameters)
            
            if validation_result.get("status") == "invalid":
                return {
                    "status": "error",
                    "message": "Invalid configuration",
                    "errors": validation_result.get("errors", []),
                    "warnings": validation_result.get("warnings", [])
                }
            
            # Return the parsed parameters and validation results
            return {
                "status": "success",
                "message": "EC2 configuration parsed and validated",
                "service": "ec2",
                "operation_type": operation_type,
                "parameters": parameters,
                "validation": validation_result,
                "requires_confirmation": True
            }
        except Exception as e:
            logger.error(f"Error processing EC2 prompt: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to process EC2 prompt: {str(e)}",
                "error": str(e)
            }
    
    def execute_operation(self, operation_details: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute an EC2 operation.
        
        Args:
            operation_details: Dictionary containing operation details
            
        Returns:
            Dictionary containing the execution results
        """
        operation_type = operation_details.get("operation_type", "create")
        parameters = operation_details.get("parameters", {})
        
        logger.info(f"Executing EC2 {operation_type} operation")
        
        try:
            if operation_type == "create":
                # Create EC2 instance
                result = create_ec2_instance(self.ec2_client, parameters)
                
                return {
                    "status": "success",
                    "message": "EC2 instance created successfully",
                    "result": result
                }
            else:
                return {
                    "status": "error",
                    "message": f"Unsupported operation type: {operation_type}"
                }
        except Exception as e:
            logger.error(f"Error executing EC2 operation: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to execute EC2 operation: {str(e)}",
                "error": str(e)
            }
