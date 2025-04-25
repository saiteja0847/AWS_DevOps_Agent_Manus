"""
Test script for the AWS DevOps Agent.
This script tests the functionality of the implemented components.
"""

import os
import sys
import logging
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
load_dotenv()

# Import agent components
try:
    from utils.config import AgentConfig
    from routers.service_router import ServiceRouter
    from utils.prompt_understanding import PromptUnderstanding
    from utils.configuration_validator import ConfigurationValidator
    from agents.ec2_agent import EC2Agent
    from agents.ec2_lifecycle_agent import EC2LifecycleAgent
    from parsers.ec2_parser import EC2Parser
    from parsers.ec2_lifecycle_parser import EC2LifecycleParser
except ImportError as e:
    logger.error(f"Failed to import required modules: {e}")
    sys.exit(1)

def test_config():
    """Test the configuration module."""
    logger.info("Testing configuration module...")
    
    try:
        # Create configuration with default values
        config = AgentConfig().get_config()
        
        # Check if required keys exist
        assert "aws_default_region" in config, "Missing aws_default_region in config"
        assert "model" in config, "Missing model in config"
        assert "schema_dir" in config, "Missing schema_dir in config"
        
        logger.info("Configuration module test passed")
        return True
    except AssertionError as e:
        logger.error(f"Configuration module test failed: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error in configuration module test: {e}")
        return False

def test_prompt_understanding():
    """Test the prompt understanding module."""
    logger.info("Testing prompt understanding module...")
    
    try:
        # Create configuration
        config = AgentConfig().get_config()
        
        # Set development mode to avoid requiring actual API keys
        config["development_mode"] = True
        
        # Create prompt understanding system
        prompt_understanding = PromptUnderstanding(config)
        
        # Test with a mock response (since we don't have actual API keys)
        prompt_understanding._extract_json_from_response = lambda x: {"InstanceType": "t2.micro", "ImageId": "ami-12345678"}
        
        # Extract parameters
        result = prompt_understanding.extract_parameters(
            "Create an EC2 instance with t2.micro instance type and Amazon Linux AMI",
            "ec2",
            "create"
        )
        
        # Check if result has expected structure
        assert result["status"] == "success", "Extraction failed"
        assert "parameters" in result, "Missing parameters in result"
        assert result["parameters"]["InstanceType"] == "t2.micro", "Incorrect InstanceType"
        
        logger.info("Prompt understanding module test passed")
        return True
    except AssertionError as e:
        logger.error(f"Prompt understanding module test failed: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error in prompt understanding module test: {e}")
        return False

def test_ec2_parser():
    """Test the EC2 parser module."""
    logger.info("Testing EC2 parser module...")
    
    try:
        # Create configuration
        config = AgentConfig().get_config()
        
        # Set development mode to avoid requiring actual API keys
        config["development_mode"] = True
        
        # Create EC2 parser
        ec2_parser = EC2Parser(config)
        
        # Mock the prompt understanding extract_parameters method
        ec2_parser.prompt_understanding.extract_parameters = lambda prompt, service, operation_type: {
            "status": "success",
            "parameters": {
                "InstanceType": "t2.micro",
                "ImageDescription": "Amazon Linux"
            }
        }
        
        # Parse prompt
        result = ec2_parser.parse_prompt(
            "Create an EC2 instance with t2.micro instance type and Amazon Linux AMI",
            "create"
        )
        
        # Check if result has expected structure
        assert result["status"] == "success", "Parsing failed"
        assert "parameters" in result, "Missing parameters in result"
        assert result["parameters"]["InstanceType"] == "t2.micro", "Incorrect InstanceType"
        assert "ImageId" in result["parameters"], "Missing ImageId in parameters"
        
        logger.info("EC2 parser module test passed")
        return True
    except AssertionError as e:
        logger.error(f"EC2 parser module test failed: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error in EC2 parser module test: {e}")
        return False

def test_ec2_lifecycle_parser():
    """Test the EC2 lifecycle parser module."""
    logger.info("Testing EC2 lifecycle parser module...")
    
    try:
        # Create configuration
        config = AgentConfig().get_config()
        
        # Set development mode to avoid requiring actual API keys
        config["development_mode"] = True
        
        # Create EC2 lifecycle parser
        ec2_lifecycle_parser = EC2LifecycleParser(config)
        
        # Mock the prompt understanding extract_parameters method
        ec2_lifecycle_parser.prompt_understanding.extract_parameters = lambda prompt, service, operation_type: {
            "status": "success",
            "parameters": {
                "Action": "stop",
                "InstanceId": "i-1234567890abcdef0"
            }
        }
        
        # Parse prompt
        result = ec2_lifecycle_parser.parse_prompt(
            "Stop the EC2 instance with ID i-1234567890abcdef0"
        )
        
        # Check if result has expected structure
        assert result["status"] == "success", "Parsing failed"
        assert "parameters" in result, "Missing parameters in result"
        assert result["parameters"]["Action"] == "stop", "Incorrect Action"
        assert result["parameters"]["InstanceId"] == "i-1234567890abcdef0", "Incorrect InstanceId"
        
        logger.info("EC2 lifecycle parser module test passed")
        return True
    except AssertionError as e:
        logger.error(f"EC2 lifecycle parser module test failed: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error in EC2 lifecycle parser module test: {e}")
        return False

