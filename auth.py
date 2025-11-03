"""Authentication utilities for Azure Sentinel."""

import logging
from azure.identity import DefaultAzureCredential, ClientSecretCredential
from azure.core.credentials import TokenCredential
from config import SentinelConfig

logger = logging.getLogger(__name__)


def get_azure_credential(config: SentinelConfig) -> TokenCredential:
    """Get Azure credential for authentication.
    
    Uses ClientSecretCredential if client credentials are provided,
    otherwise falls back to DefaultAzureCredential.
    
    Args:
        config: Sentinel configuration object.
        
    Returns:
        TokenCredential: Azure credential object for authentication.
    """
    if all([config.tenant_id, config.client_id, config.client_secret]):
        logger.info("Using ClientSecretCredential for authentication")
        return ClientSecretCredential(
            tenant_id=config.tenant_id,
            client_id=config.client_id,
            client_secret=config.client_secret
        )
    else:
        logger.info("Using DefaultAzureCredential for authentication")
        return DefaultAzureCredential()
