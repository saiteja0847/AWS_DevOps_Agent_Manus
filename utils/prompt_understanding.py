"""
Prompt understanding system for the AWS DevOps Agent.
This module handles extracting parameters and intentions from user prompts.
"""

import logging
import json
import re
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
from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate, SystemMessagePromptTemplate

class PromptUnderstanding:
    """
    Extracts parameters, configurations, and intentions from user prompts.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the prompt understanding system.
        
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
        
        logger.info("Prompt understanding system initialized")
    
    def extract_parameters(self, prompt: str, service: str, operation_type: str) -> Dict[str, Any]:
        """
        Extract service-specific parameters from a user prompt.
        
        Args:
            prompt: User's natural language prompt
            service: AWS service (e.g., "ec2", "s3")
            operation_type: Operation type (e.g., "create", "read", "update", "delete")
            
        Returns:
            Dictionary of extracted parameters
        """
        logger.info(f"Extracting parameters for {service} {operation_type} operation")
        
        # Load service-specific schema if available
        schema = self._load_schema(service, operation_type)
        
        # Create system prompt based on service and operation
        system_prompt = self._create_system_prompt(service, operation_type, schema)
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=prompt)
        ]
        
        try:
            response = self.llm.invoke(messages)
            
            # Extract JSON from response
            parameters = self._extract_json_from_response(response.content)
            
            # Validate parameters against schema if available
            if schema:
                parameters = self._validate_parameters(parameters, schema)
            
            return {
                "status": "success",
                "parameters": parameters,
                "service": service,
                "operation_type": operation_type
            }
        except Exception as e:
            logger.error(f"Error extracting parameters: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to extract parameters: {str(e)}",
                "error": str(e)
            }
    
    def translate_business_requirements(self, prompt: str) -> Dict[str, Any]:
        """
        Translate business requirements to technical specifications.
        
        Args:
            prompt: User's natural language prompt describing business requirements
            
        Returns:
            Dictionary containing translated technical specifications
        """
        logger.info("Translating business requirements to technical specifications")
        
        system_prompt = """
        You are an AWS solutions architect. Your task is to translate business requirements into specific AWS technical specifications.
        
        Given a set of business requirements, provide:
        1. The AWS services that should be used
        2. The specific configurations for each service
        3. Any connections or dependencies between services
        4. Estimated costs (low/medium/high)
        5. Security considerations
        
        Format your response as a JSON object with the following structure:
        {
            "services": [
                {
                    "name": "service_name",
                    "purpose": "why this service is needed",
                    "configuration": {
                        "param1": "value1",
                        "param2": "value2"
                    }
                }
            ],
            "connections": [
                {
                    "from": "service1",
                    "to": "service2",
                    "type": "connection_type"
                }
            ],
            "estimated_cost": "low/medium/high",
            "security_considerations": [
                "consideration1",
                "consideration2"
            ]
        }
        """
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=prompt)
        ]
        
        try:
            response = self.llm.invoke(messages)
            
            # Extract JSON from response
            specifications = self._extract_json_from_response(response.content)
            
            return {
                "status": "success",
                "specifications": specifications
            }
        except Exception as e:
            logger.error(f"Error translating business requirements: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to translate business requirements: {str(e)}",
                "error": str(e)
            }
    
    def identify_ambiguities(self, prompt: str, extracted_params: Dict[str, Any]) -> List[str]:
        """
        Identify ambiguities or missing information in the user prompt.
        
        Args:
            prompt: User's natural language prompt
            extracted_params: Dictionary of parameters already extracted
            
        Returns:
            List of questions to ask the user for clarification
        """
        logger.info("Identifying ambiguities in user prompt")
        
        system_prompt = """
        You are an AWS DevOps assistant. Your task is to identify ambiguities or missing information in a user's request.
        
        Given a user prompt and the parameters that have been extracted so far, identify any missing or ambiguous information that would be needed to fulfill the request.
        
        Format your response as a JSON array of questions to ask the user:
        [
            "question1",
            "question2"
        ]
        
        Only include questions for truly ambiguous or missing information. Do not ask questions if the information can be reasonably inferred or if it's not essential.
        """
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"""
            User prompt: {prompt}
            
            Extracted parameters: {json.dumps(extracted_params, indent=2)}
            """)
        ]
        
        try:
            response = self.llm.invoke(messages)
            
            # Extract JSON from response
            questions = self._extract_json_from_response(response.content)
            
            if not isinstance(questions, list):
                questions = [questions]
            
            return questions
        except Exception as e:
            logger.error(f"Error identifying ambiguities: {str(e)}")
            return [f"Could not identify ambiguities: {str(e)}"]
    
    def _load_schema(self, service: str, operation_type: str) -> Optional[Dict[str, Any]]:
        """
        Load the JSON schema for a specific service and operation.
        
        Args:
            service: AWS service (e.g., "ec2", "s3")
            operation_type: Operation type (e.g., "create", "read", "update", "delete")
            
        Returns:
            JSON schema dictionary or None if not found
        """
        import os
        
        schema_dir = self.config.get("schema_dir")
        if not schema_dir:
            logger.warning("Schema directory not configured")
            return None
        
        schema_file = os.path.join(schema_dir, f"{service}_{operation_type}_schema.json")
        
        if not os.path.exists(schema_file):
            logger.warning(f"Schema file not found: {schema_file}")
            return None
        
        try:
            with open(schema_file, 'r') as f:
                schema = json.load(f)
            return schema
        except Exception as e:
            logger.error(f"Error loading schema: {str(e)}")
            return None
    
    def _create_system_prompt(self, service: str, operation_type: str, schema: Optional[Dict[str, Any]]) -> str:
        """
        Create a system prompt for parameter extraction based on service and operation.
        
        Args:
            service: AWS service (e.g., "ec2", "s3")
            operation_type: Operation type (e.g., "create", "read", "update", "delete")
            schema: JSON schema for the service and operation
            
        Returns:
            System prompt string
        """
        # Base prompt
        prompt = f"""
        You are an AWS DevOps assistant specialized in extracting parameters for {service.upper()} {operation_type} operations.
        
        Given a user's request, extract all relevant parameters for a {service.upper()} {operation_type} operation.
        
        Format your response as a JSON object with the extracted parameters.
        """
        
        # Add schema information if available
        if schema:
            prompt += f"""
            
            The parameters should conform to the following schema:
            {json.dumps(schema, indent=2)}
            """
        
        # Add service-specific instructions
        if service == "ec2":
            if operation_type == "create":
                prompt += """
                
                For EC2 instance creation, be sure to extract:
                - InstanceType (e.g., t2.micro, m5.large)
                - ImageId (AMI ID) or a description of the desired image
                - KeyName if mentioned
                - SecurityGroupIds or security group descriptions
                - SubnetId or VPC information
                - Any tags to be applied
                - User data scripts if mentioned
                """
            elif operation_type == "lifecycle":
                prompt += """
                
                For EC2 lifecycle operations, be sure to extract:
                - The specific action (start, stop, reboot, terminate)
                - InstanceId or a description of the target instance
                - Force flag for terminate operations if mentioned
                """
        elif service == "s3":
            if operation_type == "create":
                prompt += """
                
                For S3 bucket creation, be sure to extract:
                - BucketName
                - Region
                - ACL settings if mentioned
                - Versioning configuration
                - Encryption settings
                """
        
        return prompt
    
    def _extract_json_from_response(self, response: str) -> Dict[str, Any]:
        """
        Extract JSON from LLM response text.
        
        Args:
            response: LLM response text
            
        Returns:
            Extracted JSON as a dictionary
        """
        # Look for JSON pattern in the response
        json_match = re.search(r'```json\n(.*?)\n```', response, re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
        else:
            # Try to find JSON without markdown formatting
            json_match = re.search(r'({.*}|\[.*\])', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
            else:
                json_str = response
        
        # Clean up the string
        json_str = re.sub(r'```.*?```', '', json_str, flags=re.DOTALL).strip()
        
        try:
            # Parse JSON
            result = json.loads(json_str)
            return result
        except json.JSONDecodeError:
            logger.error(f"Failed to parse JSON from response: {response}")
            # Attempt to fix common JSON issues
            fixed_json_str = self._fix_json_string(json_str)
            return json.loads(fixed_json_str)
    
    def _fix_json_string(self, json_str: str) -> str:
        """
        Attempt to fix common JSON formatting issues.
        
        Args:
            json_str: Potentially malformed JSON string
            
        Returns:
            Fixed JSON string
        """
        # Replace single quotes with double quotes
        json_str = json_str.replace("'", '"')
        
        # Add quotes to unquoted keys
        json_str = re.sub(r'([{,])\s*([a-zA-Z0-9_]+)\s*:', r'\1"\2":', json_str)
        
        # Fix trailing commas
        json_str = re.sub(r',\s*([}\]])', r'\1', json_str)
        
        return json_str
    
    def _validate_parameters(self, parameters: Dict[str, Any], schema: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate extracted parameters against a JSON schema.
        
        Args:
            parameters: Extracted parameters
            schema: JSON schema
            
        Returns:
            Validated parameters
        """
        try:
            from jsonschema import validate, ValidationError
            
            validate(instance=parameters, schema=schema)
            return parameters
        except ValidationError as e:
            logger.warning(f"Parameter validation failed: {str(e)}")
            # Return parameters anyway, but log the validation error
            return parameters
        except Exception as e:
            logger.error(f"Error during parameter validation: {str(e)}")
            return parameters
