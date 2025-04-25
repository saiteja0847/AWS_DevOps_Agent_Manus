"""
Main entry point for the AWS DevOps Agent.
This module handles user prompts and routes them to the appropriate service agent.
"""

import os
import sys
import logging
from dotenv import load_dotenv
from typing import Dict, Any, List, Optional

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Import service routers
try:
    from routers.service_router import ServiceRouter
    from utils.config import AgentConfig
except ImportError:
    logger.error("Required modules not found. Please ensure all dependencies are installed.")
    sys.exit(1)

class DevOpsAgent:
    """
    Main DevOps Agent class that handles user prompts and routes them to the appropriate service agent.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the DevOps Agent.
        
        Args:
            config: Optional configuration dictionary to override default settings
        """
        # Load configuration
        self.config = AgentConfig(config).get_config()
        
        # Initialize service router
        self.service_router = ServiceRouter(self.config)
        
        logger.info("AWS DevOps Agent initialized")
    
    def process_prompt(self, prompt: str) -> Dict[str, Any]:
        """
        Process a user prompt and route it to the appropriate service agent.
        
        Args:
            prompt: User's natural language prompt
            
        Returns:
            Dictionary containing the response and any relevant metadata
        """
        logger.info(f"Processing prompt: {prompt}")
        
        try:
            # Route the prompt to the appropriate service agent
            response = self.service_router.route_prompt(prompt)
            return response
        except Exception as e:
            logger.error(f"Error processing prompt: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to process prompt: {str(e)}",
                "error": str(e)
            }
    
    def confirm_operation(self, operation_details: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ask for user confirmation before executing an operation.
        
        Args:
            operation_details: Dictionary containing operation details
            
        Returns:
            Dictionary containing the confirmation status and operation details
        """
        # In a real implementation, this would interact with the user
        # For now, we'll just return the operation details with a confirmation flag
        return {
            "status": "confirmation_required",
            "operation": operation_details,
            "message": "Please confirm this operation before proceeding."
        }
    
    def execute_operation(self, operation_details: Dict[str, Any], confirmed: bool = False) -> Dict[str, Any]:
        """
        Execute an AWS operation.
        
        Args:
            operation_details: Dictionary containing operation details
            confirmed: Whether the operation has been confirmed by the user
            
        Returns:
            Dictionary containing the execution results
        """
        if not confirmed:
            return self.confirm_operation(operation_details)
        
        logger.info(f"Executing operation: {operation_details.get('operation_type', 'unknown')}")
        
        try:
            # Route the execution to the appropriate service agent
            result = self.service_router.execute_operation(operation_details)
            return result
        except Exception as e:
            logger.error(f"Error executing operation: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to execute operation: {str(e)}",
                "error": str(e)
            }

def main():
    """
    Main entry point for the AWS DevOps Agent.
    """
    # Create the DevOps Agent
    agent = DevOpsAgent()
    
    # Example usage
    if len(sys.argv) > 1:
        # If prompt is provided as command line argument
        prompt = " ".join(sys.argv[1:])
        result = agent.process_prompt(prompt)
        print(result)
    else:
        # Interactive mode
        print("AWS DevOps Agent")
        print("Type 'exit' to quit")
        
        while True:
            try:
                prompt = input("\nEnter your prompt: ")
                
                if prompt.lower() in ["exit", "quit"]:
                    break
                
                result = agent.process_prompt(prompt)
                
                if result.get("status") == "confirmation_required":
                    print("\nOperation details:")
                    for key, value in result.items():
                        print(f"  {key}: {value}")
                    
                    confirmation = input("\nDo you want to proceed? (yes/no): ")
                    
                    if confirmation.lower() in ["yes", "y"]:
                        result = agent.execute_operation(result, confirmed=True)
                
                print("\nResult:")
                print(result)
                
            except KeyboardInterrupt:
                print("\nExiting...")
                break
            except Exception as e:
                print(f"\nError: {str(e)}")

if __name__ == "__main__":
    main()