def test_configuration_validator():
    """Test the configuration validator module."""
    logger.info("Testing configuration validator module...")
    
    try:
        # Create configuration
        config = AgentConfig().get_config()
        
        # Set development mode to avoid requiring actual API keys
        config["development_mode"] = True
        
        # Create configuration validator
        configuration_validator = ConfigurationValidator(config)
        
        # Mock the LLM response for cost estimation
        configuration_validator._estimate_cost = lambda service, operation_type, parameters: {
            "estimated_monthly_cost": "low",
            "estimated_cost_range": {
                "low": "$10",
                "high": "$20"
            },
            "cost_breakdown": [],
            "cost_saving_recommendations": []
        }
        
        # Validate configuration
        result = configuration_validator.validate_configuration(
            "ec2",
            "create",
            {
                "InstanceType": "t2.micro",
                "ImageId": "ami-12345678"
            }
        )
        
        # Check if result has expected structure
        assert result["status"] == "valid", "Validation failed"
        assert "cost_estimation" in result, "Missing cost_estimation in result"
        assert result["cost_estimation"]["estimated_monthly_cost"] == "low", "Incorrect cost estimation"
        
        logger.info("Configuration validator module test passed")
        return True
    except AssertionError as e:
        logger.error(f"Configuration validator module test failed: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error in configuration validator module test: {e}")
        return False

def test_ec2_agent():
    """Test the EC2 agent module."""
    logger.info("Testing EC2 agent module...")
    
    try:
        # Create configuration
        config = AgentConfig().get_config()
        
        # Set development mode to avoid requiring actual API keys
        config["development_mode"] = True
        
        # Create EC2 agent
        ec2_agent = EC2Agent(config)
        
        # Mock the parser parse_prompt method
        ec2_agent.parser.parse_prompt = lambda prompt, operation_type: {
            "status": "success",
            "parameters": {
                "InstanceType": "t2.micro",
                "ImageId": "ami-12345678"
            }
        }
        
        # Mock the configuration validator validate_configuration method
        ec2_agent.configuration_validator.validate_configuration = lambda service, operation_type, parameters: {
            "status": "valid",
            "errors": [],
            "warnings": [],
            "cost_estimation": {
                "estimated_monthly_cost": "low"
            },
            "optimization_suggestions": []
        }
        
        # Process prompt
        result = ec2_agent.process_prompt(
            "Create an EC2 instance with t2.micro instance type and Amazon Linux AMI",
            "create"
        )
        
        # Check if result has expected structure
        assert result["status"] == "success", "Processing failed"
        assert "parameters" in result, "Missing parameters in result"
        assert result["parameters"]["InstanceType"] == "t2.micro", "Incorrect InstanceType"
        assert "validation" in result, "Missing validation in result"
        assert result["requires_confirmation"] == True, "Incorrect requires_confirmation"
        
        logger.info("EC2 agent module test passed")
        return True
    except AssertionError as e:
        logger.error(f"EC2 agent module test failed: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error in EC2 agent module test: {e}")
        return False

def test_ec2_lifecycle_agent():
    """Test the EC2 lifecycle agent module."""
    logger.info("Testing EC2 lifecycle agent module...")
    
    try:
        # Create configuration
        config = AgentConfig().get_config()
        
        # Set development mode to avoid requiring actual API keys
        config["development_mode"] = True
        
        # Create EC2 lifecycle agent
        ec2_lifecycle_agent = EC2LifecycleAgent(config)
        
        # Mock the parser parse_prompt method
        ec2_lifecycle_agent.parser.parse_prompt = lambda prompt: {
            "status": "success",
            "parameters": {
                "Action": "stop",
                "InstanceId": "i-1234567890abcdef0"
            }
        }
        
        # Mock the configuration validator validate_configuration method
        ec2_lifecycle_agent.configuration_validator.validate_configuration = lambda service, operation_type, parameters: {
            "status": "valid",
            "errors": [],
            "warnings": [],
            "cost_estimation": {
                "estimated_monthly_cost": "low"
            },
            "optimization_suggestions": []
        }
        
        # Process prompt
        result = ec2_lifecycle_agent.process_prompt(
            "Stop the EC2 instance with ID i-1234567890abcdef0"
        )
        
        # Check if result has expected structure
        assert result["status"] == "success", "Processing failed"
        assert "parameters" in result, "Missing parameters in result"
        assert result["parameters"]["Action"] == "stop", "Incorrect Action"
        assert result["parameters"]["InstanceId"] == "i-1234567890abcdef0", "Incorrect InstanceId"
        assert "validation" in result, "Missing validation in result"
        assert result["requires_confirmation"] == True, "Incorrect requires_confirmation"
        
        logger.info("EC2 lifecycle agent module test passed")
        return True
    except AssertionError as e:
        logger.error(f"EC2 lifecycle agent module test failed: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error in EC2 lifecycle agent module test: {e}")
        return False

