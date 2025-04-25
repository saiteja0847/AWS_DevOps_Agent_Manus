"""
EC2 lifecycle agent module for the AWS DevOps Agent.
This module handles EC2 instance lifecycle operations (start, stop, reboot, terminate).
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
    from parsers.ec2_lifecycle_parser import EC2LifecycleParser
    from tools.ec2_lifecycle import start_instance, stop_instance, reboot_instance, terminate_instance
except ImportError:
    logger.error("Required modules not found. Please ensure all dependencies are installed.")

class EC2LifecycleAgent:
    """
    Handles EC2 instance lifecycle operations (start, stop, reboot, terminate).
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the EC2 lifecycle agent.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        
        # Initialize components
        self.prompt_understanding = PromptUnderstanding(config)
        self.configuration_validator = ConfigurationValidator(config)
        self.parser = EC2LifecycleParser(config)
        
        # Initialize AWS client
        self.ec2_client = None
        self._initialize_aws_client()
        
        logger.info("EC2 lifecycle agent initialized")
    
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
    
    def process_prompt(self, prompt: str, operation_type: str = "lifecycle") -> Dict[str, Any]:
        """
        Process a user prompt for EC2 lifecycle operations.
        
        Args:
            prompt: User's natural language prompt
            operation_type: Operation type (default: "lifecycle")
            
        Returns:
            Dictionary containing the response
        """
        logger.info(f"Processing EC2 lifecycle prompt: {prompt}")
        
        try:
            # Parse the prompt to extract parameters
            parsed_result = self.parser.parse_prompt(prompt)
            
            if parsed_result.get("status") != "success":
                return parsed_result
            
            parameters = parsed_result.get("parameters", {})
            
            # Validate the configuration
            validation_result = self.configuration_validator.validate_configuration("ec2", "lifecycle", parameters)
            
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
                "message": "EC2 lifecycle operation parsed and validated",
                "service": "ec2",
                "operation_type": "lifecycle",
                "parameters": parameters,
                "validation": validation_result,
                "requires_confirmation": True
            }
        except Exception as e:
            logger.error(f"Error processing EC2 lifecycle prompt: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to process EC2 lifecycle prompt: {str(e)}",
                "error": str(e)
            }
    
    def execute_operation(self, operation_details: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute an EC2 lifecycle operation.
        
        Args:
            operation_details: Dictionary containing operation details
            
        Returns:
            Dictionary containing the execution results
        """
        parameters = operation_details.get("parameters", {})
        action = parameters.get("Action", "").lower()
        instance_id = parameters.get("InstanceId")
        
        logger.info(f"Executing EC2 lifecycle operation: {action} on instance {instance_id}")
        
        try:
            if not instance_id:
                return {
                    "status": "error",
                    "message": "Instance ID is required for lifecycle operations"
                }
            
            if action == "start":
                result = start_instance(self.ec2_client, instance_id)
            elif action == "stop":
                result = stop_instance(self.ec2_client, instance_id)
            elif action == "reboot":
                result = reboot_instance(self.ec2_client, instance_id)
            elif action == "terminate":
                result = terminate_instance(self.ec2_client, instance_id)
            else:
                return {
                    "status": "error",
                    "message": f"Unsupported action: {action}"
                }
            
            return {
                "status": "success",
                "message": f"EC2 instance {action} operation completed successfully",
                "result": result
            }
        except Exception as e:
            logger.error(f"Error executing EC2 lifecycle operation: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to execute EC2 lifecycle operation: {str(e)}",
                "error": str(e)
            }
