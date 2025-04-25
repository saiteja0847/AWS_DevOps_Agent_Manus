"""
EC2 parser module for the AWS DevOps Agent.
This module extracts EC2 creation parameters from user prompts.
"""

import logging
import json
import re
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
except ImportError:
    logger.error("Required modules not found. Please ensure all dependencies are installed.")

class EC2Parser:
    """
    Extracts EC2 creation parameters from user prompts.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the EC2 parser.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        
        # Initialize prompt understanding system
        self.prompt_understanding = PromptUnderstanding(config)
        
        # Common EC2 instance types
        self.instance_types = [
            "t2.micro", "t2.small", "t2.medium", "t2.large",
            "t3.micro", "t3.small", "t3.medium", "t3.large",
            "m5.large", "m5.xlarge", "m5.2xlarge",
            "c5.large", "c5.xlarge", "c5.2xlarge",
            "r5.large", "r5.xlarge", "r5.2xlarge"
        ]
        
        # Common AMI descriptions
        self.ami_descriptions = {
            "amazon linux": "ami-0c55b159cbfafe1f0",  # Example AMI ID
            "ubuntu": "ami-0dba2cb6798deb6d8",        # Example AMI ID
            "windows": "ami-0ab193018fec6aea5",       # Example AMI ID
            "red hat": "ami-0520e698dd500b1d1"        # Example AMI ID
        }
        
        logger.info("EC2 parser initialized")
    
    def parse_prompt(self, prompt: str, operation_type: str = "create") -> Dict[str, Any]:
        """
        Parse a user prompt to extract EC2 creation parameters.
        
        Args:
            prompt: User's natural language prompt
            operation_type: Operation type (default: "create")
            
        Returns:
            Dictionary containing the extracted parameters
        """
        logger.info(f"Parsing EC2 {operation_type} prompt: {prompt}")
        
        try:
            # Use prompt understanding system to extract parameters
            extraction_result = self.prompt_understanding.extract_parameters(prompt, "ec2", operation_type)
            
            if extraction_result.get("status") != "success":
                return extraction_result
            
            parameters = extraction_result.get("parameters", {})
            
            # Apply default values and transformations
            parameters = self._apply_defaults_and_transformations(parameters, operation_type)
            
            # Resolve AMI ID if needed
            if "ImageDescription" in parameters and not parameters.get("ImageId"):
                parameters = self._resolve_ami_id(parameters)
            
            return {
                "status": "success",
                "message": "Parameters extracted successfully",
                "parameters": parameters
            }
        except Exception as e:
            logger.error(f"Error parsing EC2 prompt: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to parse EC2 prompt: {str(e)}",
                "error": str(e)
            }
    
    def _apply_defaults_and_transformations(self, parameters: Dict[str, Any], operation_type: str) -> Dict[str, Any]:
        """
        Apply default values and transformations to extracted parameters.
        
        Args:
            parameters: Extracted parameters
            operation_type: Operation type
            
        Returns:
            Parameters with defaults and transformations applied
        """
        if operation_type == "create":
            # Apply default values
            if "MinCount" not in parameters:
                parameters["MinCount"] = 1
            
            if "MaxCount" not in parameters:
                parameters["MaxCount"] = 1
            
            # Transform instance type if needed
            if "InstanceTypeDescription" in parameters and not parameters.get("InstanceType"):
                parameters = self._resolve_instance_type(parameters)
            
            # Ensure Tags are in the correct format
            if "Tags" in parameters and isinstance(parameters["Tags"], dict):
                parameters["Tags"] = [{"Key": k, "Value": v} for k, v in parameters["Tags"].items()]
        
        return parameters
    
    def _resolve_instance_type(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Resolve instance type from description.
        
        Args:
            parameters: Extracted parameters
            
        Returns:
            Parameters with resolved instance type
        """
        description = parameters.get("InstanceTypeDescription", "").lower()
        
        # Try to match description to instance type
        if "small" in description or "micro" in description:
            if "compute" in description or "cpu" in description:
                parameters["InstanceType"] = "t3.micro"
            elif "memory" in description or "ram" in description:
                parameters["InstanceType"] = "r5.large"
            else:
                parameters["InstanceType"] = "t3.micro"
        elif "medium" in description:
            if "compute" in description or "cpu" in description:
                parameters["InstanceType"] = "c5.large"
            elif "memory" in description or "ram" in description:
                parameters["InstanceType"] = "r5.large"
            else:
                parameters["InstanceType"] = "t3.medium"
        elif "large" in description:
            if "compute" in description or "cpu" in description:
                parameters["InstanceType"] = "c5.xlarge"
            elif "memory" in description or "ram" in description:
                parameters["InstanceType"] = "r5.xlarge"
            else:
                parameters["InstanceType"] = "m5.large"
        else:
            # Default to t3.micro if no match
            parameters["InstanceType"] = "t3.micro"
        
        return parameters
    
    def _resolve_ami_id(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Resolve AMI ID from description.
        
        Args:
            parameters: Extracted parameters
            
        Returns:
            Parameters with resolved AMI ID
        """
        description = parameters.get("ImageDescription", "").lower()
        
        # Try to match description to AMI
        for ami_desc, ami_id in self.ami_descriptions.items():
            if ami_desc in description:
                parameters["ImageId"] = ami_id
                break
        
        # If no match, default to Amazon Linux
        if not parameters.get("ImageId"):
            parameters["ImageId"] = self.ami_descriptions["amazon linux"]
        
        return parameters
