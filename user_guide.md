# AWS DevOps Agent - User Guide

## Introduction

The AWS DevOps Agent is an AI-powered assistant that allows you to create and manage AWS infrastructure using natural language prompts. This guide provides instructions on how to use the agent effectively.

## Getting Started

### Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/aws-devops-agent.git
   cd aws-devops-agent
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Set up your AWS and OpenAI credentials in a `.env` file:
   ```
   AWS_ACCESS_KEY_ID=your_access_key_id
   AWS_SECRET_ACCESS_KEY=your_secret_access_key
   AWS_DEFAULT_REGION=us-east-1
   OPENAI_API_KEY=your_openai_api_key
   ```

### Running the Agent

You can run the agent in interactive mode:

```
python main.py
```

Or you can provide a prompt directly:

```
python main.py "Create an EC2 instance with t2.micro instance type and Amazon Linux AMI"
```

## Using the Agent

### EC2 Instance Creation

You can create EC2 instances by describing what you want in natural language. The agent will extract the necessary parameters and confirm with you before creating the instance.

Examples:

- "Create an EC2 instance with t2.micro instance type and Amazon Linux AMI"
- "Launch a new EC2 server with 2 CPUs and 4GB of RAM running Ubuntu"
- "Set up a Windows server with 8GB RAM in us-west-2 region"

The agent will extract parameters like:
- Instance type
- AMI (Amazon Machine Image)
- Region
- Security groups
- Key pairs
- Tags

### EC2 Lifecycle Management

You can manage the lifecycle of your EC2 instances with simple commands:

Examples:

- "Start the EC2 instance with ID i-1234567890abcdef0"
- "Stop my development server named 'dev-server'"
- "Reboot the database instance in us-east-1"
- "Terminate all test instances with the tag 'environment=test'"

### Best Practices

1. **Be specific**: The more details you provide, the better the agent can understand your requirements.

2. **Review before confirming**: Always review the extracted parameters before confirming an operation.

3. **Use instance IDs when possible**: For lifecycle operations, using the instance ID is more reliable than using names or descriptions.

4. **Include region information**: If you're working with resources in multiple regions, specify the region in your prompt.

## Troubleshooting

### Common Issues

1. **Missing parameters**: If the agent doesn't extract all required parameters, it will ask you for the missing information.

2. **Authentication errors**: Ensure your AWS credentials are correctly set in the `.env` file.

3. **Permission errors**: Make sure your AWS user has the necessary permissions to perform the requested operations.

4. **Rate limiting**: If you encounter rate limiting issues, try reducing the frequency of your requests.

### Getting Help

If you encounter any issues not covered in this guide, please:

1. Check the logs for error messages
2. Refer to the full documentation in `documentation.md`
3. Open an issue on the GitHub repository

## Conclusion

The AWS DevOps Agent simplifies AWS infrastructure management by allowing you to use natural language instead of remembering complex API calls or console navigation. As you use the agent more, you'll discover how to phrase your prompts effectively to get the exact results you need.