def test_service_router():
    """Test the service router module."""
    logger.info("Testing service router module...")
    
    try:
        # Create configuration
        config = AgentConfig().get_config()
        
        # Set development mode to avoid requiring actual API keys
        config["development_mode"] = True
        
        # Create service router
        service_router = ServiceRouter(config)
        
        # Mock the LLM response for routing
        service_router._use_llm_for_routing = lambda prompt: {
            "service": "ec2",
            "operation_type": "create",
            "is_lifecycle": False,
            "confidence": 0.9
        }
        
        # Mock the EC2 agent
        class MockEC2Agent:
            def process_prompt(self, prompt, operation_type):
                return {
                    "status": "success",
                    "message": "EC2 configuration parsed and validated",
                    "service": "ec2",
                    "operation_type": operation_type,
                    "parameters": {
                        "InstanceType": "t2.micro",
                        "ImageId": "ami-12345678"
                    },
                    "validation": {
                        "status": "valid"
                    },
                    "requires_confirmation": True
                }
        
        # Replace the EC2 agent with the mock
        service_router.service_agents["ec2"] = MockEC2Agent()
        
        # Route prompt
        result = service_router.route_prompt(
            "Create an EC2 instance with t2.micro instance type and Amazon Linux AMI"
        )
        
        # Check if result has expected structure
        assert result["status"] == "success", "Routing failed"
        assert "parameters" in result, "Missing parameters in result"
        assert result["parameters"]["InstanceType"] == "t2.micro", "Incorrect InstanceType"
        assert "routing_info" in result, "Missing routing_info in result"
        assert result["routing_info"]["service"] == "ec2", "Incorrect service in routing_info"
        
        logger.info("Service router module test passed")
        return True
    except AssertionError as e:
        logger.error(f"Service router module test failed: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error in service router module test: {e}")
        return False

def test_integration():
    """Test the integration of all components."""
    logger.info("Testing integration of all components...")
    
    try:
        # Create configuration
        config = AgentConfig().get_config()
        
        # Set development mode to avoid requiring actual API keys
        config["development_mode"] = True
        
        # Import main DevOpsAgent class
        try:
            from main import DevOpsAgent
        except ImportError as e:
            logger.error(f"Failed to import DevOpsAgent: {e}")
            return False
        
        # Create DevOps Agent
        agent = DevOpsAgent(config)
        
        # Mock the service router route_prompt method
         # Mock the service router route_prompt method
        agent.service_router.route_prompt = lambda prompt: {
            "status": "confirmation_required",
            "message": "EC2 configuration parsed and validated",
            "service": "ec2",
            "operation_type": "create",
            "parameters": {
                "InstanceType": "t2.micro",
                "ImageId": "ami-12345678"
            },
            "validation": {
                "status": "valid"
            },
            "requires_confirmation": True,
            "routing_info": {
                "service": "ec2"
            }
        }

        # Test integration
        result = agent.process_prompt("Create an EC2 instance with t2.micro instance type")
        assert result["status"] == "confirmation_required", "Integration failed at confirmation step"

        logger.info("Integration test passed")
        return True
    except Exception as e:
        logger.error(f"Service router integration test failed: {e}")
        return False
    
if __name__ == "__main__":
    print("🔍 Running test suite...")
    tests = [
        ("Config", test_config),
        ("Prompt Understanding", test_prompt_understanding),
        ("EC2 Parser", test_ec2_parser),
        ("EC2 Lifecycle Parser", test_ec2_lifecycle_parser),
        ("Configuration Validator", test_configuration_validator),
        ("EC2 Agent", test_ec2_agent),
        ("EC2 Lifecycle Agent", test_ec2_lifecycle_agent),
        ("Service Router", test_service_router),
        ("Integration", test_integration),
    ]

    for name, test_func in tests:
        print(f"▶ Running {name} Test...")
        result = test_func()
        print(f"{name} Test: {'✅ Passed' if result else '❌ Failed'}")