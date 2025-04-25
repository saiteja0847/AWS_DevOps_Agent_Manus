# AWS DevOps Agent Documentation

## Overview

The AWS DevOps Agent is an AI-powered tool designed to create and manage AWS infrastructure through natural language prompts. It leverages large language models to understand user requirements, translate them into AWS API calls, and execute operations with proper validation and confirmation steps.

This documentation covers the implementation details, architecture, usage instructions, and future enhancement possibilities for the AWS DevOps Agent.

## Table of Contents

1. [Architecture](#architecture)
2. [Components](#components)
3. [Installation](#installation)
4. [Configuration](#configuration)
5. [Usage](#usage)
6. [Development](#development)
7. [Testing](#testing)
8. [Future Enhancements](#future-enhancements)

## Architecture

The AWS DevOps Agent follows a modular architecture designed for extensibility and maintainability. The core components include:

- **Main Controller**: Central entry point that routes user prompts to appropriate service agents
- **Service Router**: Determines which AWS service agent should handle the request
- **Prompt Understanding System**: Extracts parameters, configurations, and intentions from user prompts
- **Service Agents**: Service-specific modules that handle operations for particular AWS services
- **Configuration Validator**: Validates configurations before execution
- **Execution Engine**: Executes AWS operations with proper error handling

The architecture diagram can be found in the `architecture_diagram.png` file.

## Components

### Main Controller (`main.py`)

The main entry point for the AWS DevOps Agent. It handles user prompts and routes them to the appropriate service agent.

### Service Router (`routers/service_router.py`)

Routes user prompts to the appropriate service agent based on the content. It uses NLP to identify service mentions and operation types.

### Prompt Understanding System (`utils/prompt_understanding.py`)

Extracts parameters, configurations, and intentions from user prompts. It can also translate business requirements to technical specifications.

### Configuration Validator (`utils/configuration_validator.py`)

Validates configurations before execution, checking for security best practices, parameter combinations, and estimating costs.

### EC2 Agent (`agents/ec2_agent.py`)

Handles EC2 instance creation operations. It uses the prompt understanding system to extract parameters and the configuration validator to validate them.

### EC2 Lifecycle Agent (`agents/ec2_lifecycle_agent.py`)

Handles EC2 instance lifecycle operations (start, stop, reboot, terminate). It uses the prompt understanding system to extract parameters and the configuration validator to validate them.

### EC2 Parser (`parsers/ec2_parser.py`)

Extracts EC2 creation parameters from user prompts. It applies default values and transformations to the extracted parameters.

### EC2 Lifecycle Parser (`parsers/ec2_lifecycle_parser.py`)

Extracts EC2 lifecycle action parameters from user prompts. It validates and normalizes the action parameter.

### EC2 Tools (`tools/ec2_tools.py`)

Contains functions for creating EC2 instances. It handles the actual AWS API calls.

### EC2 Lifecycle Tools (`tools/ec2_lifecycle.py`)

Contains functions for EC2 instance lifecycle operations (start, stop, reboot, terminate). It handles the actual AWS API calls.

## Installation

### Prerequisites

- Python 3.8 or higher
- AWS account with appropriate permissions
- OpenAI API key

### Steps

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/aws-devops-agent.git
   cd aws-devops-agent
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Create a `.env` file with your AWS and OpenAI credentials:
   ```
   AWS_ACCESS_KEY_ID=your_access_key_id
   AWS_SECRET_ACCESS_KEY=your_secret_access_key
   AWS_DEFAULT_REGION=us-east-1
   OPENAI_API_KEY=your_openai_api_key
   ```

## Configuration

The AWS DevOps Agent can be configured through environment variables or by passing a configuration dictionary to the `DevOpsAgent` constructor.

### Environment Variables

- `AWS_ACCESS_KEY_ID`: Your AWS access key ID
- `AWS_SECRET_ACCESS_KEY`: Your AWS secret access key
- `AWS_DEFAULT_REGION`: The AWS region to use (default: `us-east-1`)
- `OPENAI_API_KEY`: Your OpenAI API key
- `DEFAULT_MODEL`: The OpenAI model to use (default: `gpt-4-turbo`)
- `TEMPERATURE`: The temperature parameter for the OpenAI model (default: `0`)
- `VERBOSE`: Whether to enable verbose logging (default: `True`)
- `CONFIRMATION_REQUIRED`: Whether to require confirmation before executing operations (default: `True`)
- `MAX_RETRIES`: The maximum number of retries for AWS operations (default: `3`)
- `TIMEOUT`: The timeout for AWS operations in seconds (default: `60`)
- `DEVELOPMENT_MODE`: Whether to enable development mode (default: `False`)

### Configuration Dictionary

You can also pass a configuration dictionary to the `DevOpsAgent` constructor:

```python
from main import DevOpsAgent

config = {
    "aws_access_key_id": "your_access_key_id",
    "aws_secret_access_key": "your_secret_access_key",
    "aws_default_region": "us-east-1",
    "openai_api_key": "your_openai_api_key",
    "model": "gpt-4-turbo",
    "temperature": 0,
    "verbose": True,
    "confirmation_required": True,
    "max_retries": 3,
    "timeout": 60,
    "development_mode": False
}

agent = DevOpsAgent(config)
```

## Usage

### Basic Usage

```python
from main import DevOpsAgent

# Create the DevOps Agent
agent = DevOpsAgent()

# Process a prompt
result = agent.process_prompt("Create an EC2 instance with t2.micro instance type and Amazon Linux AMI")

# Check if confirmation is required
if result.get("status") == "success" and result.get("requires_confirmation"):
    # Display operation details
    print("Operation details:")
    for key, value in result.get("parameters", {}).items():
        print(f"  {key}: {value}")
    
    # Ask for confirmation
    confirmation = input("Do you want to proceed? (yes/no): ")
    
    if confirmation.lower() in ["yes", "y"]:
        # Execute the operation
        execution_result = agent.execute_operation(result, confirmed=True)
        print("Execution result:", execution_result)
```

### Command Line Interface

You can also use the AWS DevOps Agent from the command line:

```
python main.py "Create an EC2 instance with t2.micro instance type and Amazon Linux AMI"
```

Or in interactive mode:

```
python main.py
```

### Example Prompts

#### EC2 Instance Creation

- "Create an EC2 instance with t2.micro instance type and Amazon Linux AMI"
- "Launch a new EC2 server with 2 CPUs and 4GB of RAM running Ubuntu"
- "Set up a Windows server with 8GB RAM in us-west-2 region"

#### EC2 Lifecycle Operations

- "Start the EC2 instance with ID i-1234567890abcdef0"
- "Stop my development server named 'dev-server'"
- "Reboot the database instance in us-east-1"
- "Terminate all test instances with the tag 'environment=test'"

## Development

### Adding a New AWS Service

To add support for a new AWS service, you need to create the following components:

1. **Service Agent**: Create a new agent class in the `agents` directory
2. **Service Parser**: Create a new parser class in the `parsers` directory
3. **Service Tools**: Create a new tools module in the `tools` directory
4. **Service Schema**: Create a new schema file in the `schemas` directory
5. **Update Service Router**: Add the new service to the `service_keywords` dictionary in `service_router.py`

### Example: Adding S3 Support

1. Create `agents/s3_agent.py`:
   ```python
   class S3Agent:
       def __init__(self, config):
           self.config = config
           # Initialize components
           
       def process_prompt(self, prompt, operation_type):
           # Process the prompt
           
       def execute_operation(self, operation_details):
           # Execute the operation
   ```

2. Create `parsers/s3_parser.py`:
   ```python
   class S3Parser:
       def __init__(self, config):
           self.config = config
           # Initialize components
           
       def parse_prompt(self, prompt, operation_type):
           # Parse the prompt
   ```

3. Create `tools/s3_tools.py`:
   ```python
   def create_s3_bucket(s3_client, parameters):
       # Create an S3 bucket
       
   def upload_to_s3(s3_client, parameters):
       # Upload a file to S3
   ```

4. Create `schemas/s3_create_schema.json`:
   ```json
   {
     "type": "object",
     "properties": {
       "BucketName": {
         "type": "string",
         "description": "The name of the bucket to create."
       },
       "ACL": {
         "type": "string",
         "description": "The canned ACL to apply to the bucket."
       }
     },
     "required": ["BucketName"],
     "additionalProperties": false
   }
   ```

5. Update `service_router.py`:
   ```python
   self.service_keywords = {
       "ec2": ["ec2", "instance", "server", "virtual machine", "vm", "compute"],
       "s3": ["s3", "storage", "bucket", "object", "file"],
       # ...
   }
   ```

## Testing

The AWS DevOps Agent includes a comprehensive test suite in the `tests` directory. To run the tests:

```
python -m tests.test_agent
```

The tests cover all components of the agent, including:

- Configuration
- Prompt understanding
- EC2 parser
- EC2 lifecycle parser
- Configuration validator
- EC2 agent
- EC2 lifecycle agent
- Service router
- Integration tests

## Future Enhancements

The AWS DevOps Agent can be enhanced in several ways:

1. **Additional AWS Services**: Add support for more AWS services like S3, RDS, Lambda, VPC, etc.
2. **Infrastructure as Code**: Generate CloudFormation or Terraform templates from configurations
3. **Cost Optimization**: Enhance cost estimation and optimization suggestions
4. **Security Enhancements**: Add more security checks and best practices
5. **Multi-Service Operations**: Support operations that span multiple AWS services
6. **Business Requirements Translation**: Enhance the ability to translate business requirements to technical specifications
7. **Visualization**: Add visualization capabilities for infrastructure diagrams
8. **Monitoring Integration**: Integrate with monitoring tools like CloudWatch
9. **CI/CD Integration**: Integrate with CI/CD pipelines
10. **Web Interface**: Create a web interface for the agent

## Conclusion

The AWS DevOps Agent provides a powerful way to create and manage AWS infrastructure through natural language prompts. Its modular architecture allows for easy extension to support additional AWS services and features. By leveraging large language models, it can understand complex requirements and translate them into AWS API calls with proper validation and confirmation steps.
