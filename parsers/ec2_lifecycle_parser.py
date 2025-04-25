"""
EC2 lifecycle parser module for the AWS DevOps Agent.
This module extracts EC2 lifecycle action parameters from user prompts.
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

class EC2LifecycleParser:
    """
    Extracts EC2 lifecycle action parameters from user prompts.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the EC2 lifecycle parser.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        
        # Initialize prompt understanding system
        self.prompt_understanding = PromptUnderstanding(config)
        
        # Define lifecycle actions
        self.lifecycle_actions = ["start", "stop", "reboot", "terminate"]
        
        logger.info("EC2 lifecycle parser initialized")
    
    def parse_prompt(self, prompt: str) -> Dict[str, Any]:
        """
        Parse a user prompt to extract EC2 lifecycle parameters.
        
        Args:
            prompt: User's natural language prompt
            
        Returns:
            Dictionary containing the extracted parameters
        """
        logger.info(f"Parsing EC2 lifecycle prompt: {prompt}")
        
        try:
            # Use prompt understanding system to extract parameters
            extraction_result = self.prompt_understanding.extract_parameters(prompt, "ec2", "lifecycle")
            
            if extraction_result.get("status") != "success":
                return extraction_result
            
            parameters = extraction_result.get("parameters", {})
            
            # Ensure action is valid
            parameters = self._validate_action(parameters)
            
            # Extract instance ID if present
            parameters = self._extract_instance_id(prompt, parameters)
            
            return {
                "status": "success",
                "message": "Parameters extracted successfully",
                "parameters": parameters
            }
        except Exception as e:
            logger.error(f"Error parsing EC2 lifecycle prompt: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to parse EC2 lifecycle prompt: {str(e)}",
                "error": str(e)
            }
    
    def _validate_action(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and normalize the action parameter.
        
        Args:
            parameters: Extracted parameters
            
        Returns:
            Parameters with validated action
        """
        action = parameters.get("Action", "").lower()
        
        # Check if action is valid
        if action not in self.lifecycle_actions:
            # Try to map similar terms
            if action in ["launch", "run"]:
                action = "start"
            elif action in ["shutdown", "halt", "pause"]:
                action = "stop"
            elif action in ["restart"]:
                action = "reboot"
            elif action in ["delete", "remove", "destroy"]:
                action = "terminate"
            else:
                # Default to "stop" if action is not recognized
                action = "stop"
        
        parameters["Action"] = action
        return parameters
    
    def _extract_instance_id(self, prompt: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract instance ID from prompt if not already in parameters.
        
        Args:
            prompt: User's natural language prompt
            parameters: Extracted parameters
            
        Returns:
            Parameters with extracted instance ID
        """
        if "InstanceId" not in parameters:
            # Look for instance ID pattern in prompt
            instance_pattern = r'i-[a-z0-9]{8,17}'
            instance_match = re.search(instance_pattern, prompt)
            
            if instance_match:
                parameters["InstanceId"] = instance_match.group(0)
        
        return parameters
