"""Configuration management for Sentinel Audit and Update Tool."""

import os
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


@dataclass
class SentinelConfig:
    """Configuration for Microsoft Sentinel workspace."""
    
    subscription_id: str
    resource_group: str
    workspace_name: str
    tenant_id: Optional[str] = None
    client_id: Optional[str] = None
    client_secret: Optional[str] = None
    
    @classmethod
    def from_env(cls) -> 'SentinelConfig':
        """Create configuration from environment variables.
        
        Returns:
            SentinelConfig: Configuration object populated from environment variables.
            
        Raises:
            ValueError: If required environment variables are missing.
        """
        subscription_id = os.getenv('AZURE_SUBSCRIPTION_ID')
        resource_group = os.getenv('RESOURCE_GROUP_NAME')
        workspace_name = os.getenv('WORKSPACE_NAME')
        
        if not all([subscription_id, resource_group, workspace_name]):
            raise ValueError(
                "Missing required environment variables. "
                "Please set AZURE_SUBSCRIPTION_ID, RESOURCE_GROUP_NAME, and WORKSPACE_NAME."
            )
        
        return cls(
            subscription_id=subscription_id,
            resource_group=resource_group,
            workspace_name=workspace_name,
            tenant_id=os.getenv('AZURE_TENANT_ID'),
            client_id=os.getenv('AZURE_CLIENT_ID'),
            client_secret=os.getenv('AZURE_CLIENT_SECRET')
        )
    
    def validate(self) -> bool:
        """Validate that all required fields are present.
        
        Returns:
            bool: True if configuration is valid.
        """
        return all([
            self.subscription_id,
            self.resource_group,
            self.workspace_name
        ])
