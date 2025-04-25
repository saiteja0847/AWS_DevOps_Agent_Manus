"""
Configuration validator module for the AWS DevOps Agent.
This module validates configurations before execution.
"""

import logging
import json
from typing import Dict, Any, List, Optional, Tuple

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Import LLM components
from langchain_community.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage

class ConfigurationValidator:
    """
    Validates configurations before execution.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the configuration validator.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        
        # Initialize LLM
        self.llm = ChatOpenAI(
            model_name=config.get("model", "gpt-4-turbo"),
            temperature=config.get("temperature", 0),
            verbose=config.get("verbose", False)
        )
        
        logger.info("Configuration validator initialized")
    
    def validate_configuration(self, service: str, operation_type: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate a configuration before execution.
        
        Args:
            service: AWS service (e.g., "ec2", "s3")
            operation_type: Operation type (e.g., "create", "read", "update", "delete")
            parameters: Configuration parameters
            
        Returns:
            Dictionary containing validation results
        """
        logger.info(f"Validating {service} {operation_type} configuration")
        
        # Perform basic validation
        basic_validation = self._basic_validation(service, operation_type, parameters)
        
        # If basic validation fails, return the errors
        if not basic_validation["valid"]:
            return {
                "status": "invalid",
                "message": "Configuration validation failed",
                "errors": basic_validation["errors"],
                "warnings": basic_validation["warnings"]
            }
        
        # Perform security validation
        security_validation = self._security_validation(service, operation_type, parameters)
        
        # Perform cost estimation
        cost_estimation = self._estimate_cost(service, operation_type, parameters)
        
        # Perform optimization suggestions
        optimization_suggestions = self._suggest_optimizations(service, operation_type, parameters)
        
        # Combine all validation results
        return {
            "status": "valid" if security_validation["valid"] else "warning",
            "message": "Configuration validation completed",
            "errors": [],
            "warnings": security_validation["warnings"],
            "cost_estimation": cost_estimation,
            "optimization_suggestions": optimization_suggestions
        }
    
    def _basic_validation(self, service: str, operation_type: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform basic validation of configuration parameters.
        
        Args:
            service: AWS service
            operation_type: Operation type
            parameters: Configuration parameters
            
        Returns:
            Dictionary containing validation results
        """
        errors = []
        warnings = []
        
        # Check for required parameters based on service and operation
        if service == "ec2" and operation_type == "create":
            required_params = ["InstanceType"]
            
            # Either ImageId or a way to find an image is required
            if not parameters.get("ImageId") and not parameters.get("ImageDescription"):
                errors.append("Either ImageId or ImageDescription is required")
            
            for param in required_params:
                if param not in parameters:
                    errors.append(f"Required parameter '{param}' is missing")
        
        elif service == "ec2" and operation_type == "lifecycle":
            if not parameters.get("Action"):
                errors.append("Required parameter 'Action' is missing")
            
            if not parameters.get("InstanceId") and not parameters.get("InstanceDescription"):
                errors.append("Either InstanceId or InstanceDescription is required")
        
        elif service == "s3" and operation_type == "create":
            if not parameters.get("BucketName"):
                errors.append("Required parameter 'BucketName' is missing")
        
        # Check parameter types and values
        if service == "ec2" and operation_type == "create":
            if "InstanceType" in parameters and not isinstance(parameters["InstanceType"], str):
                errors.append("InstanceType must be a string")
            
            if "MinCount" in parameters and not isinstance(parameters["MinCount"], int):
                errors.append("MinCount must be an integer")
            
            if "MaxCount" in parameters and not isinstance(parameters["MaxCount"], int):
                errors.append("MaxCount must be an integer")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }
    
    def _security_validation(self, service: str, operation_type: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate security aspects of the configuration.
        
        Args:
            service: AWS service
            operation_type: Operation type
            parameters: Configuration parameters
            
        Returns:
            Dictionary containing validation results
        """
        warnings = []
        
        # Check for security issues based on service and operation
        if service == "ec2" and operation_type == "create":
            # Check for security groups
            if not parameters.get("SecurityGroupIds") and not parameters.get("SecurityGroups"):
                warnings.append("No security groups specified. Default security group will be used, which may not be secure.")
            
            # Check for public IP assignment
            if parameters.get("AssociatePublicIpAddress") == True:
                warnings.append("Instance will be assigned a public IP address. Ensure this is intended.")
            
            # Check for SSH key
            if not parameters.get("KeyName"):
                warnings.append("No SSH key specified. You may not be able to access the instance via SSH.")
        
        elif service == "s3" and operation_type == "create":
            # Check for public access
            if parameters.get("ACL") == "public-read" or parameters.get("ACL") == "public-read-write":
                warnings.append("Bucket will be publicly accessible. Ensure this is intended.")
            
            # Check for encryption
            if not parameters.get("BucketEncryption"):
                warnings.append("Bucket encryption not specified. Consider enabling encryption for sensitive data.")
        
        return {
            "valid": True,  # Security issues are warnings, not errors
            "warnings": warnings
        }
    
    def _estimate_cost(self, service: str, operation_type: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Estimate the cost of the configuration.
        
        Args:
            service: AWS service
            operation_type: Operation type
            parameters: Configuration parameters
            
        Returns:
            Dictionary containing cost estimation
        """
        # Use LLM to estimate cost
        system_prompt = """
        You are an AWS cost estimation expert. Your task is to estimate the cost of an AWS resource based on its configuration.
        
        Provide a cost estimation with the following information:
        1. Estimated monthly cost (low, medium, high)
        2. Cost breakdown by component
        3. Cost-saving recommendations
        
        Format your response as a JSON object with the following structure:
        {
            "estimated_monthly_cost": "low/medium/high",
            "estimated_cost_range": {
                "low": "$X",
                "high": "$Y"
            },
            "cost_breakdown": [
                {
                    "component": "component_name",
                    "description": "cost_description",
                    "estimated_cost": "$Z"
                }
            ],
            "cost_saving_recommendations": [
                "recommendation1",
                "recommendation2"
            ]
        }
        """
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"""
            Service: {service}
            Operation: {operation_type}
            Configuration: {json.dumps(parameters, indent=2)}
            """)
        ]
        
        try:
            response = self.llm.invoke(messages)
            
            # Extract JSON from response
            import re
            
            # Look for JSON pattern in the response
            json_match = re.search(r'```json\n(.*?)\n```', response.content, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                json_str = response.content
            
            # Clean up the string and parse JSON
            json_str = re.sub(r'```.*?```', '', json_str, flags=re.DOTALL).strip()
            cost_estimation = json.loads(json_str)
            
            return cost_estimation
        except Exception as e:
            logger.error(f"Error estimating cost: {str(e)}")
            return {
                "estimated_monthly_cost": "unknown",
                "estimated_cost_range": {
                    "low": "unknown",
                    "high": "unknown"
                },
                "cost_breakdown": [],
                "cost_saving_recommendations": [
                    "Unable to estimate cost due to an error"
                ]
            }
    
    def _suggest_optimizations(self, service: str, operation_type: str, parameters: Dict[str, Any]) -> List[str]:
        """
        Suggest optimizations for the configuration.
        
        Args:
            service: AWS service
            operation_type: Operation type
            parameters: Configuration parameters
            
        Returns:
            List of optimization suggestions
        """
        suggestions = []
        
        # Suggest optimizations based on service and operation
        if service == "ec2" and operation_type == "create":
            # Instance type optimization
            if parameters.get("InstanceType", "").startswith("t2."):
                suggestions.append("Consider using T3 instances instead of T2 for better price-performance ratio.")
            
            # EBS optimization
            if not parameters.get("EbsOptimized") and not parameters.get("InstanceType", "").startswith(("t2.", "t3.")):
                suggestions.append("Consider enabling EBS optimization for better storage performance.")
            
            # Spot instances
            if not parameters.get("InstanceMarketOptions"):
                suggestions.append("Consider using Spot instances for non-critical workloads to reduce costs.")
        
        elif service == "s3" and operation_type == "create":
            # Lifecycle policies
            if not parameters.get("LifecycleConfiguration"):
                suggestions.append("Consider adding lifecycle policies to automatically transition objects to cheaper storage classes or delete old objects.")
            
            # Intelligent tiering
            suggestions.append("Consider using S3 Intelligent-Tiering storage class for objects with changing or unknown access patterns.")
        
        return suggestions
