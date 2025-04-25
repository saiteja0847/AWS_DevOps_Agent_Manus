"""
EC2 tools module for the AWS DevOps Agent.
This module contains functions for creating EC2 instances.
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

def create_ec2_instance(ec2_client, parameters: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create an EC2 instance using the provided parameters.
    
    Args:
        ec2_client: Boto3 EC2 client
        parameters: Dictionary of EC2 instance parameters
        
    Returns:
        Dictionary containing the created instance details
    """
    logger.info(f"Creating EC2 instance with parameters: {parameters}")
    
    try:
        # Extract required parameters
        instance_type = parameters.get("InstanceType")
        image_id = parameters.get("ImageId")
        min_count = parameters.get("MinCount", 1)
        max_count = parameters.get("MaxCount", 1)
        
        # Extract optional parameters
        key_name = parameters.get("KeyName")
        security_group_ids = parameters.get("SecurityGroupIds")
        subnet_id = parameters.get("SubnetId")
        user_data = parameters.get("UserData")
        tags = parameters.get("Tags")
        
        # Build the request parameters
        request_params = {
            "ImageId": image_id,
            "InstanceType": instance_type,
            "MinCount": min_count,
            "MaxCount": max_count
        }
        
        # Add optional parameters if provided
        if key_name:
            request_params["KeyName"] = key_name
        
        if security_group_ids:
            request_params["SecurityGroupIds"] = security_group_ids if isinstance(security_group_ids, list) else [security_group_ids]
        
        if subnet_id:
            request_params["SubnetId"] = subnet_id
        
        if user_data:
            request_params["UserData"] = user_data
        
        # Create the instance
        response = ec2_client.run_instances(**request_params)
        
        # Extract instance details
        instances = response.get("Instances", [])
        instance_ids = [instance.get("InstanceId") for instance in instances]
        
        # Add tags if provided
        if tags and instance_ids:
            ec2_client.create_tags(
                Resources=instance_ids,
                Tags=tags if isinstance(tags, list) else [{"Key": "Name", "Value": tags}]
            )
        
        return {
            "InstanceIds": instance_ids,
            "Instances": instances,
            "RequestParameters": request_params
        }
    except Exception as e:
        logger.error(f"Error creating EC2 instance: {str(e)}")
        raise

def describe_ec2_instance(ec2_client, instance_id: str) -> Dict[str, Any]:
    """
    Describe an EC2 instance.
    
    Args:
        ec2_client: Boto3 EC2 client
        instance_id: ID of the instance to describe
        
    Returns:
        Dictionary containing the instance details
    """
    logger.info(f"Describing EC2 instance: {instance_id}")
    
    try:
        response = ec2_client.describe_instances(InstanceIds=[instance_id])
        
        # Extract instance details
        reservations = response.get("Reservations", [])
        if not reservations:
            return {"Error": "Instance not found"}
        
        instances = reservations[0].get("Instances", [])
        if not instances:
            return {"Error": "Instance not found"}
        
        return instances[0]
    except Exception as e:
        logger.error(f"Error describing EC2 instance: {str(e)}")
        raise

def find_ami(ec2_client, description: str) -> str:
    """
    Find an AMI based on description.
    
    Args:
        ec2_client: Boto3 EC2 client
        description: Description of the desired AMI
        
    Returns:
        AMI ID
    """
    logger.info(f"Finding AMI based on description: {description}")
    
    try:
        # Define filters based on description
        filters = []
        
        description_lower = description.lower()
        
        if "amazon" in description_lower and "linux" in description_lower:
            filters = [
                {"Name": "name", "Values": ["amzn2-ami-hvm-*-x86_64-gp2"]},
                {"Name": "owner-alias", "Values": ["amazon"]}
            ]
        elif "ubuntu" in description_lower:
            filters = [
                {"Name": "name", "Values": ["ubuntu/images/hvm-ssd/ubuntu-focal-20.04-amd64-server-*"]},
                {"Name": "owner-id", "Values": ["099720109477"]}  # Canonical's owner ID
            ]
        elif "windows" in description_lower:
            filters = [
                {"Name": "name", "Values": ["Windows_Server-2019-English-Full-Base-*"]},
                {"Name": "owner-alias", "Values": ["amazon"]}
            ]
        elif "red hat" in description_lower or "rhel" in description_lower:
            filters = [
                {"Name": "name", "Values": ["RHEL-8*-x86_64-*"]},
                {"Name": "owner-id", "Values": ["309956199498"]}  # Red Hat's owner ID
            ]
        else:
            # Default to Amazon Linux
            filters = [
                {"Name": "name", "Values": ["amzn2-ami-hvm-*-x86_64-gp2"]},
                {"Name": "owner-alias", "Values": ["amazon"]}
            ]
        
        # Find the latest AMI
        response = ec2_client.describe_images(
            Filters=filters,
            Owners=["amazon", "099720109477", "309956199498"],  # Amazon, Canonical, Red Hat
        )
        
        # Sort by creation date (newest first)
        images = sorted(response.get("Images", []), key=lambda x: x.get("CreationDate", ""), reverse=True)
        
        if not images:
            # Default to a known Amazon Linux AMI
            return "ami-0c55b159cbfafe1f0"
        
        return images[0].get("ImageId")
    except Exception as e:
        logger.error(f"Error finding AMI: {str(e)}")
        # Default to a known Amazon Linux AMI
        return "ami-0c55b159cbfafe1f0"
