"""Module for auditing Microsoft Sentinel data connectors."""

import logging
from typing import List, Dict, Any
from azure.mgmt.securityinsight import SecurityInsights
from azure.core.credentials import TokenCredential
from config import SentinelConfig

logger = logging.getLogger(__name__)


class DataConnectorAuditor:
    """Auditor for Microsoft Sentinel data connectors."""
    
    def __init__(self, credential: TokenCredential, config: SentinelConfig):
        """Initialize the data connector auditor.
        
        Args:
            credential: Azure credential for authentication.
            config: Sentinel configuration.
        """
        self.client = SecurityInsights(credential, config.subscription_id)
        self.config = config
    
    def list_data_connectors(self) -> List[Dict[str, Any]]:
        """List all data connectors in the Sentinel workspace.
        
        Returns:
            List of data connector details.
        """
        try:
            connectors = []
            connector_list = self.client.data_connectors.list(
                resource_group_name=self.config.resource_group,
                workspace_name=self.config.workspace_name
            )
            
            for connector in connector_list:
                connectors.append({
                    'id': connector.id,
                    'name': connector.name,
                    'type': connector.type,
                    'kind': connector.kind if hasattr(connector, 'kind') else 'Unknown',
                    'etag': connector.etag if hasattr(connector, 'etag') else None
                })
            
            logger.info(f"Found {len(connectors)} data connectors")
            return connectors
            
        except Exception as e:
            logger.error(f"Error listing data connectors: {str(e)}")
            raise
    
    def check_connector_updates(self, connector_id: str) -> Dict[str, Any]:
        """Check if updates are available for a specific data connector.
        
        Args:
            connector_id: The ID of the data connector.
            
        Returns:
            Dictionary containing update information.
        """
        # Note: This is a placeholder. The actual implementation would need to
        # query the Sentinel content hub or solution gallery to check for updates.
        logger.info(f"Checking updates for connector: {connector_id}")
        
        return {
            'connector_id': connector_id,
            'update_available': False,
            'current_version': 'Unknown',
            'latest_version': 'Unknown',
            'message': 'Update check functionality to be implemented with Content Hub API'
        }
    
    def get_connector_details(self, connector_name: str) -> Dict[str, Any]:
        """Get detailed information about a specific data connector.
        
        Args:
            connector_name: Name of the data connector.
            
        Returns:
            Detailed connector information.
        """
        try:
            connector = self.client.data_connectors.get(
                resource_group_name=self.config.resource_group,
                workspace_name=self.config.workspace_name,
                data_connector_id=connector_name
            )
            
            return {
                'id': connector.id,
                'name': connector.name,
                'type': connector.type,
                'kind': connector.kind if hasattr(connector, 'kind') else 'Unknown',
                'properties': connector.additional_properties if hasattr(connector, 'additional_properties') else {}
            }
            
        except Exception as e:
            logger.error(f"Error getting connector details: {str(e)}")
            raise
