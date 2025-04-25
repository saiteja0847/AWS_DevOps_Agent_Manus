"""
Service router module for the AWS DevOps Agent.
This module handles routing user prompts to the appropriate service agent.
"""

import logging
import re
from typing import Dict, Any, List, Optional

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

# Import service agents (will be implemented later)
try:
    from agents.ec2_agent import EC2Agent
    from agents.ec2_lifecycle_agent import EC2LifecycleAgent
    # Future imports for other services
    # from agents.s3_agent import S3Agent
    # from agents.rds_agent import RDSAgent
    # from agents.lambda_agent import LambdaAgent
except ImportError:
    logger.warning("Some service agents could not be imported. Limited functionality available.")

class ServiceRouter:
    """
    Routes user prompts to the appropriate service agent based on the content.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the service router.
        
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
        
        # Initialize service agents
        self.service_agents = {}
        self._initialize_service_agents()
        
        # Define service keywords for routing
        self.service_keywords = {
            "ec2": ["ec2", "instance", "server", "virtual machine", "vm", "compute"],
            "s3": ["s3", "storage", "bucket", "object", "file"],
            "rds": ["rds", "database", "db", "sql", "mysql", "postgresql", "aurora"],
            "lambda": ["lambda", "function", "serverless", "event-driven"],
            "vpc": ["vpc", "network", "subnet", "routing", "nat", "gateway"],
        }
        
        # Define operation types
        self.operation_types = {
            "create": ["create", "launch", "start", "deploy", "provision", "set up", "setup"],
            "read": ["describe", "get", "list", "show", "display", "view"],
            "update": ["update", "modify", "change", "edit", "alter"],
            "delete": ["delete", "remove", "terminate", "destroy", "tear down"],
            "lifecycle": ["start", "stop", "reboot", "restart", "terminate", "hibernate", "resume"]
        }
        
        logger.info("Service router initialized")
    
    def _initialize_service_agents(self):
        """
        Initialize all available service agents.
        """
        try:
            # Initialize EC2 agents
            self.service_agents["ec2"] = EC2Agent(self.config)
            self.service_agents["ec2_lifecycle"] = EC2LifecycleAgent(self.config)
            
            # Future service agent initializations
            # self.service_agents["s3"] = S3Agent(self.config)
            # self.service_agents["rds"] = RDSAgent(self.config)
            # self.service_agents["lambda"] = LambdaAgent(self.config)
            
            logger.info(f"Initialized service agents: {', '.join(self.service_agents.keys())}")
        except Exception as e:
            logger.error(f"Error initializing service agents: {str(e)}")
    
    def _identify_services(self, prompt: str) -> List[str]:
        """
        Identify AWS services mentioned in the prompt.
        
        Args:
            prompt: User's natural language prompt
            
        Returns:
            List of identified service names
        """
        prompt_lower = prompt.lower()
        identified_services = []
        
        for service, keywords in self.service_keywords.items():
            for keyword in keywords:
                if keyword in prompt_lower:
                    identified_services.append(service)
                    break
        
        return list(set(identified_services))  # Remove duplicates
    
    def _identify_operation_type(self, prompt: str) -> str:
        """
        Identify the operation type from the prompt.
        
        Args:
            prompt: User's natural language prompt
            
        Returns:
            Operation type (create, read, update, delete, lifecycle)
        """
        prompt_lower = prompt.lower()
        
        for op_type, keywords in self.operation_types.items():
            for keyword in keywords:
                if keyword in prompt_lower:
                    return op_type
        
        # Default to "read" if no operation type is identified
        return "read"
    
    def _is_lifecycle_operation(self, prompt: str) -> bool:
        """
        Determine if the prompt is requesting a lifecycle operation.
        
        Args:
            prompt: User's natural language prompt
            
        Returns:
            True if the prompt is requesting a lifecycle operation, False otherwise
        """
        prompt_lower = prompt.lower()
        lifecycle_keywords = self.operation_types["lifecycle"]
        
        # Check for lifecycle keywords
        for keyword in lifecycle_keywords:
            if keyword in prompt_lower:
                # Make sure it's not in a context like "create a server that starts automatically"
                # by checking for proximity to EC2/instance keywords
                keyword_index = prompt_lower.find(keyword)
                
                # Look for instance identifiers nearby
                instance_pattern = r'i-[a-z0-9]{8,17}'
                instance_match = re.search(instance_pattern, prompt_lower)
                
                if instance_match:
                    return True
                
                # Check for proximity to "instance" or "server" keywords
                instance_keywords = ["instance", "server", "machine"]
                for instance_keyword in instance_keywords:
                    instance_index = prompt_lower.find(instance_keyword)
                    if instance_index != -1 and abs(keyword_index - instance_index) < 20:
                        return True
        
        return False
    
    def _use_llm_for_routing(self, prompt: str) -> Dict[str, Any]:
        """
        Use LLM to determine the appropriate service and operation.
        
        Args:
            prompt: User's natural language prompt
            
        Returns:
            Dictionary containing service, operation_type, and confidence
        """
        system_prompt = """
        You are an AWS DevOps routing assistant. Your job is to analyze a user's prompt and determine:
        1. Which AWS service they want to interact with (EC2, S3, RDS, Lambda, VPC, etc.)
        2. What operation they want to perform (create, read, update, delete, lifecycle)
        3. If it's an EC2 lifecycle operation (start, stop, reboot, terminate)
        
        Respond with a JSON object containing:
        {
            "service": "service_name",
            "operation_type": "operation_type",
            "is_lifecycle": true/false,
            "confidence": 0.0-1.0
        }
        """
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=prompt)
        ]
        
        try:
            response = self.llm.invoke(messages)
            
            # Extract JSON from response
            import json
            import re
            
            # Look for JSON pattern in the response
            json_match = re.search(r'```json\n(.*?)\n```', response.content, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                json_str = response.content
            
            # Clean up the string and parse JSON
            json_str = re.sub(r'```.*?```', '', json_str, flags=re.DOTALL).strip()
            result = json.loads(json_str)
            
            return result
        except Exception as e:
            logger.error(f"Error using LLM for routing: {str(e)}")
            # Fall back to rule-based routing
            services = self._identify_services(prompt)
            operation_type = self._identify_operation_type(prompt)
            is_lifecycle = self._is_lifecycle_operation(prompt)
            
            return {
                "service": services[0] if services else "unknown",
                "operation_type": operation_type,
                "is_lifecycle": is_lifecycle,
                "confidence": 0.5  # Medium confidence for rule-based routing
            }
    
    def route_prompt(self, prompt: str) -> Dict[str, Any]:
        """
        Route a user prompt to the appropriate service agent.
        
        Args:
            prompt: User's natural language prompt
            
        Returns:
            Dictionary containing the response from the service agent
        """
        logger.info(f"Routing prompt: {prompt}")
        
        # Use LLM to determine routing
        routing_info = self._use_llm_for_routing(prompt)
        
        service = routing_info.get("service", "unknown")
        operation_type = routing_info.get("operation_type", "read")
        is_lifecycle = routing_info.get("is_lifecycle", False)
        confidence = routing_info.get("confidence", 0.0)
        
        logger.info(f"Routing determined: service={service}, operation={operation_type}, lifecycle={is_lifecycle}, confidence={confidence}")
        
        # Handle EC2 lifecycle operations specially
        if service == "ec2" and is_lifecycle and "ec2_lifecycle" in self.service_agents:
            agent = self.service_agents["ec2_lifecycle"]
        elif service in self.service_agents:
            agent = self.service_agents[service]
        else:
            return {
                "status": "error",
                "message": f"No agent available for service: {service}",
                "routing_info": routing_info
            }
        
        # Process the prompt with the selected agent
        try:
            result = agent.process_prompt(prompt, operation_type)
            result["routing_info"] = routing_info
            return result
        except Exception as e:
            logger.error(f"Error processing prompt with {service} agent: {str(e)}")
            return {
                "status": "error",
                "message": f"Error processing prompt with {service} agent: {str(e)}",
                "routing_info": routing_info,
                "error": str(e)
            }
    
    def execute_operation(self, operation_details: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute an operation using the appropriate service agent.
        
        Args:
            operation_details: Dictionary containing operation details
            
        Returns:
            Dictionary containing the execution results
        """
        service = operation_details.get("service", "unknown")
        
        if service not in self.service_agents:
            return {
                "status": "error",
                "message": f"No agent available for service: {service}"
            }
        
        agent = self.service_agents[service]
        
        try:
            result = agent.execute_operation(operation_details)
            return result
        except Exception as e:
            logger.error(f"Error executing operation with {service} agent: {str(e)}")
            return {
                "status": "error",
                "message": f"Error executing operation with {service} agent: {str(e)}",
                "error": str(e)
            }
