"""
EC2 lifecycle tools module for the AWS DevOps Agent.
This module contains functions for EC2 instance lifecycle operations (start, stop, reboot, terminate).
"""

import logging
import boto3
from typing import Dict, Any, List, Optional

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

def start_instance(ec2_client, instance_id: str) -> Dict[str, Any]:
    """
    Start an EC2 instance.
    
    Args:
        ec2_client: Boto3 EC2 client
        instance_id: ID of the instance to start
        
    Returns:
        Dictionary containing the operation result
    """
    logger.info(f"Starting EC2 instance: {instance_id}")
    
    try:
        response = ec2_client.start_instances(InstanceIds=[instance_id])
        
        # Extract state change details
        state_changes = response.get("StartingInstances", [])
        
        return {
            "InstanceId": instance_id,
            "StateChanges": state_changes,
            "Action": "start"
        }
    except Exception as e:
        logger.error(f"Error starting EC2 instance: {str(e)}")
        raise

def stop_instance(ec2_client, instance_id: str, force: bool = False) -> Dict[str, Any]:
    """
    Stop an EC2 instance.
    
    Args:
        ec2_client: Boto3 EC2 client
        instance_id: ID of the instance to stop
        force: Whether to force stop the instance
        
    Returns:
        Dictionary containing the operation result
    """
    logger.info(f"Stopping EC2 instance: {instance_id} (force={force})")
    
    try:
        response = ec2_client.stop_instances(InstanceIds=[instance_id], Force=force)
        
        # Extract state change details
        state_changes = response.get("StoppingInstances", [])
        
        return {
            "InstanceId": instance_id,
            "StateChanges": state_changes,
            "Action": "stop",
            "Force": force
        }
    except Exception as e:
        logger.error(f"Error stopping EC2 instance: {str(e)}")
        raise

def reboot_instance(ec2_client, instance_id: str) -> Dict[str, Any]:
    """
    Reboot an EC2 instance.
    
    Args:
        ec2_client: Boto3 EC2 client
        instance_id: ID of the instance to reboot
        
    Returns:
        Dictionary containing the operation result
    """
    logger.info(f"Rebooting EC2 instance: {instance_id}")
    
    try:
        ec2_client.reboot_instances(InstanceIds=[instance_id])
        
        # Reboot doesn't return state changes, so we need to describe the instance
        instance_state = get_instance_state(ec2_client, instance_id)
        
        return {
            "InstanceId": instance_id,
            "CurrentState": instance_state,
            "Action": "reboot"
        }
    except Exception as e:
        logger.error(f"Error rebooting EC2 instance: {str(e)}")
        raise

def terminate_instance(ec2_client, instance_id: str) -> Dict[str, Any]:
    """
    Terminate an EC2 instance.
    
    Args:
        ec2_client: Boto3 EC2 client
        instance_id: ID of the instance to terminate
        
    Returns:
        Dictionary containing the operation result
    """
    logger.info(f"Terminating EC2 instance: {instance_id}")
    
    try:
        response = ec2_client.terminate_instances(InstanceIds=[instance_id])
        
        # Extract state change details
        state_changes = response.get("TerminatingInstances", [])
        
        return {
            "InstanceId": instance_id,
            "StateChanges": state_changes,
            "Action": "terminate"
        }
    except Exception as e:
        logger.error(f"Error terminating EC2 instance: {str(e)}")
        raise

def get_instance_state(ec2_client, instance_id: str) -> Dict[str, Any]:
    """
    Get the current state of an EC2 instance.
    
    Args:
        ec2_client: Boto3 EC2 client
        instance_id: ID of the instance
        
    Returns:
        Dictionary containing the instance state
    """
    logger.info(f"Getting state of EC2 instance: {instance_id}")
    
    try:
        response = ec2_client.describe_instances(InstanceIds=[instance_id])
        
        # Extract instance details
        reservations = response.get("Reservations", [])
        if not reservations:
            return {"Error": "Instance not found"}
        
        instances = reservations[0].get("Instances", [])
        if not instances:
            return {"Error": "Instance not found"}
        
        instance = instances[0]
        state = instance.get("State", {})
        
        return {
            "InstanceId": instance_id,
            "State": state.get("Name"),
            "StateCode": state.get("Code")
        }
    except Exception as e:
        logger.error(f"Error getting EC2 instance state: {str(e)}")
        raise

def find_instance_by_name(ec2_client, instance_name: str) -> Optional[str]:
    """
    Find an EC2 instance by name tag.
    
    Args:
        ec2_client: Boto3 EC2 client
        instance_name: Name of the instance to find
        
    Returns:
        Instance ID if found, None otherwise
    """
    logger.info(f"Finding EC2 instance by name: {instance_name}")
    
    try:
        response = ec2_client.describe_instances(
            Filters=[
                {
                    "Name": "tag:Name",
                    "Values": [instance_name]
                },
                {
                    "Name": "instance-state-name",
                    "Values": ["pending", "running", "stopping", "stopped"]
                }
            ]
        )
        
        # Extract instance details
        reservations = response.get("Reservations", [])
        if not reservations:
            return None
        
        instances = reservations[0].get("Instances", [])
        if not instances:
            return None
        
        return instances[0].get("InstanceId")
    except Exception as e:
        logger.error(f"Error finding EC2 instance by name: {str(e)}")
        return None
